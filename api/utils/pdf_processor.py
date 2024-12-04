import fitz  # PyMuPDF
from pytesseract import pytesseract, Output
from PIL import Image
from pdf2image import convert_from_path
from typing import List, Dict
import os
import platform
from pathlib import Path
from tqdm import tqdm

class PDFProcessor:
    def __init__(self, pdf_path: str, languages: str = 'eng+vie'):
        """
        Initialize with language support
        languages: str - Tesseract language codes, e.g., 'eng+vie' for English and Vietnamese
        """
        self.pdf_path = pdf_path
        self.chunks = []
        self.languages = languages
        self.configure_tesseract()
        
    def configure_tesseract(self):
        """Configure Tesseract path and parameters"""
        system = platform.system().lower()
        
        if system == 'darwin':  # macOS
            tesseract_path = '/usr/local/bin/tesseract'
        elif system == 'windows':
            tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        else:  # Linux
            tesseract_path = '/usr/bin/tesseract'
            
        if Path(tesseract_path).exists():
            pytesseract.tesseract_cmd = tesseract_path
        else:
            raise Exception(
                f"Tesseract not found at {tesseract_path}. "
                "Please verify installation path."
            )

    def extract_text_native(self) -> List[Dict]:
        """
        Extract text using PyMuPDF (faster, for native PDFs)
        """
        doc = fitz.open(self.pdf_path)
        text_contents = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            if text.strip():  # Check if text was extracted
                text_contents.append({
                    'page': page_num + 1,
                    'content': text,
                    'source': self.pdf_path,
                    'extraction_method': 'native'
                })
                
        return text_contents

    def extract_text_ocr(self, output_dir: str = None) -> List[Dict]:
        """
        Extract text using OCR with improved language support
        """
        print(f"Converting PDF to images...")
        images = convert_from_path(self.pdf_path)
        text_contents = []
        
        # OCR configuration
        custom_config = f'-l {self.languages} --psm 6 --oem 3'
        
        print(f"Processing {len(images)} pages with OCR...")
        for i, image in tqdm(enumerate(images), total=len(images), desc="OCR Processing"):
            if output_dir:
                img_path = os.path.join(output_dir, f"page_{i + 1}.png")
                image.save(img_path, "PNG")
                # Get detailed OCR data
                ocr_data = pytesseract.image_to_data(
                    Image.open(img_path), 
                    config=custom_config, 
                    output_type=Output.DICT
                )
                text = self._reconstruct_text(ocr_data)
            else:
                ocr_data = pytesseract.image_to_data(
                    image, 
                    config=custom_config, 
                    output_type=Output.DICT
                )
                text = self._reconstruct_text(ocr_data)
                
            text_contents.append({
                'page': i + 1,
                'content': text,
                'source': self.pdf_path,
                'extraction_method': 'ocr'
            })
            
        return text_contents

    def _reconstruct_text(self, ocr_data: Dict) -> str:
        """
        Reconstruct text from OCR data preserving punctuation and layout
        """
        text = []
        last_block_no = -1
        last_line_no = -1
        
        for i in range(len(ocr_data['text'])):
            word = ocr_data['text'][i]
            block_no = ocr_data['block_num'][i]
            line_no = ocr_data['line_num'][i]
            
            if word.strip():
                if block_no != last_block_no:
                    text.append('\n\n')
                elif line_no != last_line_no:
                    text.append('\n')
                elif text:
                    text.append(' ')
                
                text.append(word)
                last_block_no = block_no
                last_line_no = line_no
        
        return ''.join(text).strip()

    def chunk_text(self, text_contents: List[Dict], chunk_size: int = 1000) -> List[Dict]:
        """
        Split text into smaller chunks for better processing
        """
        chunked_texts = []
        
        for page_content in text_contents:
            text = page_content['content']
            words = text.split()
            
            for i in range(0, len(words), chunk_size):
                chunk = ' '.join(words[i:i + chunk_size])
                chunk_dict = page_content.copy()  # Preserve metadata
                chunk_dict['content'] = chunk
                chunk_dict['chunk_index'] = i // chunk_size
                chunked_texts.append(chunk_dict)
                
        return chunked_texts

    def process(self, output_dir: str = None, chunk_size: int = 1000) -> List[Dict]:
        """
        Main processing pipeline with fallback
        """
        try:
            # Try native extraction first
            text_contents = self.extract_text_native()
            
            # Check if we got meaningful text
            total_text = ''.join(t['content'] for t in text_contents)
            if len(total_text.strip()) < 50:  # Arbitrary threshold
                raise Exception("Insufficient text extracted, falling back to OCR")
                
        except Exception as e:
            print(f"Native extraction failed or insufficient: {e}")
            print("Falling back to OCR...")
            text_contents = self.extract_text_ocr(output_dir)
            
        self.chunks = self.chunk_text(text_contents, chunk_size)
        return self.chunks

# Usage
def process_pdf(pdf_path: str, output_dir: str = None):
    processor = PDFProcessor(pdf_path)
    chunks = processor.process(output_dir)
    return chunks
