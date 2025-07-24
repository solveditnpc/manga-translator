import json
import os
import logging
import glob
from traceback import format_exc
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from deepl import DeepLTranslator

def load_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, '..', '..', 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)

if __name__ == '__main__':
    config = load_config()
    GECKODRIVER_PATH = config.get('GECKODRIVER_PATH')
    FIREFOX_PROFILE_PATH = config.get('FIREFOX_PROFILE_PATH')
    to_lan = config.get('to_lan', 'en-us')
    from_lan = config.get('from_lan', 'auto')
    active_translation_path = config.get('active_translation_path')
    folder_subdirectories = int(config.get('folder_subdirectories', 0))

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    if not active_translation_path:
        logger.error("'active_translation_path' not set in config.json. Exiting.")
        exit()

    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'output'))
    search_path = os.path.join(base_path, active_translation_path.strip('/'))
    files_to_translate = []
    for root, _, files in os.walk(search_path):
        for file in files:
            if file.endswith('.json'):
                files_to_translate.append(os.path.join(root, file))
    files_to_translate.sort()

    if not files_to_translate:
        logger.warning(f"No '.json' files found in {search_path}.")
    else:
        driver = None
        options = Options()
        options.add_argument("-profile")
        options.add_argument(FIREFOX_PROFILE_PATH)
        service = Service(executable_path=GECKODRIVER_PATH)

        try:
            logger.info("Initializing Firefox driver for the session...")
            driver = webdriver.Firefox(service=service, options=options)
            logger.info("Driver initialized.")

            translator = DeepLTranslator(driver, logger, to_lan=to_lan, from_lan=from_lan)
            translated_files_count = 0

            for filepath in files_to_translate:
                if folder_subdirectories > 0 and translated_files_count >= folder_subdirectories:
                    logger.info(f"Processed {translated_files_count} files, reaching the limit of {folder_subdirectories}.")
                    break

                logger.info(f"--- Processing file: {filepath} ---")
                try:
                    with open(filepath, "r", encoding='utf-8') as f:
                        data = json.load(f)
                    
                    texts_to_translate = data.get("rec_texts")
                    if not texts_to_translate or not any(t.strip() for t in texts_to_translate):
                        logger.warning(f"File {filepath} has no text in 'rec_texts' or is empty. Skipping.")
                        continue

                    separator = "\n<br>\n"
                    content_to_translate = separator.join(texts_to_translate)
                    
                    logger.info(f"Content to translate: {content_to_translate[:150]}...")
                    result = translator.deepl(content_to_translate)

                    if result.lower() in ["failed", "timed out"]:
                        logger.error(f"Translation failed for {filepath}. Skipping update.")
                        continue

                    translated_texts = result.split(separator)
                    data["rec_texts"] = translated_texts

                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
                    logger.info(f"Result saved to {filepath}")
                    translated_files_count += 1

                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON in {filepath}. Skipping.")
                except Exception as e:
                    logger.error(f"An error occurred while processing {filepath}: {e}")
                finally:
                    if driver:
                        translator.clear_text_areas()

        except Exception as e:
            logger.error(f"A critical error occurred: {e}")
            logger.error(format_exc())
        finally:
            if driver:
                logger.info("All files processed. Closing the browser.")
                driver.quit()
            logger.info("Script complete.")