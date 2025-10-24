"""
Debug script to test audio generation and serving
"""
import sys
import os
sys.path.insert(0, 'src')

from pipeline import ProcessingPipeline

# Test with the existing file
file_path = "books/The Alchemist mini.pdf"
cache_dir = "cache"

print("=" * 60)
print("Testing Audio Pipeline")
print("=" * 60)

# Initialize pipeline
pipeline = ProcessingPipeline(file_path, cache_dir)
print(f"Total pages: {pipeline.total_pages}")

# Process page 0
print("\nProcessing page 0...")
result = pipeline.get_page_with_prefetch(0)

print(f"\nResult status: {result['status']}")
if result['status'] == 'completed':
    print(f"Audio path: {result['audio_path']}")
    print(f"Audio file exists: {os.path.exists(result['audio_path'])}")
    if os.path.exists(result['audio_path']):
        size = os.path.getsize(result['audio_path'])
        print(f"Audio file size: {size} bytes")
    print(f"\nTranslated text (first 100 chars): {result['translated_text'][:100]}...")
else:
    print(f"Error: {result.get('error')}")
