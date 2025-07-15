import time
import json
import os
import logging
from traceback import format_exc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class CaiyunTranslator:
    def __init__(self, browser, logger):
        self.browser = browser
        self.logger = logger
        self.content = ""
        self.url = "https://fanyi.caiyunapp.com/"

    def caiyun(self, content):
        """
        Translates the given content using Caiyun Translator.
        """
        try:
            self.logger.info(f"Navigating to {self.url}")
            self.browser.get(self.url)

            self.logger.info("Finding input text area...")
            input_area = WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.ID, "textarea"))
            )
            self.logger.info("Input area found. Clearing and sending text...")
            input_area.clear()
            input_area.send_keys(content)
            self.logger.info("Text sent successfully.")

            self.logger.info("Waiting for a valid and final translation...")

            def translation_is_complete(driver):
                """Check if the translation is complete and not a transient error."""
                try:
                    output_element = driver.find_element(By.ID, "texttarget")
                    output_text = (output_element.text or "").strip().lower()
                    if not output_text or "..." in output_text or "translation in progress" in output_text:
                        return False
                    if any(err in output_text for err in ["failed", "error", "503"]):
                        return False
                    return True
                except:
                    return False

            WebDriverWait(self.browser, 15).until(translation_is_complete)
            translated_text = self.browser.find_element(By.ID, "texttarget").text
            self.logger.info(f"Translated text found: {translated_text[:100]}...")
            self.content = translated_text
            return self.content
        
        except TimeoutException:
            self.logger.error(f"Youdao translation timed out for content: {content[:50]}...")
            return "failed"
        except Exception as e:
            self.logger.error(f"An error occurred during Youdao translation: {e}")
            self.logger.error(format_exc())
            return "failed"

def load_config():
    # Construct the path to config.json 
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, '..', '..', 'config.json')
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config

if __name__ == '__main__':
    config = load_config()
    GECKODRIVER_PATH = config.get('GECKODRIVER_PATH')
    FIREFOX_PROFILE_PATH = config.get('FIREFOX_PROFILE_PATH')

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
        service = Service(executable_path = GECKODRIVER_PATH)

        try:
            logger.info("initializing firefox driver")
            driver = webdriver.Firefox(service =service,options = options)
            logger.info("driver initialized")

            translator = CaiyunTranslator(driver,logger)
            result = translator.caiyun(content_to_translate)

            with open('result.txt',"w",encoding = "utf-8") as f:
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