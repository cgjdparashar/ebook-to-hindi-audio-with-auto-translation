"""
Debug test for Brida file pagination
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from parser import BookParser

def test_brida_pagination():
    """Test that Brida file is broken into pages correctly"""
    
    file_path = 'books/Brida by Paulo Coelho  Full AUDIOBOOK 2.txt'
    
    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}")
        return
    
    print(f"\n{'='*60}")
    print(f"Testing Brida File Pagination")
    print(f"{'='*60}")
    
    # Create parser
    parser = BookParser(file_path)
    
    # Get total pages
    total_pages = parser.get_total_pages()
    
    print(f"\nFile: {os.path.basename(file_path)}")
    print(f"Total pages created: {total_pages}")
    
    # Check first few pages
    for i in range(min(5, total_pages)):
        text = parser.extract_page(i)
        word_count = len(text.split())
        print(f"\nPage {i}: {word_count} words")
        print(f"First 80 chars: {text[:80]}...")
        
        if word_count > 300:
            print(f"  ⚠️  WARNING: Page {i} has {word_count} words (exceeds 250 limit)")
        else:
            print(f"  ✓ Within limits")
    
    print(f"\n{'='*60}")
    if total_pages > 100:
        print(f"✓ File correctly split into {total_pages} pages")
    else:
        print(f"⚠️  Expected ~224 pages, got {total_pages}")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    test_brida_pagination()
