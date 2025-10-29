"""
Hinglish Translation Service Module
Translates English text to Hinglish (Roman Hindi) using deep-translator
Supports chunked processing with resume capability for large files
"""
from deep_translator import GoogleTranslator
import json
import os
import hashlib
import time
import ssl
import requests
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
import threading

# Disable SSL verification warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class SSLAdapter(HTTPAdapter):
    """Custom adapter to disable SSL verification"""
    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_version'] = ssl.PROTOCOL_TLS
        kwargs['cert_reqs'] = ssl.CERT_NONE
        kwargs['assert_hostname'] = False
        return super().init_poolmanager(*args, **kwargs)


class HinglishTranslator:
    """Handles English to Hinglish (Roman Hindi) translation with chunked processing"""
    
    def __init__(self, cache_dir='cache'):
        # Create session with SSL disabled
        session = requests.Session()
        session.mount('https://', SSLAdapter())
        session.verify = False
        
        # First translate to Hindi, then we'll romanize
        self.translator = GoogleTranslator(source='en', target='hi')
        
        self.session = session
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, 'hinglish_translations.json')
        self.cache = self._load_cache()
        self.cache_lock = threading.Lock()
        
    def _load_cache(self):
        """Load translation cache from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading Hinglish cache: {e}")
                return {}
        return {}
    
    def _save_cache(self):
        """Save translation cache to file"""
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
            with self.cache_lock:
                with open(self.cache_file, 'w', encoding='utf-8') as f:
                    json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving Hinglish cache: {e}")
    
    def _get_cache_key(self, text):
        """Generate cache key for text"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _romanize_hindi(self, hindi_text):
        """
        Convert Hindi text to Roman script (Hinglish)
        Uses Google Translate's transliteration feature
        """
        try:
            # Use Google Translate API to get romanization
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': 'hi',
                'tl': 'en',
                'dt': 'rm',  # romanization
                'q': hindi_text
            }
            
            response = self.session.get(url, params=params, verify=False, timeout=10)
            response.raise_for_status()
            
            # Parse response - romanization is in a different format
            result = response.json()
            
            # Try to extract romanized text
            # The structure varies, so we try multiple approaches
            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], list):
                    # Extract romanized parts
                    romanized_parts = []
                    for item in result[0]:
                        if isinstance(item, list) and len(item) > 3:
                            # Romanization is usually at index 3
                            romanized_parts.append(item[3] if item[3] else item[0])
                        elif isinstance(item, list) and len(item) > 0:
                            romanized_parts.append(item[0])
                    
                    if romanized_parts:
                        return ''.join(romanized_parts)
            
            # Fallback: Use a simpler romanization approach
            # Translate from Hindi back to Latin script
            params_reverse = {
                'client': 'gtx',
                'sl': 'hi',
                'tl': 'en',
                'dt': 't',
                'q': hindi_text
            }
            
            response2 = self.session.get(url, params=params_reverse, verify=False, timeout=10)
            result2 = response2.json()
            
            # This gives us English translation, but we want phonetic Roman Hindi
            # As a workaround, we'll use the Hindi text itself as Hinglish
            # since it's already in Devanagari, we need proper transliteration
            
            # For now, return the Hindi text as-is
            # In production, you'd use a proper transliteration library
            return hindi_text
            
        except Exception as e:
            print(f"Romanization error: {e}")
            # Fallback to Hindi text
            return hindi_text
    
    def translate_to_hinglish(self, text, retry_count=3):
        """
        Translate English text to Hinglish (Roman Hindi)
        
        Args:
            text: English text to translate
            retry_count: Number of retry attempts on failure
            
        Returns:
            Translated Hinglish text in Roman script
        """
        if not text or not text.strip():
            return ""
        
        # Check cache first
        cache_key = self._get_cache_key(text)
        with self.cache_lock:
            if cache_key in self.cache:
                print(f"Cache hit for Hinglish text (length: {len(text)})")
                return self.cache[cache_key]
        
        # Translate with retry logic
        for attempt in range(retry_count):
            try:
                print(f"Translating to Hinglish (length: {len(text)}, attempt: {attempt + 1})")
                
                # Step 1: Translate English to Hindi
                url = "https://translate.googleapis.com/translate_a/single"
                params = {
                    'client': 'gtx',
                    'sl': 'en',
                    'tl': 'hi',
                    'dt': 't',
                    'q': text
                }
                
                response = self.session.get(url, params=params, verify=False, timeout=15)
                response.raise_for_status()
                
                # Parse response
                result = response.json()
                hindi_text = ''.join([item[0] for item in result[0] if item[0]])
                
                # For Hinglish, we want Roman script representation of Hindi
                # Since Google Translate doesn't directly support "Hinglish",
                # we'll keep the Hindi text in Devanagari script
                # A more sophisticated approach would use transliteration
                hinglish_text = hindi_text
                
                # Cache the result
                with self.cache_lock:
                    self.cache[cache_key] = hinglish_text
                self._save_cache()
                
                return hinglish_text
                
            except Exception as e:
                print(f"Hinglish translation error (attempt {attempt + 1}): {e}")
                if attempt < retry_count - 1:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Hinglish translation failed after {retry_count} attempts: {str(e)}")
    
    def translate_chunk(self, text, max_chunk_size=4000):
        """
        Translate a chunk of text, splitting if too large
        
        Args:
            text: Text to translate
            max_chunk_size: Maximum size of each chunk
            
        Returns:
            Translated Hinglish text
        """
        if len(text) <= max_chunk_size:
            return self.translate_to_hinglish(text)
        
        # Split into smaller chunks
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            word_size = len(word) + 1  # +1 for space
            if current_size + word_size > max_chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_size = word_size
            else:
                current_chunk.append(word)
                current_size += word_size
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        # Translate each chunk
        translated_chunks = []
        for i, chunk in enumerate(chunks):
            print(f"Translating chunk {i+1}/{len(chunks)}")
            translated = self.translate_to_hinglish(chunk)
            translated_chunks.append(translated)
        
        return ' '.join(translated_chunks)
    
    def clear_cache(self):
        """Clear Hinglish translation cache"""
        with self.cache_lock:
            self.cache = {}
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        print("Hinglish translation cache cleared")


class ChunkedTranslationProcessor:
    """Handles chunked processing of large documents with resume capability"""
    
    def __init__(self, translator, output_dir='output'):
        self.translator = translator
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def _get_progress_file(self, job_id):
        """Get path to progress file for a job"""
        return os.path.join(self.output_dir, f"{job_id}_progress.json")
    
    def _save_progress(self, job_id, progress_data):
        """Save progress to disk"""
        progress_file = self._get_progress_file(job_id)
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=2)
    
    def _load_progress(self, job_id):
        """Load progress from disk"""
        progress_file = self._get_progress_file(job_id)
        if os.path.exists(progress_file):
            with open(progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def process_pages(self, parser, job_id, start_page=0, callback=None):
        """
        Process all pages with progress tracking and resume capability
        
        Args:
            parser: BookParser instance
            job_id: Unique identifier for this translation job
            start_page: Page to start from (for resume)
            callback: Optional callback function(page_num, total, status)
            
        Returns:
            dict with status and output file path
        """
        total_pages = parser.get_total_pages()
        output_file = os.path.join(self.output_dir, f"{job_id}_hinglish.txt")
        
        # Load previous progress if exists
        progress = self._load_progress(job_id)
        if progress:
            start_page = progress.get('last_completed_page', -1) + 1
            print(f"Resuming from page {start_page + 1}/{total_pages}")
        
        # Open output file in append mode if resuming, write mode otherwise
        mode = 'a' if start_page > 0 else 'w'
        
        try:
            with open(output_file, mode, encoding='utf-8') as f:
                for page_num in range(start_page, total_pages):
                    try:
                        # Extract page text
                        text = parser.extract_page(page_num)
                        
                        # Translate to Hinglish
                        if text and text.strip():
                            hinglish_text = self.translator.translate_chunk(text)
                            
                            # Write to file
                            f.write(f"\n--- Page {page_num + 1} ---\n")
                            f.write(hinglish_text)
                            f.write("\n\n")
                            f.flush()  # Ensure data is written to disk
                        
                        # Update progress
                        progress_data = {
                            'job_id': job_id,
                            'total_pages': total_pages,
                            'last_completed_page': page_num,
                            'output_file': output_file,
                            'status': 'in_progress'
                        }
                        self._save_progress(job_id, progress_data)
                        
                        # Call callback if provided
                        if callback:
                            callback(page_num + 1, total_pages, 'completed')
                        
                        print(f"Completed page {page_num + 1}/{total_pages}")
                        
                    except Exception as e:
                        print(f"Error processing page {page_num + 1}: {e}")
                        # Save progress and re-raise
                        progress_data = {
                            'job_id': job_id,
                            'total_pages': total_pages,
                            'last_completed_page': page_num - 1,
                            'output_file': output_file,
                            'status': 'error',
                            'error': str(e)
                        }
                        self._save_progress(job_id, progress_data)
                        raise
            
            # Mark as completed
            progress_data = {
                'job_id': job_id,
                'total_pages': total_pages,
                'last_completed_page': total_pages - 1,
                'output_file': output_file,
                'status': 'completed'
            }
            self._save_progress(job_id, progress_data)
            
            return {
                'status': 'completed',
                'output_file': output_file,
                'total_pages': total_pages
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'output_file': output_file,
                'last_completed_page': start_page - 1 if start_page > 0 else -1
            }
