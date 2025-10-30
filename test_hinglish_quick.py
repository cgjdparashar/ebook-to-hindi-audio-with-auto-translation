"""Quick test of the fixed Hinglish translation"""
import sys
sys.path.insert(0, 'src')

from hinglish_translator import HinglishTranslator

# Create translator
translator = HinglishTranslator('cache')

# Test simple sentences
test_cases = [
    ("what are you doing", "aap kya kar rahe ho"),
    ("this is a book", "yeh ek kitab hai"),
    ("I am going to school", "main school ja raha hun"),
]

print("="*60)
print("HINGLISH TRANSLATION TEST")
print("="*60)

for english, expected_hinglish in test_cases:
    print(f"\nEnglish: {english}")
    print(f"Expected: {expected_hinglish}")
    
    # Translate to Hinglish
    result = translator.translate_to_hinglish(english)
    print(f"Got: {result}")
    
    # Check if result is clean (no special chars)
    has_special = any(c in result for c in ['.', '~', '^', '"', '|'])
    print(f"Clean (no special chars): {'✓' if not has_special else '✗'}")
    
print("\n" + "="*60)
