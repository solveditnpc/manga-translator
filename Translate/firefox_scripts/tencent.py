import time 
import logging 
from traceback import format_exc
from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class TencentTranslator:
    def __init__(self, browser, logger):
        self.browser = browser
        self.logger = logger 
        self.content = ""   # store the translations for future database implementation
        self.url = "https://fanyi.qq.com/"

    def tencent(self,content):
        '''
        This is designed to be a seperate file in the future, so when the webscraper fails , only this function needs to be changed  
        '''
        try: 
            self.logger.info(f"Navigating to {self.url}")
            self.browser.get(self.url)

            self.logger.info("finding input text area....")
            input_area = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME,"tea-textarea")))
            self.logger.info("input area found.sending text")
            input_area.clear()
            input_area.send_keys(content)
            self.logger.info("text sent successfully.")

            self.logger.info("waiting for a valid and final translation ")

            def translation_is_complete(driver):
                try:
                    output_element = driver.find_element(By.CLASS_NAME, "target-text-box")
                    output_text = (output_element.text or "").strip().lower()

                    #still empty, not complete 
                    if not output_text or "..." in output_text or output_text == "译文":
                        return False
                    #contains a error like 503
                    if any(err in output_text for err in ["failed", "error", "503"]):
                        return False
                    #trnslation complete if 
                    return True
                except:
                    return False
            
            #check with a time out 
            WebDriverWait(self.browser, 15).until(translation_is_complete)
            translated_text = self.browser.find_element(By.CLASS_NAME,"target-text-box").text
            self.logger.info(f"Translated text:{translated_text[:100]}...")
            self.content = translated_text
            return self.content
        except TimeoutException:
            self.logger.error(f"bing translation timedout for content: {content[:50]}...")
            return "failed"
        except Exception as e:
            self.logger.error(f"Bing translation timed out for cotent: {content[:50]}...")
            self.logger.error(format_exc())
            return "failed"
        
if __name__ == '__main__':
    # broswer config
    GECKODRIVER_PATH = ''
    FIREFOX_PROFILE_PATH = ''

    #setup basic logger for testing 
    logging.basicConfig(level = logging.INFO,format= '%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    # read content
    try:
        with open('content.txt', "r",encoding = 'utf-8') as f:
            content_to_translate = f.read()
        logger.info(f"content to translate: {content_to_translate[:100]}...")
    except FileNotFoundError:
        logger.error("Error: content.txt not found")
        content_to_translate = ""

    # initialise webdriver and performing translation
    driver = None
    if content_to_translate:
        options = Options()
        options.add_argument("-profile")
        options.add_argument(FIREFOX_PROFILE_PATH)
        Service = Service(executable_path = GECKODRIVER_PATH)

        try:
            logger.info("initializing firefox driver")
            driver = webdriver.Firefox(service = service,options = options)
            logger.info("driver initialized")

            translator = TencentTranslator(driver,logger)
            result = translator.tencent(content_to_translate)

            with open('result.txt,"w",encoding = "utf-8') as f:
                f.write(result)
            logger.info("result saved to result.txt")
        except Exception as e:
            logger.error(f"an unexpected error has occurred: {e}")
            logger.error(format_exc())

        finally:
            if driver:
                logger.info("closing the browser")
                driver.quit()
            logger.info("script complete")
    else:
        logger.info("no content to translate, script complete")