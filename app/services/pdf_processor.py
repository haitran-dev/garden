from typing import List, Dict, Union
from pydantic import BaseModel, Field
from PyPDF2 import PdfReader
import io
import re

class TextChunk(BaseModel):
    """A chunk of text from the PDF, ready for LLM processing"""
    content: str = Field(..., description="The text content")
    page_number: int = Field(..., description="Source page number")
    chunk_number: int = Field(..., description="Chunk sequence number")
    clean_content: str = Field(..., description="Cleaned text for LLM")
    metadata: Dict = Field(default_factory=dict, description="Additional chunk metadata")
    embedding: List[float] = Field(default=None, description="Vector embedding for similarity search")

class ProcessedDocument(BaseModel):
    """Processed PDF document with chunks ready for LLM"""
    chunks: List[TextChunk] = Field(..., description="List of text chunks")
    total_pages: int = Field(..., description="Total number of pages")
    total_chunks: int = Field(..., description="Total number of chunks")
    metadata: Dict = Field(default_factory=dict, description="Document metadata")

class PDFProcessor:
    """
    Processes PDF documents for LLM integration by extracting,
    cleaning, and chunking text content.
    """
    
    def __init__(self, source: Union[str, io.BytesIO], chunk_size: int = 1000):
        """
        Initialize the PDF processor
        Args:
            source: Either a file path or BytesIO object containing the PDF
            chunk_size: Maximum size of text chunks in characters
        """
        self.source = source
        self.chunk_size = chunk_size

    def process_pdf(self) -> ProcessedDocument:
        """
        Main processing pipeline for PDF documents
        Returns:
            ProcessedDocument: Processed document with text chunks ready for LLM
        """
        # Create PDF reader object
        reader = PdfReader(self.source)
        chunks = []
        chunk_number = 0

        # Process each page in the PDF
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            # Extract raw text from page
            text = page.extract_text()
            
            # Split page text into manageable chunks
            page_chunks = self._create_chunks(text, self.chunk_size)
            
            # Process each chunk and create TextChunk objects
            for chunk in page_chunks:
                # Clean text for LLM processing
                clean_text = self._clean_text_for_llm(chunk)
                chunks.append(TextChunk(
                    content=chunk,
                    clean_content=clean_text,
                    page_number=page_num + 1,
                    chunk_number=chunk_number,
                    metadata={
                        "source_page": page_num + 1,
                        "length": len(chunk),
                        "clean_length": len(clean_text),
                        "estimated_tokens": len(clean_text.split())  # Approximate token count
                    }
                ))
                chunk_number += 1

        # Create and return processed document
        return ProcessedDocument(
            chunks=chunks,
            total_pages=len(reader.pages),
            total_chunks=len(chunks),
            metadata=reader.metadata if hasattr(reader, 'metadata') else {}
        )

    def _clean_text_for_llm(self, text: str) -> str:
        """
        Enhanced text cleaning for better LLM processing
        Args:
            text: Raw text to clean
        Returns:
            str: Thoroughly cleaned and normalized text
        """
        # Handle common PDF extraction issues
        text = self._fix_common_pdf_issues(text)
        
        # Remove unwanted elements
        text = self._remove_unwanted_elements(text)
        
        # Normalize text
        text = self._normalize_text(text)
        
        # Fix spacing and punctuation
        text = self._fix_spacing_and_punctuation(text)
        
        return text.strip()

    def _fix_common_pdf_issues(self, text: str) -> str:
        """Fix common issues from PDF text extraction"""
        # Replace various types of hyphens and dashes
        text = re.sub(r'[\u2010-\u2015]', '-', text)
        
        # Fix broken words (word- break)
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
        
        # Handle ligatures
        ligature_map = {
            'ﬁ': 'fi', 'ﬂ': 'fl', 'ﬀ': 'ff',
            'ﬃ': 'ffi', 'ﬄ': 'ffl'
        }
        for ligature, replacement in ligature_map.items():
            text = text.replace(ligature, replacement)
            
        return text

    def _remove_unwanted_elements(self, text: str) -> str:
        """Remove unwanted elements from text"""
        # Remove page numbers
        text = re.sub(r'\b\d+\s*\|\s*Page', '', text)
        
        # Remove headers/footers (common patterns)
        text = re.sub(r'^.*?\[Running Head:.*?\].*$', '', text, flags=re.MULTILINE)
        
        # Remove citations [1], [2,3], etc.
        text = re.sub(r'\[\d+(?:,\s*\d+)*\]', '', text)
        
        # Remove figure and table references
        text = re.sub(r'(Figure|Fig\.|Table)\s+\d+', '', text)
        
        # Remove URLs (basic pattern)
        text = re.sub(r'http[s]?://\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+\.\S+', '', text)
        
        return text

    def _normalize_text(self, text: str) -> str:
        """Normalize text content"""
        # Convert unicode characters to ascii where possible
        text = text.encode('ascii', 'ignore').decode()
        
        # Convert all whitespace to single spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove repeated punctuation
        text = re.sub(r'([.,!?])\1+', r'\1', text)
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        return text

    def _fix_spacing_and_punctuation(self, text: str) -> str:
        """Fix spacing around punctuation and other characters"""
        # Remove space before punctuation
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        
        # Ensure space after punctuation
        text = re.sub(r'([.,!?;:])(\w)', r'\1 \2', text)
        
        # Fix spaces around parentheses
        text = re.sub(r'\s*\(\s*', ' (', text)
        text = re.sub(r'\s*\)\s*', ') ', text)
        
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text

    def _create_chunks(self, text: str, chunk_size: int) -> List[str]:
        """
        Split text into chunks while preserving sentence boundaries
        Args:
            text: Text to split into chunks
            chunk_size: Maximum chunk size in characters
        Returns:
            List[str]: List of text chunks
        """
        chunks = []
        current_chunk = []
        current_size = 0
        
        # Split text into sentences
        sentences = text.split('.')
        
        # Process each sentence
        for sentence in sentences:
            sentence = sentence.strip() + '.'
            sentence_size = len(sentence)
            
            # Start new chunk if current one would exceed size limit
            if current_size + sentence_size > chunk_size and current_chunk:
                chunks.append(''.join(current_chunk))
                current_chunk = []
                current_size = 0
            
            # Add sentence to current chunk
            current_chunk.append(sentence)
            current_size += sentence_size
        
        # Add any remaining text as final chunk
        if current_chunk:
            chunks.append(''.join(current_chunk))
        
        return chunks
