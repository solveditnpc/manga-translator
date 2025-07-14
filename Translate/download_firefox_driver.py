import os 
import platform 
import requests
import zipfile 
import tarfile 
import logging 

#logging
logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')

#platform specific config
OS_SYSTEM = platform.system()
DRIVER_DIR = "./config/tools"

if OS_SYSTEM == "Windows":
    DRIVER_EXECUTABLE = "geckodriver.exe"
else: #linux/mac
    DRIVER_EXECUTABLE = "geckodriver"

DRIVER_PATH = os.path.join(DRIVER_DIR,DRIVER_EXECUTABLE)

def get_latest_driver_info():
    """
    Fetches the latest driver from the github api 
    return the download url and the filename for the current os 
    """
    logging.info("fetchign the latest driver")
    api_url = "https://api.github.com/repos/mozilla/geckodriver/releases/latest"
    try: 
        response = requests.get(api_url,timeout=15)
        response.raise_for_status()
        release_data = response.json()
        assets = release_data.get("assets",[])

        #correct asset filename pattern 
        if OS_SYSTEM == "Windows":
            #assume 64 bti 
            search_pattern = "win64.zip"
        elif OS_SYSTEM == "Linux":
            #assume 64 bit 
            search_pattern = "linux64.tar.gz"
        elif OS_SYSTEM == "Darwin": 
            search_pattern = "macos.tar.gz"
        else:
            logging.error(f"unsupported os : {OS_SYSTEM}")
            return None,None
        
        for asset in assets :
            asset_name = asset.get("name","")
            if search_pattern in asset_name:
                logging.info(f"found driver package for {OS_SYSTEM}: {asset_name}")
                return asset.get("browser_download_url"), asset_name
            
        logging.error(f"could not find a suitable driver ")
        return None, None 
    except requests.RequestException as e:
        logging.error(f"failed to connect to github api: {e}")
        return None, None 
def download_and_extract_driver(url,filename):
    """
    downloads and extracts the geckodriver
    """
    if not url or not filename:
        return False 
    archive_path = os.path.join(DRIVER_DIR,filename)
    try:
        #download driver package 
        logging.info(f"downlaoding form: {url}")
        response = requests.get(url,stream=True,timeout=60)
        response.raise_for_status()

        if not os.path.exists(DRIVER_DIR):
            os.makedris(DRIVER_DIR)
            logging.info(f"created driectory: {DRIVER_DIR}")
        with open(archive_path,"wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logging.info(f"success: {filename}")

        #extract executable
        logging.info(f"extracting:{filename}")
        if filename.endwith("zip"):
            with zipfile.ZipFile(archive_path,"r") as zip_ref:
                #extract only the executable to the taret dir
                zip_ref.extract(DRIVER_EXECUTABLE,DRIVER_DIR)
        elif filename.endswith(".tar.gz"):
            with tarfile.open(archive_path,"r:gz") as tar:
                #only extrat the executable to the target path 
                for member in tar.getmembers():
                    if os.path.basename(member.name)== DRIVER_EXECUTABLE:
                        member.name = os.path.basename(member.name)
                        tar.extract(member,DRIVER_DIR)
                        break
        logging.info(f"successfully extracted : {DRIVER_EXECUTABLE} to {DRIVER_PATH}")

        #set permission on linux/mac
        if OS_SYSTEM != "Windows":
            os.chmod(DRIVER_PATH,0o755) # Owner- read,write,execute,Group- read,execute ,Others- read,execute
            logging.info(f"set executable premission for {DRIVER_PATH}")

        return True
    except Exception as e:
        logging.error(f"error while downloading or extracting: {e}")
        return False
    finally:
        #clear the downloaded archive 
        if os.path.exists(archive_path):
            os.remove(archive_path)
            logging.info(f"removed temp archive: {archive_path}")

if __name__ == "__main__":
    logging.info("starting driver update")
    download_url,driver_filename = get_latest_driver_info()

    if download_url and driver_filename:
        success = download_and_extract_driver(download_url,driver_filename)
        if success:
            logging.info("update process completed successfully")
            logging.info(f"driver is located at :{os.path.abspath(DRIVER_PATH)}")
        else:
            logging.error("update process failed")
    else:
        logging.error("could not retrieve driver info , aborting")