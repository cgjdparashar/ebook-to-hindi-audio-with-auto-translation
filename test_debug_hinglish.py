"""Debug Hinglish translation to see what's being returned"""
import sys
sys.path.insert(0, 'src')

from hinglish_translator import HinglishTranslator

# Create translator
translator = HinglishTranslator('cache')

# Test simple sentence
text = "This is a test"
print(f"Input: {text}")
print(f"Translating...")

result = translator.translate_to_hinglish(text)

print(f"\nResult: {result}")
print(f"Result type: {type(result)}")
print(f"Result length: {len(result)}")
print(f"Result repr: {repr(result[:50])}")

# Check if contains Devanagari
import unicodedata
has_devanagari = any('\u0900' <= c <= '\u097F' for c in result)
print(f"Contains Devanagari: {has_devanagari}")

# Check if contains Roman
has_roman = any('a' <= c.lower() <= 'z' for c in result)
print(f"Contains Roman: {has_roman}")
