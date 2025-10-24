"""
Translation Service Module
Translates English text to Hindi using deep-translator with caching
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


class TranslationService:
    """Handles English to Hindi translation with caching"""
    
    def __init__(self, cache_dir='cache'):
        # Create session with SSL disabled
        session = requests.Session()
        session.mount('https://', SSLAdapter())
        session.verify = False
        
        self.translator = GoogleTranslator(source='en', target='hi')
        # Monkey patch the translator's session
        if hasattr(self.translator, 'proxies'):
            self.translator.proxies = {'http': None, 'https': None}
        
        self.session = session
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, 'translations.json')
        self.cache = self._load_cache()
        
    def _load_cache(self):
        """Load translation cache from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading cache: {e}")
                return {}
        return {}
    
    def _save_cache(self):
        """Save translation cache to file"""
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def _get_cache_key(self, text):
        """Generate cache key for text"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _chunk_text(self, text, max_chunk_size=4500):
        """Split text into smaller chunks for translation"""
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
        
        return chunks
    
    def translate(self, text, retry_count=3):
        """
        Translate English text to Hindi
        
        Args:
            text: English text to translate
            retry_count: Number of retry attempts on failure
            
        Returns:
            Translated Hindi text
        """
        if not text or not text.strip():
            return ""
        
        # Check cache first
        cache_key = self._get_cache_key(text)
        if cache_key in self.cache:
            print(f"Cache hit for text (length: {len(text)})")
            return self.cache[cache_key]
        
        # Split into chunks if text is too long
        if len(text) > 4500:
            print(f"Text too long ({len(text)} chars), splitting into chunks...")
            chunks = self._chunk_text(text)
            translated_chunks = []
            for i, chunk in enumerate(chunks):
                print(f"Translating chunk {i+1}/{len(chunks)}")
                translated_chunk = self._translate_single(chunk, retry_count)
                translated_chunks.append(translated_chunk)
            translated_text = ' '.join(translated_chunks)
        else:
            translated_text = self._translate_single(text, retry_count)
        
        # Cache the result
        self.cache[cache_key] = translated_text
        self._save_cache()
        
        return translated_text
    
    def _translate_single(self, text, retry_count=3):
        """Translate a single chunk of text"""
        # Translate with retry logic
        for attempt in range(retry_count):
            try:
                print(f"Translating text (length: {len(text)}, attempt: {attempt + 1})")
                
                # Manual translation using requests without SSL verification
                url = "https://translate.googleapis.com/translate_a/single"
                params = {
                    'client': 'gtx',
                    'sl': 'en',
                    'tl': 'hi',
                    'dt': 't',
                    'q': text
                }
                
                response = self.session.get(url, params=params, verify=False, timeout=10)
                response.raise_for_status()
                
                # Parse response
                result = response.json()
                translated_text = ''.join([item[0] for item in result[0] if item[0]])
                
                return translated_text
                
            except Exception as e:
                print(f"Translation error (attempt {attempt + 1}): {e}")
                if attempt < retry_count - 1:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Translation failed after {retry_count} attempts: {str(e)}")
    
    def translate_batch(self, texts):
        """
        Translate multiple texts
        
        Args:
            texts: List of English texts
            
        Returns:
            List of translated Hindi texts
        """
        translations = []
        for text in texts:
            translated = self.translate(text)
            translations.append(translated)
        return translations
    
    def clear_cache(self):
        """Clear translation cache"""
        self.cache = {}
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        print("Translation cache cleared")


def translate_text(text, cache_dir='cache'):
    """Convenience function to translate text"""
    service = TranslationService(cache_dir)
    return service.translate(text)
