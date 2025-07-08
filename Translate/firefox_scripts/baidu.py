import time
import logging
from traceback import format_exc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class BaiduTranslator:
    def __init__(self, browser, logger):
        self.browser = browser
        self.logger = logger
        self.content = ""
        self.url = "https://fanyi.baidu.com/mtpe-individual/multimodal#/auto/en"

    def baidu(self, content):
        """
        Translates the given content using Caiyun Translator.
        """
        try:
            self.browser.set_page_load_timeout(180)
            self.logger.info(f"Navigating to {self.url}")
            self.browser.get(self.url)

            self.logger.info("Finding input text area...")
            input_area = WebDriverWait(self.browser, 50).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='textbox']"))
            )
            self.logger.info("Input area found. Clearing and sending text...")
            self.browser.execute_script('arguments[0].innerHTML = ""',input_area)
            input_area.send_keys(content)
            self.logger.info("Text sent successfully.")

            self.logger.info("Waiting for a valid and final translation...")

            def translation_is_complete(driver):
                """Check if the translation is complete and not a transient error."""
                try:
                    output_container = driver.find_element(By.CSS_SELECTOR, "div.output-content")
                    output_text = output_container.text.strip()
                    if output_text and "..." not in output_text and "翻译中..." not in output_text:
                        return output_text
                    return False
                except NoSuchElementException:
                    return False

            translated_text = WebDriverWait(self.browser, 25).until(translation_is_complete)
            
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
            content_to_translate = f.read().strip()
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
            driver = webdriver.Firefox(service =service,options = options)
            logger.info("driver initialized")

            translator = BaiduTranslator(driver,logger)
            result = translator.baidu(content_to_translate)

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