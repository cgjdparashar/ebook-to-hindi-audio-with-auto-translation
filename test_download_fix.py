"""Test download functionality"""
import requests
import os
import time

print("Testing Hinglish download functionality...")
print("=" * 60)

# Upload test file
test_file = "books/test_download.txt"
print(f"\n1. Uploading file: {test_file}")

with open(test_file, 'rb') as f:
    files = {'file': (os.path.basename(test_file), f)}
    response = requests.post("http://localhost:5000/hinglish/upload", files=files)

data = response.json()
if not data.get('success'):
    print(f"❌ Upload failed: {data.get('error')}")
    exit(1)

job_id = data['job_id']
total_pages = data['total_pages']
print(f"✅ Upload successful!")
print(f"   Job ID: {job_id}")
print(f"   Total pages: {total_pages}")

# Start translation
print(f"\n2. Starting translation...")
response = requests.post("http://localhost:5000/hinglish/translate", json={'job_id': job_id})
data = response.json()

if not data.get('success'):
    print(f"❌ Translation failed to start: {data.get('error')}")
    exit(1)

print(f"✅ Translation started")

# Poll for completion
print(f"\n3. Waiting for completion...")
max_wait = 60  # 60 seconds max
start_time = time.time()

while time.time() - start_time < max_wait:
    response = requests.get(f"http://localhost:5000/hinglish/progress/{job_id}")
    data = response.json()
    
    if data.get('success'):
        progress = data['progress']
        status = progress['status']
        completed = progress['completed']
        total = progress['total']
        
        print(f"   Progress: {completed}/{total} pages - Status: {status}")
        
        if status == 'completed':
            print(f"✅ Translation completed!")
            break
        elif status == 'error':
            error = progress.get('error', 'Unknown error')
            print(f"❌ Translation failed: {error}")
            exit(1)
    
    time.sleep(2)
else:
    print(f"❌ Timeout waiting for translation")
    exit(1)

# Test download
print(f"\n4. Testing download...")
response = requests.get(f"http://localhost:5000/hinglish/download/{job_id}")

if response.status_code == 200:
    # Check if it's actually a file (not JSON error)
    content_type = response.headers.get('Content-Type', '')
    
    if 'application/json' in content_type:
        print(f"❌ Download returned JSON error: {response.text}")
        exit(1)
    
    # Save downloaded file
    download_path = f"/tmp/test_download_{job_id}.txt"
    with open(download_path, 'wb') as f:
        f.write(response.content)
    
    file_size = os.path.getsize(download_path)
    print(f"✅ Download successful!")
    print(f"   File saved to: {download_path}")
    print(f"   File size: {file_size} bytes")
    
    # Show first 200 chars
    with open(download_path, 'r', encoding='utf-8') as f:
        content = f.read(200)
        print(f"\n   First 200 characters:")
        print(f"   {'-'*50}")
        print(f"   {content}")
        print(f"   {'-'*50}")
    
    print(f"\n✅ All tests passed! Download functionality is working.")
else:
    print(f"❌ Download failed with status code: {response.status_code}")
    print(f"   Response: {response.text}")
    exit(1)

print("=" * 60)
