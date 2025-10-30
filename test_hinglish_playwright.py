"""
Playwright E2E test for Hinglish translation feature
Tests file upload, page-by-page translation progress, and download
"""

import requests
import time
import json
import os

BASE_URL = "http://localhost:5000"
TEST_FILE = "books/Brida_by_Paulo_Coelho_Full_AUDIOBOOK_5.txt"

def cleanup_test_data():
    """Clean up progress and cache files before testing"""
    try:
        # Delete output files
        for file in os.listdir('output'):
            if file.endswith('_progress.json') or file.endswith('_hinglish.txt'):
                os.remove(os.path.join('output', file))
        print("✓ Cleaned up output files")
        
        # Delete Hinglish cache to force fresh translation
        cache_file = 'cache/hinglish_translations.json'
        if os.path.exists(cache_file):
            os.remove(cache_file)
        print("✓ Cleaned up Hinglish translation cache")
    except Exception as e:
        print(f"⚠ Cleanup warning: {e}")

def test_hinglish_page_loads():
    """Test that the Hinglish page loads correctly"""
    print("\n[TEST 1] Testing Hinglish page load...")
    
    response = requests.get(f"{BASE_URL}/hinglish")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert "English to Hinglish Translator" in response.text, "Page title not found"
    
    print("✓ Hinglish page loads successfully")

def test_file_upload():
    """Test file upload endpoint"""
    print("\n[TEST 2] Testing file upload...")
    
    if not os.path.exists(TEST_FILE):
        print(f"⚠ Test file not found: {TEST_FILE}")
        return None
    
    with open(TEST_FILE, 'rb') as f:
        files = {'file': (os.path.basename(TEST_FILE), f, 'text/plain')}
        response = requests.post(f"{BASE_URL}/hinglish/upload", files=files)
    
    assert response.status_code == 200, f"Upload failed with status {response.status_code}"
    
    data = response.json()
    assert data['success'] == True, "Upload response missing success=True"
    assert 'job_id' in data, "Upload response missing job_id"
    assert 'total_pages' in data, "Upload response missing total_pages"
    
    print(f"✓ File uploaded successfully")
    print(f"  Job ID: {data['job_id']}")
    print(f"  Total pages: {data['total_pages']}")
    print(f"  Resume from: {data.get('resume_from', 0)}")
    
    return data

def test_start_translation(job_id):
    """Test starting translation"""
    print("\n[TEST 3] Testing translation start...")
    
    response = requests.post(
        f"{BASE_URL}/hinglish/translate",
        headers={'Content-Type': 'application/json'},
        json={'job_id': job_id}
    )
    
    assert response.status_code == 200, f"Translation start failed with status {response.status_code}"
    
    data = response.json()
    assert data['success'] == True, "Translation start response missing success=True"
    
    print("✓ Translation started successfully")

def test_progress_updates(job_id, total_pages, max_wait=60):
    """Test that progress updates page-by-page"""
    print("\n[TEST 4] Testing page-by-page progress updates...")
    
    start_time = time.time()
    last_completed = -1
    progress_updates = []
    
    while time.time() - start_time < max_wait:
        response = requests.get(f"{BASE_URL}/hinglish/progress/{job_id}")
        assert response.status_code == 200, f"Progress check failed with status {response.status_code}"
        
        data = response.json()
        assert data['success'] == True, "Progress response missing success=True"
        
        completed = data.get('completed', 0)
        status = data.get('status', 'unknown')
        
        # Track progress updates
        if completed > last_completed:
            progress_updates.append({
                'completed': completed,
                'total': data['total'],
                'status': status,
                'timestamp': time.time() - start_time
            })
            print(f"  Progress: Page {completed}/{data['total']} ({status})")
            last_completed = completed
        
        # Check completion
        if status == 'completed':
            print(f"✓ Translation completed successfully!")
            print(f"  Total updates: {len(progress_updates)}")
            print(f"  Time elapsed: {time.time() - start_time:.2f}s")
            return progress_updates
        
        # Check for errors
        if status == 'error':
            error_msg = data.get('error', 'Unknown error')
            raise AssertionError(f"Translation failed: {error_msg}")
        
        time.sleep(2)  # Poll every 2 seconds
    
    raise TimeoutError(f"Translation did not complete within {max_wait}s")

def test_download_file(job_id):
    """Test downloading the translated file"""
    print("\n[TEST 5] Testing file download...")
    
    response = requests.get(f"{BASE_URL}/hinglish/download/{job_id}")
    assert response.status_code == 200, f"Download failed with status {response.status_code}"
    
    # Check content type
    content_type = response.headers.get('Content-Type', '')
    assert 'text/plain' in content_type or 'application/octet-stream' in content_type, \
        f"Unexpected content type: {content_type}"
    
    # Check content
    content = response.text
    assert len(content) > 0, "Downloaded file is empty"
    assert "Page 1" in content, "Downloaded file missing page markers"
    
    print(f"✓ File downloaded successfully")
    print(f"  File size: {len(content)} characters")

def run_all_tests():
    """Run all Hinglish translation tests"""
    print("="*60)
    print("HINGLISH TRANSLATION E2E TESTS")
    print("="*60)
    
    # Cleanup before testing
    cleanup_test_data()
    
    try:
        # Test 1: Page loads
        test_hinglish_page_loads()
        
        # Test 2: Upload file
        upload_data = test_file_upload()
        if not upload_data:
            print("⚠ Skipping remaining tests - test file not found")
            return
        
        job_id = upload_data['job_id']
        total_pages = upload_data['total_pages']
        
        # Test 3: Start translation
        test_start_translation(job_id)
        
        # Test 4: Monitor progress (with timeout for large files)
        # For 224 pages, set max_wait to allow ~5 seconds per page
        max_wait = min(total_pages * 5, 300)  # Cap at 5 minutes
        progress_updates = test_progress_updates(job_id, total_pages, max_wait=max_wait)
        
        # Test 5: Download file
        test_download_file(job_id)
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print(f"Summary:")
        print(f"  - Total pages translated: {total_pages}")
        print(f"  - Progress updates captured: {len(progress_updates)}")
        print(f"  - Average time per page: {progress_updates[-1]['timestamp']/total_pages:.2f}s")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except TimeoutError as e:
        print(f"\n⏱ TEST TIMEOUT: {e}")
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get(BASE_URL, timeout=2)
        print(f"✓ Server is running at {BASE_URL}")
    except requests.exceptions.ConnectionError:
        print(f"❌ ERROR: Server is not running at {BASE_URL}")
        print("Please start the Flask server with: python src/app.py")
        exit(1)
    
    # Run tests
    success = run_all_tests()
    exit(0 if success else 1)
