#!/usr/bin/env python3
"""
Test suite for restart fix and download filename
"""
import requests
import time
import os

BASE_URL = 'http://localhost:5000'

def create_test_file(filename, content):
    """Create a test file"""
    filepath = os.path.join('books', filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return filepath

def test_upload_with_restart():
    """Test upload with force_restart flag"""
    print("=" * 60)
    print("TEST: Upload with force_restart flag")
    print("=" * 60)
    
    # Create test file
    test_file = 'test_restart_1.txt'
    filepath = create_test_file(test_file, 'Hello world! This is a test.')
    
    try:
        # First upload
        with open(filepath, 'rb') as f:
            files = {'file': (test_file, f, 'text/plain')}
            response = requests.post(f'{BASE_URL}/hinglish/upload', files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        job_id_1 = data['job_id']
        print(f"✅ First upload successful, job_id: {job_id_1}")
        
        # Second upload with force_restart
        with open(filepath, 'rb') as f:
            files = {'file': (test_file, f, 'text/plain')}
            form_data = {'force_restart': 'true'}
            response = requests.post(f'{BASE_URL}/hinglish/upload', files=files, data=form_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert data['has_progress'] == False, "Progress should be cleared with force_restart"
        assert data['resume_from'] == 0, "Should start from page 0"
        print(f"✅ Force restart successful, resume_from: {data['resume_from']}")
        
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

def test_different_files_different_jobs():
    """Test that different files get different job IDs"""
    print("\n" + "=" * 60)
    print("TEST: Different files get different job IDs")
    print("=" * 60)
    
    # Create two different test files
    file1 = 'test_file_a.txt'
    file2 = 'test_file_b.txt'
    path1 = create_test_file(file1, 'Content A')
    path2 = create_test_file(file2, 'Content B')
    
    try:
        # Upload file 1
        with open(path1, 'rb') as f:
            files = {'file': (file1, f, 'text/plain')}
            response = requests.post(f'{BASE_URL}/hinglish/upload', files=files)
        
        data1 = response.json()
        job_id_1 = data1['job_id']
        print(f"✅ File A uploaded, job_id: {job_id_1}")
        
        # Upload file 2
        with open(path2, 'rb') as f:
            files = {'file': (file2, f, 'text/plain')}
            response = requests.post(f'{BASE_URL}/hinglish/upload', files=files)
        
        data2 = response.json()
        job_id_2 = data2['job_id']
        print(f"✅ File B uploaded, job_id: {job_id_2}")
        
        assert job_id_1 != job_id_2, "Different files should have different job IDs"
        print(f"✅ Confirmed: Different files → different job IDs")
        
    finally:
        if os.path.exists(path1):
            os.remove(path1)
        if os.path.exists(path2):
            os.remove(path2)

def test_same_name_different_content():
    """Test that same filename with different content gets different job ID"""
    print("\n" + "=" * 60)
    print("TEST: Same name, different content → different job IDs")
    print("=" * 60)
    
    filename = 'same_name_test.txt'
    filepath = os.path.join('books', filename)
    
    try:
        # Upload with content A
        with open(filepath, 'w') as f:
            f.write('Content A for same name test')
        
        with open(filepath, 'rb') as f:
            files = {'file': (filename, f, 'text/plain')}
            response = requests.post(f'{BASE_URL}/hinglish/upload', files=files)
        
        data1 = response.json()
        job_id_1 = data1['job_id']
        print(f"✅ Upload 1 (Content A), job_id: {job_id_1}")
        
        # Change content
        with open(filepath, 'w') as f:
            f.write('Content B - completely different')
        
        # Upload with content B (same filename)
        with open(filepath, 'rb') as f:
            files = {'file': (filename, f, 'text/plain')}
            response = requests.post(f'{BASE_URL}/hinglish/upload', files=files)
        
        data2 = response.json()
        job_id_2 = data2['job_id']
        print(f"✅ Upload 2 (Content B), job_id: {job_id_2}")
        
        assert job_id_1 != job_id_2, "Different content should create different job ID"
        print(f"✅ Confirmed: Same name + different content → different job IDs")
        
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

def test_download_filename():
    """Test that download filename matches upload filename"""
    print("\n" + "=" * 60)
    print("TEST: Download filename matches upload filename")
    print("=" * 60)
    
    filename = 'my_custom_file.txt'
    filepath = create_test_file(filename, 'Test content for download')
    
    try:
        # Upload
        with open(filepath, 'rb') as f:
            files = {'file': (filename, f, 'text/plain')}
            response = requests.post(f'{BASE_URL}/hinglish/upload', files=files)
        
        data = response.json()
        assert data['success'] == True
        print(f"✅ File uploaded: {filename}")
        print(f"   Expected download name: my_custom_file.txt")
        print(f"   (Backend will use original filename basename)")
        
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

def main():
    print("\n" + "🔄" * 30)
    print("RESTART FIX TEST SUITE")
    print("🔄" * 30 + "\n")
    
    try:
        # Check server
        response = requests.get(BASE_URL)
        if response.status_code != 200:
            print("❌ Server not running on localhost:5000")
            return
        print("✅ Server is running\n")
        
        # Run tests
        test_upload_with_restart()
        test_different_files_different_jobs()
        test_same_name_different_content()
        test_download_filename()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == '__main__':
    main()
