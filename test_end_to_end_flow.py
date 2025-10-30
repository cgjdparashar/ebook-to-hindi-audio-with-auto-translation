"""
End-to-end test for Hinglish translation feature
Tests the complete flow from upload to download
"""
import requests
import time
import json
import os

BASE_URL = "http://localhost:5000"

def test_complete_flow():
    """Test complete Hinglish translation flow"""
    print("=" * 80)
    print("END-TO-END HINGLISH TRANSLATION TEST")
    print("=" * 80)
    
    # Create test file
    test_file = 'books/test_e2e.txt'
    test_content = """Once upon a time in a small village, there lived a young boy named Ram.
He was very kind and helpful to everyone in the village.
Every morning, he would wake up early and help his mother fetch water from the well.
One day, he found a small injured bird on his way to school.
He carefully picked up the bird and took it home to nurse it back to health."""
    
    print(f"\n1. Creating test file: {test_file}")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    print(f"   ✅ Test file created ({len(test_content)} characters)")
    
    # Step 1: Upload file
    print("\n2. Uploading file to /hinglish/upload...")
    with open(test_file, 'rb') as f:
        files = {'file': ('test_e2e.txt', f, 'text/plain')}
        response = requests.post(f'{BASE_URL}/hinglish/upload', files=files)
    
    print(f"   Status Code: {response.status_code}")
    if response.status_code != 200:
        print(f"   ❌ Upload failed: {response.text}")
        return False
    
    upload_data = response.json()
    print(f"   Response: {json.dumps(upload_data, indent=4)}")
    
    job_id = upload_data.get('job_id')
    total_pages = upload_data.get('total_pages')
    
    if not job_id:
        print("   ❌ No job_id in response!")
        return False
    
    print(f"   ✅ Upload successful!")
    print(f"   Job ID: {job_id}")
    print(f"   Total Pages: {total_pages}")
    
    # Step 2: Start translation
    print("\n3. Starting translation via /hinglish/translate...")
    response = requests.post(
        f'{BASE_URL}/hinglish/translate',
        json={'job_id': job_id},
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"   Status Code: {response.status_code}")
    if response.status_code != 200:
        print(f"   ❌ Translation start failed: {response.text}")
        return False
    
    translate_data = response.json()
    print(f"   Response: {json.dumps(translate_data, indent=4)}")
    print("   ✅ Translation started!")
    
    # Step 3: Monitor progress
    print("\n4. Monitoring progress via /hinglish/progress/<job_id>...")
    print("   (Polling every 1 second for up to 60 seconds)")
    print()
    
    last_completed = -1
    start_time = time.time()
    max_wait = 60  # 60 seconds timeout
    
    while True:
        elapsed = time.time() - start_time
        if elapsed > max_wait:
            print(f"\n   ⚠️ Timeout after {max_wait} seconds")
            break
        
        response = requests.get(f'{BASE_URL}/hinglish/progress/{job_id}')
        
        if response.status_code != 200:
            print(f"   ❌ Progress check failed: {response.status_code}")
            time.sleep(1)
            continue
        
        progress_data = response.json()
        status = progress_data.get('status')
        completed = progress_data.get('completed', 0)
        total = progress_data.get('total', total_pages)
        error = progress_data.get('error')
        
        # Only print if progress changed
        if completed != last_completed or status in ['completed', 'error']:
            timestamp = time.strftime("%H:%M:%S")
            progress_pct = (completed / total * 100) if total > 0 else 0
            print(f"   [{timestamp}] Pages: {completed}/{total} ({progress_pct:.1f}%) - Status: {status}")
            last_completed = completed
        
        if status == 'completed':
            print(f"\n   ✅ Translation completed! {completed}/{total} pages processed")
            break
        elif status == 'error':
            print(f"\n   ❌ Translation failed with error:")
            print(f"   {error}")
            return False
        
        time.sleep(1)
    
    # Step 4: Download result
    print("\n5. Downloading translated file via /hinglish/download/<job_id>...")
    response = requests.get(f'{BASE_URL}/hinglish/download/{job_id}')
    
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   ❌ Download failed: {response.text}")
        return False
    
    # Save downloaded file
    download_path = 'books/test_e2e_downloaded.txt'
    with open(download_path, 'wb') as f:
        f.write(response.content)
    
    file_size = len(response.content)
    print(f"   ✅ Download successful!")
    print(f"   File size: {file_size} bytes")
    print(f"   Saved to: {download_path}")
    
    # Step 5: Verify content
    print("\n6. Verifying downloaded content...")
    with open(download_path, 'r', encoding='utf-8') as f:
        downloaded_content = f.read()
    
    print(f"   Content length: {len(downloaded_content)} characters")
    print(f"   Content preview (first 200 chars):")
    print(f"   {downloaded_content[:200]}...")
    
    # Check if it's in Hinglish (Roman script, not Devanagari)
    has_devanagari = any('\u0900' <= char <= '\u097F' for char in downloaded_content)
    has_roman = any('a' <= char.lower() <= 'z' for char in downloaded_content)
    
    print(f"\n   Has Devanagari script: {has_devanagari}")
    print(f"   Has Roman script: {has_roman}")
    
    if has_devanagari:
        print("   ⚠️ WARNING: Content contains Devanagari (Hindi) script!")
        print("   Expected: Hinglish (Roman script only)")
        return False
    
    if not has_roman:
        print("   ❌ ERROR: Content has no Roman characters!")
        return False
    
    print("   ✅ Content is in Roman script (Hinglish)")
    
    # Cleanup
    print("\n7. Cleaning up test files...")
    for file_path in [test_file, download_path]:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"   Deleted: {file_path}")
    
    return True

if __name__ == '__main__':
    print("\nNOTE: This test requires:")
    print("  1. Flask server running on http://localhost:5000")
    print("  2. Internet access for Google Translate API")
    print()
    
    try:
        success = test_complete_flow()
        
        print("\n" + "=" * 80)
        if success:
            print("✅ ALL TESTS PASSED - Feature working end-to-end!")
        else:
            print("❌ TEST FAILED - See errors above")
        print("=" * 80)
        
    except requests.exceptions.ConnectionError:
        print("\n" + "=" * 80)
        print("❌ ERROR: Cannot connect to Flask server")
        print("   Please start the server with: python src/app.py")
        print("=" * 80)
    except Exception as e:
        print("\n" + "=" * 80)
        print(f"❌ UNEXPECTED ERROR: {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
