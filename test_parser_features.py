"""
Test script to verify text file parsing and auto-play features
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from parser import BookParser

def test_text_parser():
    """Test text file parsing"""
    print("Testing Text File Parser...")
    print("=" * 60)
    
    # Test with the sample text file
    txt_path = "books/test_story.txt"
    
    if not os.path.exists(txt_path):
        print(f"Error: {txt_path} not found!")
        return False
    
    try:
        parser = BookParser(txt_path)
        print(f"✓ File type detected: {parser.file_type}")
        
        total_pages = parser.get_total_pages()
        print(f"✓ Total pages: {total_pages}")
        
        # Test extracting first page
        first_page = parser.extract_page(0)
        print(f"\n✓ First page extracted ({len(first_page)} characters):")
        print("-" * 60)
        print(first_page[:200] + "..." if len(first_page) > 200 else first_page)
        print("-" * 60)
        
        # Test extracting all pages
        if total_pages > 1:
            second_page = parser.extract_page(1)
            print(f"\n✓ Second page extracted ({len(second_page)} characters):")
            print("-" * 60)
            print(second_page[:200] + "..." if len(second_page) > 200 else second_page)
            print("-" * 60)
        
        print("\n✅ Text file parsing test PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Text file parsing test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_pdf_parser():
    """Test PDF parsing still works"""
    print("\n\nTesting PDF Parser...")
    print("=" * 60)
    
    pdf_path = "books/The Alchemist mini.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"Warning: {pdf_path} not found! Skipping PDF test.")
        return True
    
    try:
        parser = BookParser(pdf_path)
        print(f"✓ File type detected: {parser.file_type}")
        
        total_pages = parser.get_total_pages()
        print(f"✓ Total pages: {total_pages}")
        
        # Test extracting first page
        first_page = parser.extract_page(0)
        print(f"✓ First page extracted ({len(first_page)} characters)")
        
        print("\n✅ PDF parsing test PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ PDF parsing test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("PARSER FEATURE TESTS")
    print("=" * 60)
    
    results = []
    results.append(("Text File Parsing", test_text_parser()))
    results.append(("PDF Parsing", test_pdf_parser()))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    print("=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️ SOME TESTS FAILED!")
    print("=" * 60)
