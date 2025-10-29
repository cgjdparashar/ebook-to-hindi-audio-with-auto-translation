"""
Test script to debug the processing pipeline
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from parser import BookParser
from translator import TranslationService
from tts import TTSEngine

print("="*60)
print("Testing AI Audiobook Translator Components")
print("="*60)

# Test 1: PDF Parser
print("\n1. Testing PDF Parser...")
try:
    parser = BookParser("books/The Alchemist mini.pdf")
    total_pages = parser.get_total_pages()
    print(f"✓ PDF loaded: {total_pages} pages")
    
    # Extract first page
    page_0_text = parser.extract_page(0)
    print(f"✓ Page 1 extracted: {len(page_0_text)} characters")
    print(f"  First 100 chars: {page_0_text[:100]}...")
except Exception as e:
    print(f"✗ PDF Parser Error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Translation
print("\n2. Testing Translation Service...")
try:
    translator = TranslationService('cache')
    test_text = "Hello, this is a test."
    translated = translator.translate(test_text)
    print(f"✓ Translation successful")
    print(f"  English: {test_text}")
    print(f"  Hindi: {translated}")
except Exception as e:
    print(f"✗ Translation Error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: TTS
print("\n3. Testing TTS Engine...")
try:
    tts = TTSEngine('cache')
    test_hindi = "नमस्ते, यह एक परीक्षण है।"
    audio_path = tts.generate_audio(test_hindi)
    print(f"✓ TTS successful")
    print(f"  Audio file: {audio_path}")
    print(f"  File exists: {os.path.exists(audio_path)}")
    if os.path.exists(audio_path):
        print(f"  File size: {os.path.getsize(audio_path)} bytes")
except Exception as e:
    print(f"✗ TTS Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("Test Complete!")
print("="*60)
