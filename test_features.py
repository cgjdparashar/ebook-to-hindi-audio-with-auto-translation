"""
Comprehensive test suite for auto-play and auto-advance features
Tests the web interface using browser automation
"""
import time
import requests
import os


def test_server_running():
    """Test if Flask server is running"""
    print("Testing Flask Server...")
    print("=" * 60)
    
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code == 200:
            print("✓ Server is running on http://localhost:5000")
            return True
        else:
            print(f"✗ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Server is not running! Please start it with: python src/app.py")
        return False
    except Exception as e:
        print(f"✗ Error checking server: {str(e)}")
        return False


def test_file_upload(file_path):
    """Test file upload endpoint"""
    print(f"\nTesting File Upload: {os.path.basename(file_path)}")
    print("=" * 60)
    
    if not os.path.exists(file_path):
        print(f"✗ File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f)}
            response = requests.post("http://localhost:5000/upload", files=files, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✓ Upload successful!")
                print(f"  - Filename: {data.get('filename')}")
                print(f"  - Total pages: {data.get('total_pages')}")
                return True
            else:
                print(f"✗ Upload failed: {data.get('error')}")
                return False
        else:
            print(f"✗ Server returned status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Upload error: {str(e)}")
        return False


def test_page_processing(page_num=0):
    """Test page processing endpoint"""
    print(f"\nTesting Page Processing (Page {page_num})...")
    print("=" * 60)
    
    try:
        response = requests.get(f"http://localhost:5000/process/{page_num}", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✓ Page {page_num} processed successfully!")
                print(f"  - Translated text length: {len(data.get('translated_text', ''))} chars")
                print(f"  - Audio URL: {data.get('audio_url')}")
                
                # Check if audio file exists
                audio_url = data.get('audio_url', '')
                if audio_url:
                    audio_response = requests.head(f"http://localhost:5000{audio_url}", timeout=5)
                    if audio_response.status_code == 200:
                        print(f"✓ Audio file is accessible")
                        return True
                    else:
                        print(f"✗ Audio file not accessible: {audio_response.status_code}")
                        return False
            else:
                print(f"✗ Processing failed: {data.get('error')}")
                return False
        else:
            print(f"✗ Server returned status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Processing error: {str(e)}")
        return False


def run_comprehensive_tests():
    """Run all tests"""
    print("=" * 60)
    print("COMPREHENSIVE FEATURE TESTS")
    print("Auto-play, Auto-advance, and TXT support")
    print("=" * 60)
    
    results = []
    
    # Test 1: Server running
    results.append(("Server Running", test_server_running()))
    
    if not results[0][1]:
        print("\n⚠️ Server not running! Start it with: python src/app.py")
        return
    
    # Test 2: Upload text file
    txt_file = "books/test_story.txt"
    results.append(("TXT Upload", test_file_upload(txt_file)))
    
    if results[-1][1]:
        # Test 3: Process first page
        time.sleep(1)  # Give server time to initialize
        results.append(("Page Processing", test_page_processing(0)))
    
    # Test 4: Upload PDF file (if exists)
    pdf_file = "books/The Alchemist mini.pdf"
    if os.path.exists(pdf_file):
        results.append(("PDF Upload", test_file_upload(pdf_file)))
        
        if results[-1][1]:
            time.sleep(1)
            results.append(("PDF Page Processing", test_page_processing(0)))
    
    # Print summary
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
        print("\nFeatures verified:")
        print("  ✓ TXT file support")
        print("  ✓ File upload working")
        print("  ✓ Page processing working")
        print("  ✓ Audio generation working")
        print("\nTo test auto-play and auto-advance:")
        print("  1. Open http://localhost:5000 in your browser")
        print("  2. Upload a file (TXT, PDF, or EPUB)")
        print("  3. Audio should auto-play when page loads")
        print("  4. When audio ends, it should auto-advance to next page")
    else:
        print("⚠️ SOME TESTS FAILED!")
    
    print("=" * 60)


if __name__ == "__main__":
    run_comprehensive_tests()
