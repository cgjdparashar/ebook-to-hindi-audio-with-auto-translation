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


app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')

# Configuration
UPLOAD_FOLDER = 'books'
CACHE_FOLDER = 'cache'
ALLOWED_EXTENSIONS = {'pdf', 'epub'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CACHE_FOLDER'] = CACHE_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Global pipeline instance
current_pipeline = None


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Home page with upload interface"""
    return render_template('index.html')


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
            return jsonify({'error': 'Invalid file type. Only PDF and EPUB allowed'}), 400
        
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


@app.route('/books', methods=['GET'])
def list_books():
    """List available books in books folder"""
    try:
        books = []
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            for filename in os.listdir(app.config['UPLOAD_FOLDER']):
                if allowed_file(filename):
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    books.append({
                        'filename': filename,
                        'size': os.path.getsize(filepath)
                    })
        return jsonify({'books': books})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(CACHE_FOLDER, exist_ok=True)
    
    print("=" * 60)
    print("AI-Powered Audiobook Translator")
    print("=" * 60)
    print(f"Server starting at http://localhost:5000")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Cache folder: {CACHE_FOLDER}")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
