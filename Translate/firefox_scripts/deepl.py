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

class DeepLTranslator:
    def __init__(self, browser, logger):
        self.browser = browser
        self.logger = logger 
        self.content = ""   # store the translations for future database implementation
        self.url = "https://www.deepl.com/translator#auto/en"

    def deepl(self,content):
        '''
        This is designed to be a seperate file in the future, so when the webscraper fails , only this function needs to be changed  
        '''
        try: 
            self.logger.info(f"Navigating to {self.url}")
            self.browser.get(self.url)

            #accept cookies
            try:
                accept_button = WebDriverWait(self.browser,5).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'[data-testid="cookie-banner-strict-accept-all"]')))
                accept_button.click()
                self.logger.info("accepted deepl cookies")
            except TimeoutException:
                self.logger.info("cookie banner not found or already accepted")
            self.logger.info("finding input text area..")
            #deepl specific div in input area
            input_area = WebDriverWait(self.browser,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,'div[aria-labelledby="translation-source-heading"]')))
            self.logger.info("text sent")

            self.logger.info("waiting for a valid and final translation ")

            #wait for div to contain *any* text
            WebDriverWait(self.browser,20).until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,'div[aria-labelledby="translation-target-heading"]'),'.'))
            #delay
            time.sleep()

            translated_text = self.browser.find_element(By.css_SELECTOR, 'div[aria-labelledby="translation-target-heading"]').text
            self.logger.info(f"translated text: {translated_text[:100]}...")
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
            driver = webdriver.Firefox(service =service,options = options)
            logger.info("driver initialized")

            translator = DeepLTranslator(driver,logger)
            result = translator.deepl(content_to_translate)

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