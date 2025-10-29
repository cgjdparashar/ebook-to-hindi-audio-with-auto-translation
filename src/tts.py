"""
Text-to-Speech Module
Converts Hindi text to audio using gTTS
"""
from gtts import gTTS
import os
import hashlib
import time
from io import BytesIO


class TTSEngine:
    """Text-to-Speech engine for Hindi audio generation"""
    
    def __init__(self, cache_dir='cache'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.memory_cache = {}  # In-memory cache for audio data
        print("TTS Engine initialized with gTTS")
    
    def _get_cache_key(self, text):
        """Generate cache key for audio file"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _get_audio_path(self, cache_key):
        """Get full path for cached audio file"""
        return os.path.join(self.cache_dir, f"{cache_key}.mp3")
    
    def generate_audio(self, text, page_num=None):
        """
        Generate audio from Hindi text
        
        Args:
            text: Hindi text to convert to speech
            page_num: Optional page number for naming
            
        Returns:
            Path to generated audio file (for backward compatibility)
        """
        if not text or not text.strip():
            # For empty text, create a silent 1-second audio file
            print(f"Empty text detected, generating silent audio")
            cache_key = self._get_cache_key("__EMPTY__")
            audio_path = self._get_audio_path(cache_key)
            
            # Check if silent audio already exists
            if cache_key not in self.memory_cache and not os.path.exists(audio_path):
                # Generate minimal silent audio (1 second of silence)
                tts = gTTS(text=".", lang='hi', slow=False)
                audio_fp = BytesIO()
                tts.write_to_fp(audio_fp)
                audio_data = audio_fp.getvalue()
                
                # Save to disk
                with open(audio_path, 'wb') as f:
                    f.write(audio_data)
                
                # Store in memory cache
                self.memory_cache[cache_key] = audio_data
            elif os.path.exists(audio_path) and cache_key not in self.memory_cache:
                # Load existing silent audio into memory
                with open(audio_path, 'rb') as f:
                    self.memory_cache[cache_key] = f.read()
            
            return audio_path
        
        # Check cache
        cache_key = self._get_cache_key(text)
        audio_path = self._get_audio_path(cache_key)
        
        # Check memory cache first
        if cache_key in self.memory_cache:
            print(f"Audio memory cache hit for text (length: {len(text)})")
            return audio_path
        
        # Check disk cache
        if os.path.exists(audio_path):
            print(f"Audio disk cache hit for text (length: {len(text)})")
            # Load into memory cache
            with open(audio_path, 'rb') as f:
                self.memory_cache[cache_key] = f.read()
            return audio_path
        
        # Generate audio
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
            
            print(f"Generating audio for text (length: {len(text)})")
            
            # Retry logic with exponential backoff for rate limiting
            max_retries = 8  # Increased from 5
            base_delay = 5  # Increased from 2 seconds to 5 seconds
            
            for attempt in range(max_retries):
                try:
                    # Add initial delay to avoid rate limiting (especially on Render)
                    if attempt == 0 and os.environ.get('RENDER'):
                        time.sleep(3)  # 3 second delay before first attempt on Render
                    
                    # Use gTTS to generate audio in memory
                    tts = gTTS(text=text, lang='hi', slow=False)
                    
                    # Save to memory buffer
                    audio_buffer = BytesIO()
                    tts.write_to_fp(audio_buffer)
                    audio_data = audio_buffer.getvalue()
                    
                    # Store in memory cache
                    self.memory_cache[cache_key] = audio_data
                    
                    # Also save to disk for local development
                    try:
                        with open(audio_path, 'wb') as f:
                            f.write(audio_data)
                        print(f"Audio saved to disk: {audio_path} ({len(audio_data)} bytes)")
                    except Exception as disk_err:
                        print(f"Warning: Could not save to disk (ephemeral filesystem?): {disk_err}")
                    
                    print(f"Audio generated successfully in memory: {len(audio_data)} bytes")
                    return audio_path
                    
                except Exception as tts_error:
                    error_msg = str(tts_error)
                    
                    # Check if it's a rate limit error
                    if "429" in error_msg or "Too Many Requests" in error_msg or "HTTPError" in error_msg:
                        if attempt < max_retries - 1:
                            delay = base_delay * (2 ** attempt)  # Exponential backoff: 5, 10, 20, 40, 80...
                            print(f"Rate limit hit. Retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                            time.sleep(delay)
                            continue
                        else:
                            raise Exception(f"Failed to generate audio after {max_retries} attempts: Rate limit exceeded. Please try again in a few minutes.")
                    else:
                        # Not a rate limit error, raise immediately
                        raise Exception(f"Failed to generate audio: {error_msg}")
                        
        except Exception as e:
            raise Exception(f"Failed to generate audio: {str(e)}")
    
    def get_audio_data(self, text):
        """
        Get audio data from memory cache
        
        Args:
            text: Hindi text to get audio for
            
        Returns:
            BytesIO object containing audio data, or None if not found
        """
        cache_key = self._get_cache_key(text)
        
        if cache_key in self.memory_cache:
            return BytesIO(self.memory_cache[cache_key])
        
        # Try to load from disk if not in memory
        audio_path = self._get_audio_path(cache_key)
        if os.path.exists(audio_path):
            try:
                with open(audio_path, 'rb') as f:
                    audio_data = f.read()
                self.memory_cache[cache_key] = audio_data
                return BytesIO(audio_data)
            except Exception as e:
                print(f"Error loading audio from disk: {e}")
        
        return None
    
    def generate_batch(self, texts):
        """
        Generate audio for multiple texts
        
        Args:
            texts: List of Hindi texts
            
        Returns:
            List of paths to generated audio files
        """
        audio_paths = []
        # Increase delay on Render to avoid rate limits
        delay_between = 3 if os.environ.get('RENDER') else 1
        
        for i, text in enumerate(texts):
            try:
                audio_path = self.generate_audio(text, page_num=i)
                audio_paths.append(audio_path)
                
                # Add delay between requests to avoid rate limiting
                if i < len(texts) - 1:  # Don't delay after the last one
                    time.sleep(delay_between)
                    
            except Exception as e:
                print(f"Error generating audio for text {i}: {e}")
                audio_paths.append(None)
        return audio_paths
    
    def clear_cache(self):
        """Clear audio cache"""
        try:
            if os.path.exists(self.cache_dir):
                for file in os.listdir(self.cache_dir):
                    if file.endswith('.wav') or file.endswith('.mp3'):
                        os.remove(os.path.join(self.cache_dir, file))
                print("Audio cache cleared")
        except Exception as e:
            print(f"Error clearing cache: {e}")
    
    def cleanup(self):
        """Cleanup TTS engine"""
        pass  # No cleanup needed for gTTS


def text_to_speech(text, cache_dir='cache'):
    """Convenience function to convert text to speech"""
    engine = TTSEngine(cache_dir)
    return engine.generate_audio(text)
