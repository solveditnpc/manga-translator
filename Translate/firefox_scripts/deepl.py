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
from selenium.webdriver.common.keys import Keys

DEEPL_SOURCE_LANGUAGES = {
    "ar": "Arabic", "bg": "Bulgarian", "zh": "Chinese", "cs": "Czech", "da": "Danish",
    "nl": "Dutch", "en": "English", "et": "Estonian", "fi": "Finnish", "fr": "French",
    "de": "German", "el": "Greek", "he": "Hebrew", "hu": "Hungarian", "id": "Indonesian",
    "it": "Italian", "ja": "Japanese", "ko": "Korean", "lv": "Latvian", "lt": "Lithuanian",
    "nb": "Norwegian (bokmål)", "pl": "Polish", "pt": "Portuguese", "ro": "Romanian",
    "ru": "Russian", "sk": "Slovak", "sl": "Slovenian", "es": "Spanish", "sv": "Swedish",
    "tr": "Turkish", "uk": "Ukrainian", "vi": "Vietnamese"
}

DEEPL_TARGET_LANGUAGES = {
    "ar": "Arabic", "bg": "Bulgarian", "zh-hans": "Chinese (simplified)", "zh-hant": "Chinese (traditional)",
    "cs": "Czech", "da": "Danish", "nl": "Dutch", "en-us": "English (American)", "en-gb": "English (British)",
    "et": "Estonian", "fi": "Finnish", "fr": "French", "de": "German", "el": "Greek", "he": "Hebrew",
    "hu": "Hungarian", "id": "Indonesian", "it": "Italian", "ja": "Japanese", "ko": "Korean",
    "lv": "Latvian", "lt": "Lithuanian", "nb": "Norwegian (bokmål)", "pl": "Polish",
    "pt-br": "Portuguese (Brazilian)", "pt-pt": "Portuguese (Portugal)", "ro": "Romanian",
    "ru": "Russian", "sk": "Slovak", "sl": "Slovenian", "es": "Spanish", "es-419": "Spanish (Latin American)",
    "sv": "Swedish", "tr": "Turkish", "uk": "Ukrainian", "vi": "Vietnamese"
}

class DeepLTranslator:
    def __init__(self, browser, logger, to_lan="en-us", from_lan="auto"):
        self.browser = browser
        self.logger = logger
        self.content = ""  # store the translations for future database implementation

        if to_lan.lower() not in DEEPL_TARGET_LANGUAGES:
            raise ValueError(f"Invalid target language: {to_lan}")
        if from_lan.lower() != 'auto' and from_lan.lower() not in DEEPL_SOURCE_LANGUAGES:
            raise ValueError(f"Invalid source language: {from_lan}")

        self.to_lan = to_lan.lower()
        self.from_lan = from_lan.lower()
        self.url = "https://www.deepl.com/translator"

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

            #Language Selection
            if self.from_lan != 'auto':
                self._select_language('source', self.from_lan)
            self._select_language('target', self.to_lan)

            self.logger.info("finding input text area..")
            #deepl specific div in input area
            input_area = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="textbox"][aria-labelledby="translation-source-heading"]')))
            input_area.send_keys(content)
            self.logger.info("Text sent")

            self.logger.info("waiting for a valid and final translation ")

            # Wait for the output element to contain the translation
            output_selector = 'd-textarea[data-testid="translator-target-input"]'
            WebDriverWait(self.browser, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, output_selector)))
            
            # Add a small delay for the text to be fully rendered
            time.sleep(1)

            # Extract the translated text
            translated_text = self.browser.find_element(By.CSS_SELECTOR, output_selector).text
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

    def _select_language(self, lang_direction, lang_code):
        """Selects the source or target language on DeepL."""
        try:
            self.logger.info(f"Setting {lang_direction} language to {lang_code}")
            # 1. Click the language dropdown button to open the menu.
            lang_button_selector = f'button[data-testid="translator-{lang_direction}-lang-btn"]'
            lang_button = WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, lang_button_selector))
            )
            lang_button.click()

            # 2. Type the language name into the search input.
            lang_search_input = WebDriverWait(self.browser, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[placeholder="Search languages"]'))
            )
            
            # Determine which dictionary to use for the language name
            if lang_direction == 'source':
                language_name = DEEPL_SOURCE_LANGUAGES[lang_code]
            else:
                language_name = DEEPL_TARGET_LANGUAGES[lang_code]

            lang_search_input.send_keys(language_name)
            self.logger.info(f"Typed '{language_name}' into language search.")
            time.sleep(0.5)  # Pause for UI to update after typing.

            # 3. Press Enter to select the language.
            lang_search_input.send_keys(Keys.RETURN)
            self.logger.info(f"{lang_direction.capitalize()} language set to {language_name}.")
            time.sleep(1)
        except Exception as e:
            self.logger.error(f"Failed to set {lang_direction} language to {lang_code}: {e}")
            raise

def load_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, '..', '..', 'config.json')
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config

if __name__ == '__main__':
    config = load_config()
    GECKODRIVER_PATH = config.get('GECKODRIVER_PATH')
    FIREFOX_PROFILE_PATH = config.get('FIREFOX_PROFILE_PATH')
    to_lan = config.get('to_lan', 'en-us')
    from_lan = config.get('from_lan', 'auto')

    logging.basicConfig(level = logging.INFO,format= '%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

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
        service = Service(executable_path=GECKODRIVER_PATH)

        try:
            logger.info("initializing firefox driver")
            driver = webdriver.Firefox(service =service,options = options)
            logger.info("driver initialized")

            translator = DeepLTranslator(driver, logger, to_lan=to_lan, from_lan=from_lan)
            result = translator.deepl(content_to_translate)

            with open('result.txt', "w", encoding="utf-8") as f:
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