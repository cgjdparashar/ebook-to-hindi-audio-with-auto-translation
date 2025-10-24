"""
PDF and EPUB Parser Module
Extracts text from PDF and EPUB files with page-level granularity
"""
import PyPDF2
from ebooklib import epub
from ebooklib import ITEM_DOCUMENT
from bs4 import BeautifulSoup
import os


class BookParser:
    """Parser for PDF and EPUB files"""
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_type = self._detect_file_type()
        
    def _detect_file_type(self):
        """Detect file type based on extension"""
        ext = os.path.splitext(self.file_path)[1].lower()
        if ext == '.pdf':
            return 'pdf'
        elif ext == '.epub':
            return 'epub'
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    def get_total_pages(self):
        """Get total number of pages/chapters"""
        if self.file_type == 'pdf':
            return self._get_pdf_pages()
        elif self.file_type == 'epub':
            return self._get_epub_chapters()
    
    def extract_page(self, page_num):
        """Extract text from specific page/chapter"""
        if self.file_type == 'pdf':
            return self._extract_pdf_page(page_num)
        elif self.file_type == 'epub':
            return self._extract_epub_chapter(page_num)
    
    def _get_pdf_pages(self):
        """Get number of pages in PDF"""
        try:
            with open(self.file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                return len(reader.pages)
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    def _extract_pdf_page(self, page_num):
        """Extract text from specific PDF page"""
        try:
            with open(self.file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                if page_num >= len(reader.pages):
                    raise ValueError(f"Page {page_num} out of range")
                page = reader.pages[page_num]
                text = page.extract_text()
                return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting PDF page {page_num}: {str(e)}")
    
    def _get_epub_chapters(self):
        """Get number of chapters in EPUB"""
        try:
            book = epub.read_epub(self.file_path)
            chapters = [item for item in book.get_items() if item.get_type() == ITEM_DOCUMENT]
            return len(chapters)
        except Exception as e:
            raise Exception(f"Error reading EPUB: {str(e)}")
    
    def _extract_epub_chapter(self, chapter_num):
        """Extract text from specific EPUB chapter"""
        try:
            book = epub.read_epub(self.file_path)
            chapters = [item for item in book.get_items() if item.get_type() == ITEM_DOCUMENT]
            
            if chapter_num >= len(chapters):
                raise ValueError(f"Chapter {chapter_num} out of range")
            
            chapter = chapters[chapter_num]
            content = chapter.get_content()
            soup = BeautifulSoup(content, 'html.parser')
            text = soup.get_text()
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting EPUB chapter {chapter_num}: {str(e)}")
    
    def extract_all_pages(self):
        """Extract text from all pages/chapters"""
        total_pages = self.get_total_pages()
        pages = []
        for i in range(total_pages):
            text = self.extract_page(i)
            pages.append({
                'page_num': i,
                'text': text
            })
        return pages


def parse_book(file_path):
    """Convenience function to parse a book file"""
    parser = BookParser(file_path)
    return parser
