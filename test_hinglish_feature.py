"""
Test suite for Hinglish translation feature
Tests the new Page 2 functionality
"""
import time
import requests
import os


def test_server_running():
    """Test if Flask server is running"""
    print("\n" + "="*60)
    print("Testing Flask Server...")
    print("="*60)
    
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


def test_hinglish_page_loads():
    """Test if Hinglish page loads"""
    print("\n" + "="*60)
    print("Testing Hinglish Page Load...")
    print("="*60)
    
    try:
        response = requests.get("http://localhost:5000/hinglish", timeout=5)
        if response.status_code == 200:
            print("✓ Hinglish translation page loads successfully")
            return True
        else:
            print(f"✗ Hinglish page returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error loading Hinglish page: {str(e)}")
        return False


def test_hinglish_file_upload(file_path):
    """Test file upload for Hinglish translation"""
    print("\n" + "="*60)
    print(f"Testing Hinglish File Upload: {os.path.basename(file_path)}")
    print("="*60)
    
    if not os.path.exists(file_path):
        print(f"✗ File not found: {file_path}")
        return False, None
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f)}
            response = requests.post("http://localhost:5000/hinglish/upload", files=files, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✓ Upload successful!")
                print(f"  - Filename: {data.get('filename')}")
                print(f"  - Total pages: {data.get('total_pages')}")
                print(f"  - Job ID: {data.get('job_id')}")
                print(f"  - Resume from: {data.get('resume_from', 0)}")
                return True, data.get('job_id')
            else:
                print(f"✗ Upload failed: {data.get('error')}")
                return False, None
        else:
            print(f"✗ Server returned status code: {response.status_code}")
            print(f"  Response: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"✗ Upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None


def test_hinglish_translation_start(job_id):
    """Test starting Hinglish translation"""
    print("\n" + "="*60)
    print(f"Testing Hinglish Translation Start...")
    print("="*60)
    
    try:
        response = requests.post(
            "http://localhost:5000/hinglish/translate",
            json={'job_id': job_id},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✓ Translation started successfully!")
                return True
            else:
                print(f"✗ Translation start failed: {data.get('error')}")
                return False
        else:
            print(f"✗ Server returned status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Translation start error: {str(e)}")
        return False


def test_hinglish_translation_progress(job_id, timeout=300):
    """Test Hinglish translation progress and wait for completion"""
    print("\n" + "="*60)
    print(f"Monitoring Hinglish Translation Progress...")
    print("="*60)
    
    start_time = time.time()
    last_completed = -1
    
    try:
        while time.time() - start_time < timeout:
            response = requests.get(f"http://localhost:5000/hinglish/progress/{job_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    progress = data.get('progress', {})
                    total = progress.get('total', 0)
                    completed = progress.get('completed', 0)
                    status = progress.get('status', 'unknown')
                    
                    # Show progress update if changed
                    if completed != last_completed:
                        percent = int((completed / total) * 100) if total > 0 else 0
                        print(f"  Progress: {completed}/{total} pages ({percent}%) - Status: {status}")
                        last_completed = completed
                    
                    if status == 'completed':
                        print(f"✓ Translation completed successfully!")
                        print(f"  Total pages processed: {total}")
                        return True
                    elif status == 'error':
                        error = progress.get('error', 'Unknown error')
                        print(f"✗ Translation failed: {error}")
                        return False
            
            time.sleep(2)  # Poll every 2 seconds
        
        print(f"✗ Translation timed out after {timeout} seconds")
        return False
            
    except Exception as e:
        print(f"✗ Progress monitoring error: {str(e)}")
        return False


def test_hinglish_download(job_id):
    """Test downloading Hinglish translation"""
    print("\n" + "="*60)
    print(f"Testing Hinglish Download...")
    print("="*60)
    
    try:
        response = requests.get(f"http://localhost:5000/hinglish/download/{job_id}", timeout=30)
        
        if response.status_code == 200:
            # Save the downloaded file temporarily
            download_path = f"/tmp/test_hinglish_download_{job_id}.txt"
            with open(download_path, 'wb') as f:
                f.write(response.content)
            
            file_size = os.path.getsize(download_path)
            print(f"✓ Download successful!")
            print(f"  - File saved to: {download_path}")
            print(f"  - File size: {file_size} bytes")
            
            # Show first 500 characters of the file
            with open(download_path, 'r', encoding='utf-8') as f:
                content = f.read(500)
                print(f"\n  First 500 characters:")
                print(f"  {'-'*50}")
                print(f"  {content}")
                print(f"  {'-'*50}")
            
            return True
        else:
            print(f"✗ Download failed with status code: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Download error: {str(e)}")
        return False


def test_existing_audiobook_feature():
    """Test that existing audiobook feature (Page 1) still works"""
    print("\n" + "="*60)
    print("Testing Existing Audiobook Feature (Page 1)...")
    print("="*60)
    
    try:
        # Test main page loads
        response = requests.get("http://localhost:5000/", timeout=5)
        if response.status_code != 200:
            print(f"✗ Main page failed to load")
            return False
        
        print(f"✓ Main audiobook page loads successfully")
        
        # Test upload endpoint exists
        test_file = "books/test_hinglish_story.txt"
        if os.path.exists(test_file):
            with open(test_file, 'rb') as f:
                files = {'file': (os.path.basename(test_file), f)}
                response = requests.post("http://localhost:5000/upload", files=files, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✓ Audiobook upload still works")
                    return True
                else:
                    print(f"✗ Audiobook upload failed: {data.get('error')}")
                    return False
        else:
            print(f"⚠ Test file not found, skipping upload test")
            return True
            
    except Exception as e:
        print(f"✗ Error testing audiobook feature: {str(e)}")
        return False


def run_comprehensive_hinglish_tests():
    """Run all Hinglish translation tests"""
    print("\n" + "="*80)
    print("COMPREHENSIVE HINGLISH TRANSLATION TESTS")
    print("Testing Page 2: English to Hinglish Translation Feature")
    print("="*80)
    
    results = []
    
    # Test 1: Server running
    results.append(("Server Running", test_server_running()))
    
    if not results[0][1]:
        print("\n⚠️ Server not running! Start it with: python src/app.py")
        return
    
    # Test 2: Hinglish page loads
    results.append(("Hinglish Page Loads", test_hinglish_page_loads()))
    
    # Test 3: Test existing audiobook feature still works
    results.append(("Existing Audiobook Feature", test_existing_audiobook_feature()))
    
    # Test 4: Upload file for Hinglish translation
    test_file = "books/test_hinglish_story.txt"
    success, job_id = test_hinglish_file_upload(test_file)
    results.append(("Hinglish File Upload", success))
    
    if success and job_id:
        # Test 5: Start translation
        success = test_hinglish_translation_start(job_id)
        results.append(("Hinglish Translation Start", success))
        
        if success:
            # Test 6: Monitor progress
            success = test_hinglish_translation_progress(job_id)
            results.append(("Hinglish Translation Progress", success))
            
            if success:
                # Test 7: Download result
                success = test_hinglish_download(job_id)
                results.append(("Hinglish Download", success))
    
    # Print summary
    print("\n" + "="*80)
    print("TEST RESULTS SUMMARY")
    print("="*80)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    print("="*80)
    
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\nFeatures verified:")
        print("  ✓ Hinglish translation page accessible")
        print("  ✓ File upload for Hinglish translation working")
        print("  ✓ Translation processing working")
        print("  ✓ Progress tracking working")
        print("  ✓ Download functionality working")
        print("  ✓ Existing audiobook feature still works")
        print("\nTo manually test:")
        print("  1. Open http://localhost:5000 for audiobook feature")
        print("  2. Open http://localhost:5000/hinglish for Hinglish translation")
    else:
        print("⚠️ SOME TESTS FAILED!")
        print("\nPlease check the error messages above.")
    
    print("="*80)


if __name__ == "__main__":
    run_comprehensive_hinglish_tests()
