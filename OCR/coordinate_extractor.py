import os
from pathlib import Path
import cv2
import numpy as np
from paddleocr import PaddleOCR
from pdf2image import convert_from_path
from pdf2image.exceptions import PDFInfoNotInstalledError
from docx import Document
from docx2pdf import convert

INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")

# Define max side limit from the warning message
MAX_SIDE_LIMIT = 4000

# Create output directory if it doesn't exist
OUTPUT_DIR.mkdir(exist_ok=True)

# Initialize PaddleOCR
ocr = PaddleOCR(
    use_doc_orientation_classify=False, 
    use_doc_unwarping=False, 
    use_textline_orientation=False
)

def process_image(image_path):
    """Processes a single image file (PNG, JPG, JPEG)."""
    print(f"Processing {image_path.name}...")
    output_dir = OUTPUT_DIR / image_path.stem
    output_dir.mkdir(exist_ok=True)

    cv_image = cv2.imread(str(image_path))
    if cv_image is None:
        print(f"Error: Could not read image {image_path.name}")
        return

    h, w, _ = cv_image.shape
    image_to_process = cv_image

    if max(h, w) > MAX_SIDE_LIMIT:
        print(f"  - Resizing image from {w}x{h} to fit within {MAX_SIDE_LIMIT}px limit.")
        if w > h:
            new_w = MAX_SIDE_LIMIT
            new_h = int(h * (MAX_SIDE_LIMIT / w))
        else:
            new_h = MAX_SIDE_LIMIT
            new_w = int(w * (MAX_SIDE_LIMIT / h))
        image_to_process = cv2.resize(cv_image, (new_w, new_h), interpolation=cv2.INTER_AREA)

    result = ocr.predict(image_to_process)

    if result and result[0]:
        json_output_path = output_dir / "ocr_result.json"
        result[0].save_to_json(str(json_output_path))
        print(f"  - Saved JSON results to {json_output_path}")

        # Save the processed image(s) to the output directory
        result[0].save_to_img(str(output_dir))
        print(f"  - Saved processed image(s) to {output_dir}")
    else:
        print(f"  - No text found in {image_path.name}.")

def process_pdf(pdf_path):
    """Converts a PDF to images, saves them, resizes if necessary, and runs OCR on each page."""
    print(f"Processing {pdf_path.name}...")
    pdf_output_dir = OUTPUT_DIR / pdf_path.stem
    pdf_output_dir.mkdir(exist_ok=True)

    try:
        images = convert_from_path(str(pdf_path))
    except PDFInfoNotInstalledError:
        print("Error: Poppler is not installed or not in your PATH.")
        print("Please install")
        return

    for i, image in enumerate(images):
        page_num = i + 1
        print(f"  - Processing page {page_num}...")

        page_result_dir = pdf_output_dir / f"page_{page_num}_results"
        page_result_dir.mkdir(exist_ok=True)

        # Save the image from the PDF page
        image_path = page_result_dir / f"page_{page_num}.png"
        image.save(image_path, "PNG")
        print(f"    - Saved page image to {image_path}")

        # Read the saved image for processing
        cv_image = cv2.imread(str(image_path))
        h, w, _ = cv_image.shape
        image_to_process = cv_image

        if max(h, w) > MAX_SIDE_LIMIT:
            print(f"    - Resizing page {page_num} from {w}x{h} to fit within {MAX_SIDE_LIMIT}px limit.")
            if w > h:
                new_w = MAX_SIDE_LIMIT
                new_h = int(h * (MAX_SIDE_LIMIT / w))
            else:
                new_h = MAX_SIDE_LIMIT
                new_w = int(w * (MAX_SIDE_LIMIT / h))
            image_to_process = cv2.resize(cv_image, (new_w, new_h), interpolation=cv2.INTER_AREA)

        result = ocr.predict(image_to_process)

        if result and result[0]:
            json_output_path = page_result_dir / "ocr_result.json"
            result[0].save_to_json(str(json_output_path))
            print(f"    - Saved JSON results to {json_output_path}")

            # Save the processed image(s) to the page result directory
            result[0].save_to_img(str(page_result_dir))
            print(f"    - Saved processed image(s) to {page_result_dir}")
        else:
            print(f"    - No text found on page {page_num}.")

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