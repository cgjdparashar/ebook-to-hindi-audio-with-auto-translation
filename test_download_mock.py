"""Test download with mock completed job"""
import requests
import os

print("Testing download with mock completed job...")
print("=" * 60)

# Create a mock output file
os.makedirs('output', exist_ok=True)
mock_output = 'output/test_mock_hinglish.txt'
with open(mock_output, 'w', encoding='utf-8') as f:
    f.write("--- Page 1 ---\n")
    f.write("यह एक परीक्षण फ़ाइल है\n")
    f.write("\n")

print(f"Created mock output file: {mock_output}")

# Manually add a completed job to the server
import hashlib
job_id = hashlib.md5(b"test_mock_job").hexdigest()

# Make a request to simulate adding the job
# Since we can't directly access the server's memory, 
# let's test by uploading first and then manually completing it

# Upload a file
test_file = "books/test_download.txt"
with open(test_file, 'rb') as f:
    files = {'file': (os.path.basename(test_file), f)}
    response = requests.post("http://localhost:5000/hinglish/upload", files=files)

data = response.json()
if data.get('success'):
    job_id = data['job_id']
    print(f"Job created with ID: {job_id}")
    
    # Now let's check the download endpoint directly
    # It should fail because translation isn't complete
    print(f"\nTrying to download before completion...")
    response = requests.get(f"http://localhost:5000/hinglish/download/{job_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 400:
        try:
            error_data = response.json()
            print(f"✅ Correctly blocked: {error_data.get('error')}")
        except:
            print(f"Response: {response.text[:200]}")
    else:
        print(f"Response: {response.text[:200]}")

print("=" * 60)
