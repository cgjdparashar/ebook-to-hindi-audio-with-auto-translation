"""
Text-to-Speech Module
Converts Hindi text to audio using gTTS
"""
from gtts import gTTS
import os
import hashlib


class TTSEngine:
    """Text-to-Speech engine for Hindi audio generation"""
    
    def __init__(self, cache_dir='cache'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
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
            Path to generated audio file
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Check cache
        cache_key = self._get_cache_key(text)
        audio_path = self._get_audio_path(cache_key)
        
        if os.path.exists(audio_path):
            print(f"Audio cache hit for text (length: {len(text)})")
            return audio_path
        
        # Generate audio
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
            
            print(f"Generating audio for text (length: {len(text)})")
            
            # Use gTTS to generate audio
            tts = gTTS(text=text, lang='hi', slow=False)
            tts.save(audio_path)
            
            if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                print(f"Audio generated successfully: {audio_path} ({os.path.getsize(audio_path)} bytes)")
                return audio_path
            else:
                raise Exception("Audio file was not created or is empty")
                
        except Exception as e:
            raise Exception(f"Failed to generate audio: {str(e)}")
    
    def generate_batch(self, texts):
        """
        Generate audio for multiple texts
        
        Args:
            texts: List of Hindi texts
            
        Returns:
            List of paths to generated audio files
        """
        audio_paths = []
        for i, text in enumerate(texts):
            try:
                audio_path = self.generate_audio(text, page_num=i)
                audio_paths.append(audio_path)
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
