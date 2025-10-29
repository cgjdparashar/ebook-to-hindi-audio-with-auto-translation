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
        elif ext == '.txt':
            return 'txt'
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    def get_total_pages(self):
        """Get total number of pages/chapters"""
        if self.file_type == 'pdf':
            return self._get_pdf_pages()
        elif self.file_type == 'epub':
            return self._get_epub_chapters()
        elif self.file_type == 'txt':
            return self._get_txt_pages()
    
    def extract_page(self, page_num):
        """Extract text from specific page/chapter"""
        if self.file_type == 'pdf':
            return self._extract_pdf_page(page_num)
        elif self.file_type == 'epub':
            return self._extract_epub_chapter(page_num)
        elif self.file_type == 'txt':
            return self._extract_txt_page(page_num)
    
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
    
    def _get_txt_pages(self):
        """Get number of pages in TXT file (smart pagination)"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Handle empty or whitespace-only files
            content = content.strip()
            if not content:
                self._txt_pages = [""]  # Empty page for empty files
                return 1
            
            # Break into small pages (200-250 words max for faster processing)
            MAX_WORDS_PER_PAGE = 250
            pages = []
            
            # Split by double newlines (paragraphs) first
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            
            # If no paragraphs (continuous text), use word-based chunking
            if len(paragraphs) <= 1:
                # File has no paragraph breaks - split by words directly
                all_words = content.split()
                
                # Create pages of MAX_WORDS_PER_PAGE words each
                for i in range(0, len(all_words), MAX_WORDS_PER_PAGE):
                    page_words = all_words[i:i + MAX_WORDS_PER_PAGE]
                    pages.append(' '.join(page_words))
            else:
                # Normal paragraph processing
                current_page = []
                word_count = 0
                
                for para in paragraphs:
                    para_words = len(para.split())
                    
                    # If single paragraph is too large, split it further
                    if para_words > MAX_WORDS_PER_PAGE:
                        # Split long paragraph by sentences
                        sentences = para.replace('! ', '!|').replace('? ', '?|').replace('. ', '.|').split('|')
                        for sentence in sentences:
                            sentence = sentence.strip()
                            if not sentence:
                                continue
                            sentence_words = len(sentence.split())
                            
                            if word_count + sentence_words > MAX_WORDS_PER_PAGE and current_page:
                                # Save current page
                                pages.append(' '.join(current_page))
                                current_page = [sentence]
                                word_count = sentence_words
                            else:
                                current_page.append(sentence)
                                word_count += sentence_words
                    else:
                        # Normal paragraph processing
                        if word_count + para_words > MAX_WORDS_PER_PAGE and current_page:
                            # Save current page
                            pages.append('\n\n'.join(current_page))
                            current_page = [para]
                            word_count = para_words
                        else:
                            current_page.append(para)
                            word_count += para_words
                
                # Add last page
                if current_page:
                    pages.append('\n\n'.join(current_page))
            
            # Store pages for later extraction
            self._txt_pages = pages
            return len(pages) if pages else 1
            
        except Exception as e:
            raise Exception(f"Error reading TXT file: {str(e)}")
    
    def _extract_txt_page(self, page_num):
        """Extract text from specific TXT page"""
        try:
            # Ensure pages are loaded
            if not hasattr(self, '_txt_pages'):
                self._get_txt_pages()
            
            if page_num >= len(self._txt_pages):
                raise ValueError(f"Page {page_num} out of range")
            
            return self._txt_pages[page_num]
        except Exception as e:
            raise Exception(f"Error extracting TXT page {page_num}: {str(e)}")
    
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
