"""
Test TXT file pagination with large text
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from parser import BookParser

def test_large_text():
    """Test that large TXT files are broken into small pages"""
    
    # Create a large test file
    test_file = 'books/large_test.txt'
    os.makedirs('books', exist_ok=True)
    
    # Generate a large text (simulating a large paragraph)
    large_paragraph = ' '.join(['This is a test sentence with multiple words.'] * 100)
    
    # Write test file with multiple large paragraphs
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(large_paragraph + '\n\n')
        f.write(large_paragraph + '\n\n')
        f.write(large_paragraph)
    
    # Test parser
    parser = BookParser(test_file)
    total_pages = parser.get_total_pages()
    
    print(f"\n{'='*60}")
    print(f"Large TXT File Test Results")
    print(f"{'='*60}")
    print(f"Total pages created: {total_pages}")
    
    # Check each page
    for i in range(min(5, total_pages)):  # Check first 5 pages
        text = parser.extract_page(i)
        word_count = len(text.split())
        print(f"\nPage {i}: {word_count} words")
        print(f"First 100 chars: {text[:100]}...")
        
        # Verify word count is within limits
        if word_count > 300:
            print(f"⚠️  WARNING: Page {i} has {word_count} words (exceeds 250 word limit)")
        else:
            print(f"✓ Page {i} is within size limits")
    
    # Cleanup
    os.remove(test_file)
    
    print(f"\n{'='*60}")
    if total_pages > 1:
        print("✓ Large text successfully split into multiple pages")
    else:
        print("⚠️  Large text was not split properly")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    test_large_text()
