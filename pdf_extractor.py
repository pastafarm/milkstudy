"""
PDF Text Extractor Module
Extracts and processes text content from PDF files for quiz generation.
"""

import PyPDF2
from typing import List, Dict
import re


class PDFExtractor:
    """Handles extraction and chunking of text from PDF files."""

    def __init__(self, pdf_path: str):
        """
        Initialize the PDF extractor.

        Args:
            pdf_path: Path to the PDF file
        """
        self.pdf_path = pdf_path
        self.text = ""
        self.pages = []

    def extract_text(self) -> str:
        """
        Extract all text from the PDF file.

        Returns:
            Complete text content of the PDF
        """
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                self.pages = []

                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    self.pages.append({
                        'page_num': page_num + 1,
                        'text': page_text
                    })
                    self.text += page_text + "\n"

                return self.text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

    def get_page_text(self, page_num: int) -> str:
        """
        Get text from a specific page.

        Args:
            page_num: Page number (1-indexed)

        Returns:
            Text content of the specified page
        """
        if not self.pages:
            self.extract_text()

        for page in self.pages:
            if page['page_num'] == page_num:
                return page['text']

        return ""

    def get_text_chunks(self, chunk_size: int = 2000, overlap: int = 200) -> List[str]:
        """
        Split the text into manageable chunks for processing.

        Args:
            chunk_size: Maximum size of each chunk in characters
            overlap: Number of overlapping characters between chunks

        Returns:
            List of text chunks
        """
        if not self.text:
            self.extract_text()

        # Clean the text
        clean_text = self._clean_text(self.text)

        chunks = []
        start = 0
        text_length = len(clean_text)

        while start < text_length:
            end = start + chunk_size

            # Try to break at a sentence or paragraph boundary
            if end < text_length:
                # Look for period followed by space or newline
                last_period = clean_text.rfind('. ', start, end)
                last_newline = clean_text.rfind('\n', start, end)

                break_point = max(last_period, last_newline)
                if break_point > start:
                    end = break_point + 1

            chunks.append(clean_text[start:end].strip())
            start = end - overlap

        return chunks

    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.

        Args:
            text: Raw text from PDF

        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove page numbers (simple pattern)
        text = re.sub(r'\n\d+\n', '\n', text)

        # Fix common PDF extraction issues
        text = text.replace('\x00', '')

        return text.strip()

    def get_total_pages(self) -> int:
        """
        Get the total number of pages in the PDF.

        Returns:
            Total page count
        """
        if not self.pages:
            self.extract_text()

        return len(self.pages)

    def search_text(self, keyword: str) -> List[Dict]:
        """
        Search for a keyword in the PDF text.

        Args:
            keyword: The keyword to search for

        Returns:
            List of matches with page numbers and context
        """
        if not self.pages:
            self.extract_text()

        matches = []
        for page in self.pages:
            if keyword.lower() in page['text'].lower():
                # Find the context around the keyword
                text_lower = page['text'].lower()
                index = text_lower.find(keyword.lower())

                # Get context (100 chars before and after)
                start = max(0, index - 100)
                end = min(len(page['text']), index + len(keyword) + 100)
                context = page['text'][start:end].strip()

                matches.append({
                    'page': page['page_num'],
                    'context': context,
                    'keyword': keyword
                })

        return matches
