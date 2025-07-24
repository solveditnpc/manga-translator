import time
import logging
from traceback import format_exc
from selenium.webdriver.common.by import By
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
        self.content = ""
        self._initial_setup_done = False

        if to_lan.lower() not in DEEPL_TARGET_LANGUAGES:
            raise ValueError(f"Invalid target language: {to_lan}")
        if from_lan.lower() != 'auto' and from_lan.lower() not in DEEPL_SOURCE_LANGUAGES:
            raise ValueError(f"Invalid source language: {from_lan}")

        self.to_lan = to_lan.lower()
        self.from_lan = from_lan.lower()
        self.url = "https://www.deepl.com/translator"

    def _initial_setup(self):
        """Performs one-time setup like navigation and cookie acceptance."""
        if self._initial_setup_done:
            return
        
        self.logger.info(f"Navigating to {self.url}")
        self.browser.get(self.url)

        try:
            accept_button = WebDriverWait(self.browser, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="cookie-banner-strict-accept-all"]')))
            accept_button.click()
            self.logger.info("Accepted DeepL cookies")
        except TimeoutException:
            self.logger.info("Cookie banner not found or already accepted")

        if self.from_lan != 'auto':
            self._select_language('source', self.from_lan)
        self._select_language('target', self.to_lan)
        self._initial_setup_done = True


    def deepl(self, content):
        '''Translates a single block of content.'''
        try:
            self._initial_setup()

            self.logger.info("Finding input text area...")
            input_area = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="textbox"][aria-labelledby="translation-source-heading"]')))
            input_area.send_keys(content)
            self.logger.info("Text sent")

            self.logger.info("Waiting for a valid and final translation...")
            output_selector = 'd-textarea[data-testid="translator-target-input"]'
            WebDriverWait(self.browser, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, output_selector)))
            
            time.sleep(1)

            translated_text = self.browser.find_element(By.CSS_SELECTOR, output_selector).text
            self.logger.info(f"Translated text: {translated_text[:100]}...")
            self.content = translated_text
            return self.content
        except Exception as e:
            self.logger.error(f"Translation failed for content: {content[:50]}...")
            self.logger.error(format_exc())
            return "failed"

    def clear_text_areas(self):
        """Clears the input text area to prepare for the next translation."""
        try:
            self.logger.info("Clearing text areas...")
            input_area = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="textbox"][aria-labelledby="translation-source-heading"]')))
        
            input_area.send_keys(Keys.CONTROL + 'a')
            input_area.send_keys(Keys.DELETE)
            self.logger.info("Text areas cleared.")
            time.sleep(1)
        except Exception as e:
            self.logger.error("Failed to clear text areas.")
            self.logger.error(format_exc())

    def _select_language(self, lang_direction, lang_code):
        """Selects the source or target language on DeepL."""
        try:
            self.logger.info(f"Setting {lang_direction} language to {lang_code}")
            lang_button_selector = f'button[data-testid="translator-{lang_direction}-lang-btn"]'
            lang_button = WebDriverWait(self.browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, lang_button_selector)))
            lang_button.click()

            lang_search_input = WebDriverWait(self.browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[placeholder="Search languages"]')))
            
            language_name = DEEPL_SOURCE_LANGUAGES[lang_code] if lang_direction == 'source' else DEEPL_TARGET_LANGUAGES[lang_code]
            lang_search_input.send_keys(language_name)
            self.logger.info(f"Typed '{language_name}' into language search.")
            time.sleep(0.5)

            lang_search_input.send_keys(Keys.RETURN)
            self.logger.info(f"{lang_direction.capitalize()} language set to {language_name}.")
            time.sleep(1)
        except Exception as e:
            self.logger.error(f"Failed to set {lang_direction} language to {lang_code}: {e}")
            raise