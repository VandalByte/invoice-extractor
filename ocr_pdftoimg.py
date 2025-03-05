from paddleocr import PaddleOCR
import easygui
import fitz  # PyMuPDF
from PIL import Image
import numpy as np
import io

def pdf_to_images(pdf_path):
    """
    Converts each page of a PDF to images.
    Returns a list of image paths or numpy arrays.
    """
    doc = fitz.open(pdf_path)
    images = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap()
        
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img_np = np.array(img)  # Convert to numpy array for PaddleOCR
        
        images.append(img_np)

    return images

def upload_and_extract_text():
    """
    Opens a file dialog to select an image or PDF and extracts text using PaddleOCR.
    """
    file_path = easygui.fileopenbox(title="Select an Image or PDF",
                                    filetypes=["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.tiff", "*.pdf"])

    if not file_path:
        print("No file selected.")
        return None, None

    print(f"Selected file: {file_path}")

    ocr = PaddleOCR(use_angle_cls=True, lang="en")

    extracted_text = []
    
    if file_path.lower().endswith(".pdf"):
        print("Processing PDF...")
        images = pdf_to_images(file_path)
        
        for img in images:
            result = ocr.ocr(img, cls=True)
            extracted_text.extend([line[1][0] for line in result[0]])

    else:
        result = ocr.ocr(file_path, cls=True)
        extracted_text = [line[1][0] for line in result[0]]

    print("\nExtracted Text:\n" + "\n".join(extracted_text))
    return file_path, extracted_text

# Run the function
file_path, text = upload_and_extract_text()
