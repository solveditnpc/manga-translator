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

LANGUAGES = {
        "af": "Afrikaans", "am": "Amharic", "ar": "Arabic", "as": "Assamese", "az": "Azerbaijani",
        "ba": "Bashkir", "be": "Belarusian", "bg": "Bulgarian", "bho": "Bhojpuri", "bn": "Bangla",
        "bo": "Tibetan", "brx": "Bodo", "bs": "Bosnian", "ca": "Catalan", "cs": "Czech",
        "cy": "Welsh", "da": "Danish", "de": "German", "doi": "Dogri", "dsb": "Lower Sorbian",
        "dv": "Divehi", "el": "Greek", "en": "English", "es": "Spanish", "et": "Estonian",
        "eu": "Basque", "fa": "Persian", "fi": "Finnish", "fil": "Filipino", "fj": "Fijian",
        "fo": "Faroese", "fr": "French", "fr-CA": "French (Canada)", "ga": "Irish",
        "gl": "Galician", "gom": "Konkani", "gu": "Gujarati", "ha": "Hausa", "he": "Hebrew",
        "hi": "Hindi", "hne": "Chhattisgarhi", "hr": "Croatian", "hsb": "Upper Sorbian",
        "ht": "Haitian Creole", "hu": "Hungarian", "hy": "Armenian", "id": "Indonesian",
        "ig": "Igbo", "ikt": "Inuinnaqtun", "is": "Icelandic", "it": "Italian", "iu": "Inuktitut",
        "iu-Latn": "Inuktitut (Latin)", "ja": "Japanese", "ka": "Georgian", "kk": "Kazakh",
        "km": "Khmer", "kmr": "Kurdish (Northern)", "kn": "Kannada", "ko": "Korean", "ks": "Kashmiri",
        "ku": "Kurdish (Central)", "ky": "Kyrgyz", "lb": "Luxembourgish", "ln": "Lingala",
        "lo": "Lao", "lt": "Lithuanian", "lug": "Ganda", "lv": "Latvian",
        "lzh": "Chinese (Literary)", "mai": "Maithili", "mg": "Malagasy", "mi": "Māori",
        "mk": "Macedonian", "ml": "Malayalam", "mn-Cyrl": "Mongolian (Cyrillic)",
        "mn-Mong": "Mongolian (Traditional)", "mni": "Manipuri", "mr": "Marathi", "ms": "Malay",
        "mt": "Maltese", "mww": "Hmong Daw", "my": "Myanmar (Burmese)", "nb": "Norwegian",
        "ne": "Nepali", "nl": "Dutch", "nso": "Sesotho sa Leboa", "nya": "Nyanja", "or": "Odia",
        "otq": "Querétaro Otomi", "pa": "Punjabi", "pl": "Polish", "prs": "Dari", "ps": "Pashto",
        "pt": "Portuguese (Brazil)", "pt-PT": "Portuguese (Portugal)", "ro": "Romanian",
        "ru": "Russian", "run": "Rundi", "rw": "Kinyarwanda", "sd": "Sindhi", "si": "Sinhala",
        "sk": "Slovak", "sl": "Slovenian", "sm": "Samoan", "sn": "Shona", "so": "Somali",
        "sq": "Albanian", "sr-Cyrl": "Serbian (Cyrillic)", "sr-Latn": "Serbian (Latin)",
        "st": "Sesotho", "sv": "Swedish", "sw": "Swahili", "ta": "Tamil", "te": "Telugu",
        "th": "Thai", "ti": "Tigrinya", "tk": "Turkmen", "tlh-Latn": "Klingon (Latin)",
        "tlh-Piqd": "Klingon (pIqaD)", "tn": "Setswana", "to": "Tongan", "tr": "Turkish",
        "tt": "Tatar", "ty": "Tahitian", "ug": "Uyghur", "uk": "Ukrainian", "ur": "Urdu",
        "uz": "Uzbek (Latin)", "vi": "Vietnamese", "xh": "Xhosa", "yo": "Yoruba",
        "yua": "Yucatec Maya", "yue": "Cantonese (Traditional)", "zh-Hans": "Chinese Simplified",
        "zh-Hant": "Chinese Traditional", "zu": "Zulu"
    }

class BingTranslator:
    def __init__(self, browser, logger, to_lan):
        self.browser = browser
        self.logger = logger 
        self.content = ""   # store the translations for future database implementation
        if to_lan not in LANGUAGES:
            raise ValueError(f"Invalid language: {to_lan}")
        self.url = f"https://www.bing.com/translator?to={to_lan}"

    def bing(self,content):
        '''
        This is designed to be a seperate file in the future, so when the webscraper fails , only this function needs to be changed  
        '''
        try: 
            self.logger.info(f"Navigating to {self.url}")
            self.browser.get(self.url)

            self.logger.info("finding input text area....")
            input_area = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.ID,"tta_input_ta")))
            self.logger.info("input area found.sending text")
            input_area.clear()
            input_area.send_keys(content)
            self.logger.info("text sent successfully.")

            self.logger.info("waiting for a valid and final translation ")

            def translation_is_complete(driver):
                output_element = driver.find_element(By.ID, "tta_output_ta")
                output_text = (output_element.text or "").strip().lower()

                #still empty, not complete 
                if not output_text:
                    return False
                #contains placeholders , not complete 
                if "..."in output_text:
                    return False
                #contains a error like 503
                if any(err in output_text for err in ["failed", "error", "503"]):
                    return False
                #trnslation complete if 
                return True
            
            #check with a time out 
            WebDriverWait(self.browser, 15).until(translation_is_complete)
            translated_text = self.browser.find_element(By.ID,"tta_output_ta").text
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
        
def load_config():
    # Construct the path to config.json relative to the script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, '..', '..', 'config.json')
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config

if __name__ == '__main__':
    config = load_config()
    GECKODRIVER_PATH = config.get('GECKODRIVER_PATH')
    FIREFOX_PROFILE_PATH = config.get('FIREFOX_PROFILE_PATH')
    to_lan = config.get('to_lan', 'en')

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
            driver = webdriver.Firefox(service = service,options = options)
            logger.info("driver initialized")

            translator = BingTranslator(driver,logger, to_lan=to_lan)
            result = translator.bing(content_to_translate)

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