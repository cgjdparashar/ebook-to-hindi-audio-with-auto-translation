"""
Test to debug progress issue
"""
import requests
import time
import json

BASE_URL = "http://localhost:5000"

def test_upload_and_progress():
    """Test upload and progress tracking"""
    print("=" * 60)
    print("Testing Upload and Progress Tracking")
    print("=" * 60)
    
    # Step 1: Upload file
    print("\n1. Uploading file...")
    file_path = 'books/test_translation.txt'
    
    with open(file_path, 'rb') as f:
        files = {'file': (f'test_translation.txt', f, 'text/plain')}
        response = requests.post(f'{BASE_URL}/hinglish/upload', files=files)
    
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    if response.status_code != 200:
        print("   ❌ Upload failed!")
        return False
    
    upload_data = response.json()
    job_id = upload_data.get('job_id')
    print(f"   ✅ Upload successful! Job ID: {job_id}")
    
    # Step 2: Start translation
    print("\n2. Starting translation...")
    response = requests.post(
        f'{BASE_URL}/hinglish/translate',
        json={'job_id': job_id},
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    if response.status_code != 200:
        print("   ❌ Translation start failed!")
        return False
    
    print("   ✅ Translation started!")
    
    # Step 3: Poll progress
    print("\n3. Polling progress...")
    for i in range(20):  # Poll for 20 seconds max
        time.sleep(1)
        response = requests.get(f'{BASE_URL}/hinglish/progress/{job_id}')
        
        if response.status_code != 200:
            print(f"   ❌ Progress check failed: {response.status_code}")
            continue
        
        progress_data = response.json()
        print(f"   Poll {i+1}: {json.dumps(progress_data, indent=2)}")
        
        status = progress_data.get('status')
        completed = progress_data.get('completed', 0)
        total = progress_data.get('total', 0)
        
        if status == 'completed':
            print(f"   ✅ Translation completed! {completed}/{total} pages")
            return True
        elif status == 'error':
            print(f"   ❌ Translation error: {progress_data.get('error')}")
            return False
    
    print("   ⚠️ Timeout waiting for completion")
    return False

if __name__ == '__main__':
    try:
        success = test_upload_and_progress()
        if success:
            print("\n" + "=" * 60)
            print("✅ TEST PASSED: Progress tracking working!")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("❌ TEST FAILED: Progress tracking issue detected")
            print("=" * 60)
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
