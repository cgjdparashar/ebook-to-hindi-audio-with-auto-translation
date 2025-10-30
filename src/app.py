"""
Flask Web Application
Main server for AI Audiobook Translator
"""
from flask import Flask, render_template, request, jsonify, send_file
import os
import sys
from werkzeug.utils import secure_filename

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline import ProcessingPipeline
from hinglish_translator import HinglishTranslator, ChunkedTranslationProcessor
from parser import BookParser
import hashlib
import threading


app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')

# Configuration
# Use /tmp on Render (ephemeral filesystem) or local directories
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/tmp/books') if os.environ.get('RENDER') else 'books'
CACHE_FOLDER = os.environ.get('CACHE_FOLDER', '/tmp/cache') if os.environ.get('RENDER') else 'cache'
OUTPUT_FOLDER = os.environ.get('OUTPUT_FOLDER', '/tmp/output') if os.environ.get('RENDER') else 'output'
ALLOWED_EXTENSIONS = {'pdf', 'epub', 'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CACHE_FOLDER'] = CACHE_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Global pipeline instance (for audiobook feature - Page 1)
current_pipeline = None

# Global instances for Hinglish translation (Page 2)
hinglish_translator = None
hinglish_processor = None
hinglish_jobs = {}  # Track translation jobs
hinglish_jobs_lock = threading.Lock()


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Home page with upload interface"""
    return render_template('index.html')


@app.route('/books', methods=['GET'])
def list_books():
    """List all books in the books folder"""
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        books = []
        
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(filepath) and allowed_file(filename):
                file_size = os.path.getsize(filepath)
                file_ext = filename.rsplit('.', 1)[1].lower()
                books.append({
                    'filename': filename,
                    'size': file_size,
                    'size_kb': round(file_size / 1024, 2),
                    'type': file_ext.upper()
                })
        
        return jsonify({'books': books})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/books/<filename>', methods=['DELETE'])
def delete_book(filename):
    """Delete a book from the books folder"""
    try:
        # Security: prevent directory traversal
        filename = secure_filename(filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Book not found'}), 404
        
        os.remove(filepath)
        return jsonify({'success': True, 'message': f'Deleted {filename}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/books/<filename>/load', methods=['POST'])
def load_book(filename):
    """Load a book from the bookshelf"""
    global current_pipeline
    
    try:
        # Security: prevent directory traversal
        filename = secure_filename(filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Book not found'}), 404
        
        if not allowed_file(filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Initialize processing pipeline
        current_pipeline = ProcessingPipeline(filepath, app.config['CACHE_FOLDER'])
        
        return jsonify({
            'success': True,
            'filename': filename,
            'total_pages': current_pipeline.total_pages
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    global current_pipeline
    
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only PDF, EPUB, and TXT allowed'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Initialize processing pipeline
        current_pipeline = ProcessingPipeline(filepath, app.config['CACHE_FOLDER'])
        
        return jsonify({
            'success': True,
            'filename': filename,
            'total_pages': current_pipeline.total_pages
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/process/<int:page_num>', methods=['GET'])
def process_page(page_num):
    """Process a specific page"""
    global current_pipeline
    
    try:
        if not current_pipeline:
            return jsonify({'error': 'No book uploaded'}), 400
        
        print(f"\n{'='*60}")
        print(f"Processing request for page {page_num}")
        print(f"{'='*60}")
        
        # Get page with prefetch
        page_data = current_pipeline.get_page_with_prefetch(page_num)
        
        print(f"Page data status: {page_data.get('status')}")
        
        if page_data['status'] == 'error':
            error_msg = page_data.get('error', 'Processing failed')
            print(f"ERROR: {error_msg}")
            return jsonify({'error': error_msg}), 500
        
        print(f"Page processed successfully!")
        return jsonify({
            'success': True,
            'page_num': page_data['page_num'],
            'translated_text': page_data['translated_text'],
            'audio_url': f'/audio/{page_num}'
        })
        
    except Exception as e:
        import traceback
        print(f"\nEXCEPTION in process_page:")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route('/audio/<int:page_num>', methods=['GET'])
def get_audio(page_num):
    """Serve audio file for a specific page"""
    global current_pipeline
    
    try:
        print(f"\n[AUDIO] Request for page {page_num}", flush=True)
        
        if not current_pipeline:
            print(f"[AUDIO] ERROR: No pipeline", flush=True)
            return jsonify({'error': 'No book uploaded'}), 400
        
        print(f"[AUDIO] Getting page data...", flush=True)
        page_data = current_pipeline.get_page(page_num)
        print(f"[AUDIO] Page data status: {page_data.get('status')}", flush=True)
        
        if page_data['status'] == 'error':
            print(f"[AUDIO] ERROR: Page status is error", flush=True)
            return jsonify({'error': 'Audio not available'}), 404
        
        # Get translated text to retrieve audio from memory
        translated_text = page_data.get('translated_text', '')
        if not translated_text:
            print(f"[AUDIO] ERROR: No translated text", flush=True)
            return jsonify({'error': 'No translated text available'}), 404
        
        print(f"[AUDIO] Getting audio data from memory...", flush=True)
        
        # Try to get audio from memory cache
        audio_data = current_pipeline.tts.get_audio_data(translated_text)
        
        if audio_data:
            print(f"[AUDIO] Serving audio from memory cache", flush=True)
            return send_file(
                audio_data,
                mimetype='audio/mpeg',
                as_attachment=False,
                download_name=f'page_{page_num}.mp3'
            )
        
        # Fallback to disk if memory cache misses (for local dev)
        audio_path = page_data['audio_path']
        print(f"[AUDIO] Audio path: {audio_path}", flush=True)
        
        # Convert to absolute path if it's relative
        if not os.path.isabs(audio_path):
            audio_path = os.path.abspath(audio_path)
            print(f"[AUDIO] Converted to absolute path: {audio_path}", flush=True)
        
        print(f"[AUDIO] File exists: {os.path.exists(audio_path)}", flush=True)
        
        if os.path.exists(audio_path):
            print(f"[AUDIO] Serving audio from disk", flush=True)
            return send_file(audio_path, mimetype='audio/mpeg')
        
        print(f"[AUDIO] ERROR: Audio not found in memory or disk", flush=True)
        return jsonify({'error': 'Audio file not found'}), 404
        
    except Exception as e:
        import traceback
        print(f"\n[AUDIO] EXCEPTION:", flush=True)
        print(traceback.format_exc(), flush=True)
        return jsonify({'error': str(e)}), 500


@app.route('/status', methods=['GET'])
def get_status():
    """Get processing status"""
    global current_pipeline
    
    if not current_pipeline:
        return jsonify({'error': 'No book uploaded'}), 400
    
    status = current_pipeline.get_status()
    return jsonify(status)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})


# ============================================================================
# HINGLISH TRANSLATION ROUTES (PAGE 2)
# Separate page for English to Hinglish translation with chunked processing
# ============================================================================

@app.route('/hinglish')
def hinglish_page():
    """Hinglish translation page"""
    return render_template('hinglish.html')


@app.route('/hinglish/upload', methods=['POST'])
def hinglish_upload():
    """Handle file upload for Hinglish translation"""
    global hinglish_translator, hinglish_processor
    
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only PDF, EPUB, and TXT allowed'}), 400
        
        # Initialize translator and processor if needed
        if not hinglish_translator:
            hinglish_translator = HinglishTranslator(app.config['CACHE_FOLDER'])
        
        if not hinglish_processor:
            hinglish_processor = ChunkedTranslationProcessor(
                hinglish_translator, 
                app.config['OUTPUT_FOLDER']
            )
        
        # Save file
        filename = secure_filename(file.filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Calculate file content hash BEFORE saving to detect if it's truly a new file
        file.seek(0)
        file_content = file.read()
        content_hash = hashlib.md5(file_content).hexdigest()
        file.seek(0)  # Reset for saving
        
        # Save the file
        file.save(filepath)
        
        # Create job ID based on filename AND content hash
        # This ensures different content = different job, even with same filename
        job_id = hashlib.md5(f"{filename}_{content_hash}".encode()).hexdigest()
        
        # Parse file to get total pages
        parser = BookParser(filepath)
        total_pages = parser.get_total_pages()
        
        # Check if there's existing progress
        progress = hinglish_processor._load_progress(job_id)
        resume_from = 0
        if progress:
            resume_from = progress.get('last_completed_page', -1) + 1
        
        # Store job info
        with hinglish_jobs_lock:
            hinglish_jobs[job_id] = {
                'filename': filename,
                'filepath': filepath,
                'total_pages': total_pages,
                'status': 'uploaded',
                'completed': resume_from,
                'parser': parser
            }
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'filename': filename,
            'total_pages': total_pages,
            'resume_from': resume_from
        })
        
    except Exception as e:
        import traceback
        print(f"Hinglish upload error: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to upload file. Please try again.'}), 500


@app.route('/hinglish/translate', methods=['POST'])
def hinglish_translate():
    """Start Hinglish translation for a job"""
    global hinglish_processor
    
    try:
        # Handle malformed JSON
        data = request.get_json(force=False, silent=True)
        if data is None:
            return jsonify({'error': 'Invalid JSON data'}), 400
        
        job_id = data.get('job_id')
        
        if not job_id:
            return jsonify({'error': 'No job ID provided'}), 400
        
        with hinglish_jobs_lock:
            if job_id not in hinglish_jobs:
                return jsonify({'error': 'Job not found'}), 404
            
            job = hinglish_jobs[job_id]
            
            if job['status'] == 'processing':
                return jsonify({'error': 'Job already in progress'}), 400
            
            job['status'] = 'processing'
        
        # Start translation in background thread
        def translation_worker(job_id, parser):
            def progress_callback(page_num, total, status):
                with hinglish_jobs_lock:
                    if job_id in hinglish_jobs:
                        hinglish_jobs[job_id]['completed'] = page_num
            
            try:
                result = hinglish_processor.process_pages(
                    parser, 
                    job_id,
                    callback=progress_callback
                )
                
                with hinglish_jobs_lock:
                    if job_id in hinglish_jobs:
                        hinglish_jobs[job_id]['status'] = result['status']
                        hinglish_jobs[job_id]['output_file'] = result.get('output_file')
                        if result['status'] == 'error':
                            hinglish_jobs[job_id]['error'] = result.get('error')
                
            except Exception as e:
                with hinglish_jobs_lock:
                    if job_id in hinglish_jobs:
                        hinglish_jobs[job_id]['status'] = 'error'
                        hinglish_jobs[job_id]['error'] = str(e)
        
        # Start worker thread
        thread = threading.Thread(
            target=translation_worker, 
            args=(job_id, job['parser'])
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True, 'message': 'Translation started'})
        
    except Exception as e:
        import traceback
        print(f"Hinglish translate error: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to start translation. Please try again.'}), 500


@app.route('/hinglish/progress/<job_id>', methods=['GET'])
def hinglish_progress(job_id):
    """Get translation progress for a job"""
    try:
        with hinglish_jobs_lock:
            if job_id not in hinglish_jobs:
                return jsonify({'error': 'Job not found'}), 404
            
            job = hinglish_jobs[job_id]
            
            # Return flat structure with required fields
            return jsonify({
                'success': True,
                'completed': job.get('completed', 0),
                'total': job['total_pages'],
                'status': job['status'],
                'error': job.get('error')
            })
    except Exception as e:
        import traceback
        print(f"Hinglish progress error: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to retrieve progress. Please try again.'}), 500


@app.route('/hinglish/download/<job_id>', methods=['GET'])
def hinglish_download(job_id):
    """Download translated Hinglish file"""
    try:
        with hinglish_jobs_lock:
            if job_id not in hinglish_jobs:
                print(f"[DOWNLOAD] Job {job_id} not found in jobs")
                return jsonify({'error': 'Job not found'}), 404
            
            job = hinglish_jobs[job_id]
            print(f"[DOWNLOAD] Job status: {job['status']}")
            
            if job['status'] != 'completed':
                print(f"[DOWNLOAD] Job not completed, status: {job['status']}")
                return jsonify({'error': 'Translation not completed'}), 400
            
            output_file = job.get('output_file')
            print(f"[DOWNLOAD] Output file: {output_file}")
            
            if not output_file:
                print(f"[DOWNLOAD] No output file in job data")
                return jsonify({'error': 'Output file not found'}), 404
            
            if not os.path.exists(output_file):
                print(f"[DOWNLOAD] Output file does not exist on disk: {output_file}")
                return jsonify({'error': 'Output file not found'}), 404
            
            # Send file as download
            original_filename = job['filename']
            download_name = f"{os.path.splitext(original_filename)[0]}_hinglish.txt"
            
            # Ensure absolute path
            if not os.path.isabs(output_file):
                output_file = os.path.abspath(output_file)
            
            print(f"[DOWNLOAD] Sending file: {output_file} as {download_name}")
            print(f"[DOWNLOAD] File size: {os.path.getsize(output_file)} bytes")
            
            return send_file(
                output_file,
                as_attachment=True,
                download_name=download_name,
                mimetype='text/plain'
            )
            
    except Exception as e:
        import traceback
        print(f"Hinglish download error: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to download file. Please try again.'}), 500


if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(CACHE_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    # Get port from environment variable (Render sets this)
    port = int(os.environ.get('PORT', 5000))
    
    print("=" * 60)
    print("AI-Powered Audiobook Translator")
    print("=" * 60)
    print(f"Server starting on port {port}")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Cache folder: {CACHE_FOLDER}")
    print(f"Environment: {'Render' if os.environ.get('RENDER') else 'Local'}")
    print("=" * 60)
    
    app.run(debug=False, host='0.0.0.0', port=port, use_reloader=False)
