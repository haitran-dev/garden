import fitz  # PyMuPDF
from pytesseract import pytesseract, Output
from PIL import Image
from pdf2image import convert_from_bytes
from typing import List, Dict, Union
import io
import platform
from pathlib import Path
from tqdm import tqdm
import numpy
from PIL import ImageEnhance

class PDFProcessor:
    def __init__(self, pdf_source: Union[str, io.BytesIO], languages: str = 'eng+vie'):
        """
        Initialize with PDF source support
        pdf_source: Can be either a file path (str) or BytesIO object
        """
        self.pdf_source = pdf_source
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
        """Extract text using PyMuPDF (faster, for native PDFs)"""
        # Handle both file path and BytesIO
        if isinstance(self.pdf_source, io.BytesIO):
            doc = fitz.open(stream=self.pdf_source.getvalue(), filetype="pdf")
        else:
            doc = fitz.open(self.pdf_source)
            
        text_contents = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            if text.strip():
                text_contents.append({
                    'page': page_num + 1,
                    'content': text,
                    'extraction_method': 'native'
                })
                
        return text_contents

    def extract_text_ocr(self) -> List[Dict]:
        """Extract text using OCR with improved settings for Vietnamese text"""
        print(f"Converting PDF to images...")
        
        # Handle both file path and BytesIO
        if isinstance(self.pdf_source, io.BytesIO):
            images = convert_from_bytes(self.pdf_source.getvalue(), dpi=300)  # Increased DPI
        else:
            images = convert_from_path(self.pdf_source, dpi=300)  # Increased DPI
            
        text_contents = []
        # Enhanced OCR configuration for better capital letter recognition
        custom_config = (
            f'-l {self.languages} '  # Language packs
            '--psm 6 '               # Assume uniform block of text
            '--oem 3 '              # LSTM neural net mode
            '-c preserve_interword_spaces=1 '  # Preserve spacing
            '-c tessedit_char_blacklist=§ '    # Remove problematic characters
            '-c tessedit_do_invert=0 '         # Don't invert colors
            '-c textord_heavy_nr=1 '           # Better handling of bold text
            '-c textord_min_linesize=3 '       # Minimum text size
            '-c textord_min_xheight=4 '        # Minimum character height
        )
        
        print(f"Processing {len(images)} pages with OCR...")
        for i, image in tqdm(enumerate(images), total=len(images), desc="OCR Processing"):
            # Preprocess image for better OCR
            img_pil = Image.fromarray(numpy.array(image))
            img_pil = img_pil.convert('L')  # Convert to grayscale
            
            # Enhance image contrast
            enhancer = ImageEnhance.Contrast(img_pil)
            img_pil = enhancer.enhance(1.5)  # Increase contrast
            
            ocr_data = pytesseract.image_to_data(
                img_pil,
                config=custom_config,
                output_type=Output.DICT
            )
            text = self._reconstruct_text(ocr_data)
            
            text_contents.append({
                'page': i + 1,
                'content': text,
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

    def process(self) -> List[Dict]:
        """Main processing pipeline"""
        try:
            text_contents = self.extract_text_native()
            total_text = ''.join(t['content'] for t in text_contents)
            if len(total_text.strip()) < 50:
                raise Exception("Insufficient text extracted, falling back to OCR")
        except Exception as e:
            print(f"Native extraction failed or insufficient: {e}")
            print("Falling back to OCR...")
            text_contents = self.extract_text_ocr()
            
        self.chunks = self.chunk_text(text_contents)
        return self.chunks

# Usage
def process_pdf(pdf_path: str, output_dir: str = None):
    processor = PDFProcessor(pdf_path)
    chunks = processor.process(output_dir)
    return chunks
