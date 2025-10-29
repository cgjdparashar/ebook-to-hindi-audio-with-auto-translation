"""
Async Processing Pipeline
Coordinates background processing of pages for seamless playback
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading
from queue import Queue
import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parser import BookParser
from translator import TranslationService
from tts import TTSEngine


class ProcessingPipeline:
    """Manages async processing of book pages"""
    
    def __init__(self, book_path, cache_dir='cache', prefetch_count=3):
        self.book_path = book_path
        self.cache_dir = cache_dir
        self.prefetch_count = prefetch_count
        
        # Initialize services
        self.parser = BookParser(book_path)
        self.translator = TranslationService(cache_dir)
        self.tts = TTSEngine(cache_dir)
        
        # Processing state
        self.total_pages = self.parser.get_total_pages()
        self.current_page = 0
        self.processed_pages = {}
        self.processing_lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        print(f"Pipeline initialized: {self.total_pages} pages")
    
    def process_page(self, page_num):
        """
        Process a single page: extract → translate → generate audio
        
        Args:
            page_num: Page number to process
            
        Returns:
            dict with page data and audio path
        """
        try:
            print(f"Processing page {page_num + 1}/{self.total_pages}")
            
            # Extract text
            text = self.parser.extract_page(page_num)
            
            # Handle empty pages gracefully
            if not text or not text.strip():
                print(f"Page {page_num + 1}: Empty page detected, using placeholder")
                text = "Empty page"
                translated_text = "खाली पृष्ठ"  # "Empty page" in Hindi
            else:
                print(f"Page {page_num + 1}: Extracted {len(text)} characters")
                # Translate to Hindi
                translated_text = self.translator.translate(text)
                print(f"Page {page_num + 1}: Translated to Hindi ({len(translated_text)} chars)")
            
            # Generate audio
            audio_path = self.tts.generate_audio(translated_text, page_num)
            print(f"Page {page_num + 1}: Audio generated at {audio_path}")
            
            result = {
                'page_num': page_num,
                'original_text': text,
                'translated_text': translated_text,
                'audio_path': audio_path,
                'status': 'completed'
            }
            
            # Cache the result
            with self.processing_lock:
                self.processed_pages[page_num] = result
            
            return result
            
        except Exception as e:
            error_msg = f"Error processing page {page_num}: {str(e)}"
            print(error_msg)
            return {
                'page_num': page_num,
                'status': 'error',
                'error': error_msg
            }
    
    def get_page(self, page_num):
        """
        Get processed page data, process if not ready
        
        Args:
            page_num: Page number to retrieve
            
        Returns:
            Processed page data
        """
        if page_num >= self.total_pages:
            raise ValueError(f"Page {page_num} out of range (total: {self.total_pages})")
        
        # Check if already processed
        with self.processing_lock:
            if page_num in self.processed_pages:
                return self.processed_pages[page_num]
        
        # Process the page
        return self.process_page(page_num)
    
    def prefetch_pages(self, start_page):
        """
        Prefetch upcoming pages in background
        
        Args:
            start_page: Starting page for prefetch
        """
        def prefetch_worker():
            # Increase delay on Render
            delay = 4 if os.environ.get('RENDER') else 1.5
            
            for i in range(start_page, min(start_page + self.prefetch_count, self.total_pages)):
                with self.processing_lock:
                    if i in self.processed_pages:
                        continue
                
                try:
                    self.process_page(i)
                    # Add delay between prefetch requests to avoid rate limiting
                    if i < min(start_page + self.prefetch_count, self.total_pages) - 1:
                        time.sleep(delay)  # Longer delay on Render
                except Exception as e:
                    print(f"Prefetch error for page {i}: {e}")
        
        # Run prefetch in background
        self.executor.submit(prefetch_worker)
    
    def get_page_with_prefetch(self, page_num):
        """
        Get page and trigger prefetch for upcoming pages
        
        Args:
            page_num: Page number to retrieve
            
        Returns:
            Processed page data
        """
        # Get current page
        page_data = self.get_page(page_num)
        
        # Trigger prefetch for next pages
        if page_num + 1 < self.total_pages:
            self.prefetch_pages(page_num + 1)
        
        return page_data
    
    def get_status(self):
        """Get processing status"""
        with self.processing_lock:
            processed_count = len(self.processed_pages)
        
        return {
            'total_pages': self.total_pages,
            'processed_pages': processed_count,
            'current_page': self.current_page
        }
    
    def cleanup(self):
        """Cleanup resources"""
        self.executor.shutdown(wait=False)
        self.tts.cleanup()


def create_pipeline(book_path, cache_dir='cache'):
    """Convenience function to create a processing pipeline"""
    return ProcessingPipeline(book_path, cache_dir)
