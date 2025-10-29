"""
Quick verification test for TXT pagination improvements
Run this while the Flask server is running on localhost:5000
"""
import requests
import time

BASE_URL = 'http://localhost:5000'

def test_txt_upload_and_processing():
    """Test TXT file upload and verify pagination"""
    
    print("\n" + "="*60)
    print("Testing TXT File Processing Improvements")
    print("="*60)
    
    # Create a medium-sized test file
    test_content = """
This is the first paragraph of our test story. It contains several sentences 
to make it realistic. We want to ensure that the pagination works correctly 
and creates multiple pages from this content.

This is the second paragraph. It also has multiple sentences. The smart 
pagination algorithm should handle this properly and create pages that are 
neither too large nor too small.

This is the third paragraph with even more content. We're adding enough text 
here to ensure that the pagination algorithm will create multiple pages. Each 
page should be around 200-250 words for optimal processing speed.

The fourth paragraph continues our story. By having multiple paragraphs with 
varying lengths, we can test how well the algorithm groups content together. 
The goal is fast processing without losing narrative flow.

And finally, a fifth paragraph to round things out. This should be enough 
content to create at least 2-3 pages, demonstrating that large text files 
will be automatically split into manageable chunks.
"""
    
    # Save test file
    with open('books/quick_test.txt', 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print("\n✓ Created test file: books/quick_test.txt")
    print(f"  Word count: {len(test_content.split())} words")
    
    # Upload file
    try:
        with open('books/quick_test.txt', 'rb') as f:
            files = {'file': ('quick_test.txt', f, 'text/plain')}
            response = requests.post(f'{BASE_URL}/upload', files=files, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            total_pages = data.get('total_pages', 0)
            print(f"\n✓ Upload successful!")
            print(f"  Total pages created: {total_pages}")
            
            if total_pages > 1:
                print(f"  ✓ Text correctly split into multiple pages")
            else:
                print(f"  ⚠️  Only 1 page created (expected 2+)")
            
            # Test processing first page
            print(f"\n→ Processing page 0...")
            start_time = time.time()
            
            process_response = requests.get(f'{BASE_URL}/process/0', timeout=60)
            
            if process_response.status_code == 200:
                process_time = time.time() - start_time
                page_data = process_response.json()
                
                print(f"  ✓ Page 0 processed in {process_time:.1f} seconds")
                print(f"  Status: {page_data.get('status')}")
                
                if page_data.get('status') == 'ready':
                    print(f"  ✓ Audio URL: {page_data.get('audio_url')}")
                    
                    # Check if audio file exists
                    audio_url = page_data.get('audio_url')
                    if audio_url:
                        audio_response = requests.get(f'{BASE_URL}{audio_url}', timeout=10)
                        if audio_response.status_code == 200:
                            print(f"  ✓ Audio file accessible ({len(audio_response.content)} bytes)")
                        else:
                            print(f"  ⚠️  Audio file not accessible (status {audio_response.status_code})")
                else:
                    print(f"  ⚠️  Page status: {page_data.get('status')}")
                    if 'error' in page_data:
                        print(f"  Error: {page_data['error']}")
            else:
                print(f"  ✗ Processing failed (status {process_response.status_code})")
                print(f"  Response: {process_response.text[:200]}")
        else:
            print(f"\n✗ Upload failed (status {response.status_code})")
            print(f"  Response: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("\n✗ Could not connect to server")
        print("  Make sure Flask is running: python src/app.py")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
    
    print("\n" + "="*60)
    print("Test Complete")
    print("="*60 + "\n")

if __name__ == '__main__':
    test_txt_upload_and_processing()
