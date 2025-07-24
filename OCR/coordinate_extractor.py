from pathlib import Path
import cv2
from paddleocr import PaddleOCR
from pdf2image import convert_from_path, pdfinfo_from_path
from pdf2image.exceptions import PDFInfoNotInstalledError
from docx2pdf import convert
import json


SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR.parent / "config.json"
with open(CONFIG_PATH, "r") as cf:
    CONFIG = json.load(cf)

INPUT_DIR = SCRIPT_DIR.parent / "input"
OUTPUT_DIR = SCRIPT_DIR.parent / "output"

OUTPUT_DIR.mkdir(exist_ok=True)

_ocr_param_keys = [
    "lang",                               
    #"text_det_limit_side_len",           #to get max performance , disable this feature
    "use_doc_orientation_classify",      #textline orientation is enough for calculation of line angles, set to false 
    "use_doc_unwarping",                  #add padding to the image if you want to enable this feature,it causes the image to twist along a tensor and lead to less accurate predictions , set to false
    "use_textline_orientation",
]
ocr_kwargs = {k: CONFIG[k] for k in _ocr_param_keys if k in CONFIG}
ocr = PaddleOCR(**ocr_kwargs)

def run_ocr_and_save_results(image_to_process, output_dir, basename=None):
    """Runs OCR on a given image, handles errors, and saves the results."""
    try:
        print("    - Running OCR...")
        result = ocr.predict(image_to_process)

        if result and result[0]:
            # Save JSON results with a name based on the input file/page
            json_filename = f"{basename}.json" if basename else "ocr_result.json"
            json_output_path = output_dir / json_filename
            result[0].save_to_json(str(json_output_path))
            print(f"    - Saved JSON results to {json_output_path}")

            # 1. Get list of files before saving images
            files_before = set(p.name for p in output_dir.glob('*'))

            # 2. Let PaddleOCR save the images with its default random names
            result[0].save_to_img(str(output_dir))
            print(f"    - Saved visualization(s) to {output_dir}")

            # 3. Find the newly created image files
            files_after = set(p.name for p in output_dir.glob('*'))
            new_files = files_after - files_before

            # 4. Rename the new files if a basename is provided
            if basename:
                new_images = sorted([f for f in new_files if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
                for i, filename in enumerate(new_images):
                    old_path = output_dir / filename
                    new_name = f"{basename}_visualization_{i + 1}{old_path.suffix}"
                    new_path = output_dir / new_name
                    old_path.rename(new_path)
                    print(f"    - Renamed {filename} to {new_name}")
        else:
            print("    - No text found in image.")
    except Exception as e:
        print(f"    - An error occurred during OCR processing: {e}")

def process_image(image_path):
    """Processes a single image file (PNG, JPG, JPEG)."""
    print(f"Processing {image_path.name}...")
    output_dir = OUTPUT_DIR / image_path.stem
    output_dir.mkdir(exist_ok=True)

    cv_image = cv2.imread(str(image_path))
    if cv_image is None:
        print(f"Error: Could not read image {image_path.name}")
        return

    run_ocr_and_save_results(cv_image, output_dir, basename=image_path.stem)

def update_config_for_pdf(pdf_name, page_count):
    """Updates the config.json file with active_translation_path and folder_subdirectories."""
    try:
        with open(CONFIG_PATH, "r+") as f:
            config_data = json.load(f)
            config_data["active_translation_path"] = f"/{pdf_name}"
            config_data["folder_subdirectories"] = str(page_count)
            f.seek(0)
            json.dump(config_data, f, indent=4)
            f.truncate()
        print(f"Updated config.json: active_translation_path='/{pdf_name}', folder_subdirectories='{page_count}'")
    except Exception as e:
        print(f"Error updating config.json: {e}")

def process_pdf(pdf_path):
    """Converts a PDF to images, saves them, resizes if necessary, and runs OCR on each page."""
    print(f"Processing {pdf_path.name}...")
    pdf_output_dir = OUTPUT_DIR / pdf_path.stem
    pdf_output_dir.mkdir(exist_ok=True)

    try:
        # Get total number of pages without loading the whole file
        pdf_info = pdfinfo_from_path(str(pdf_path))
        page_count = pdf_info['Pages']
    except PDFInfoNotInstalledError:
        print("Error: Poppler is not installed or not in PATH. Please install Poppler and try again.")
        return

    update_config_for_pdf(pdf_path.stem, page_count)

    # Process one page at a time to save memory
    for page_num in range(1, page_count + 1):
        print(f"  - Processing page {page_num}/{page_count}...")

        # Create a directory for the page's results
        page_result_dir = pdf_output_dir / f"page_{page_num}_results"
        page_result_dir.mkdir(exist_ok=True)

        # Convert and save only the current page
        image_path = page_result_dir / f"page_{page_num}.png"

        # Only convert if the image doesn't already exist
        if not image_path.exists():
            print("    - Converting page to image (300 DPI)...")
            try:
                page_image = convert_from_path(
                    str(pdf_path),
                    dpi=300,
                    first_page=page_num,
                    last_page=page_num
                )[0]
                page_image.save(image_path, "PNG")
                print(f"    - Saved page image to {image_path}")
            except Exception as e:
                print(f"    - Error converting page {page_num}: {e}")
                continue
        else:
            print(f"    - Image already exists: {image_path}")

        # Check if OCR results already exist
        json_output_path = page_result_dir / f"page_{page_num}.json"
        if json_output_path.exists():
            print(f"    - OCR results already exist: {json_output_path}")
            continue

        # Run OCR on the saved image
        cv_image = cv2.imread(str(image_path))
        if cv_image is None:
            print(f"    - Error: Could not read image {image_path}")
            continue

        run_ocr_and_save_results(cv_image, page_result_dir, basename=f"page_{page_num}")


def process_docx(docx_path):
    """Converts a DOCX file to PDF and then processes it."""
    print(f"Converting {docx_path.name} to PDF...")
    pdf_path = OUTPUT_DIR / f"{docx_path.stem}.pdf"
    try:
        convert(str(docx_path), str(pdf_path))
        print(f"Successfully converted to {pdf_path.name}")
        process_pdf(pdf_path)
    except Exception as e:
        print(f"Error converting {docx_path.name} to PDF: {e}")
        print("Please ensure you have LibreOffice or Microsoft Office installed.")

def main():
    """Finds and processes all supported files in the input directory."""
    print("Starting file processing...")
    supported_extensions = ["*.pdf", "*.png", "*.jpg", "*.jpeg", "*.docx"]
    files_to_process = []
    for ext in supported_extensions:
        files_to_process.extend(INPUT_DIR.glob(ext))

    if not files_to_process:
        print(f"No supported files found in '{INPUT_DIR}' directory.")
        return

    for file_path in files_to_process:
        ext = file_path.suffix.lower()
        if ext == ".pdf":
            process_pdf(file_path)
        elif ext in [".png", ".jpg", ".jpeg"]:
            process_image(file_path)
        elif ext == ".docx":
            process_docx(file_path)
    
    print("Processing complete.")

if __name__ == "__main__":
    main()