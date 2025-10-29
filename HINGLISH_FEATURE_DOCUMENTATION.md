# Hinglish Translation Feature Documentation

## Overview
This document describes the new **English to Hinglish Translation** feature (Page 2) added to the AI Audiobook Translator application.

## Feature Summary
A completely separate page that translates large English documents (PDF, EPUB, TXT) to Hindi (Devanagari script), supporting files with 5000+ pages. The feature includes:

- ✅ Chunked processing for large files
- ✅ Automatic resume on network failures  
- ✅ Progress tracking with real-time updates
- ✅ Download as .txt file (no on-page display)
- ✅ Completely separate from existing audiobook feature

## User Interface

### Page 1: Audiobook Translator (Existing - Unchanged)
- URL: `http://localhost:5000/`
- Function: Convert books to Hindi audiobooks with TTS
- Features: Upload → Translate → Generate Audio → Play
- Navigation: Link to "Text Translator" in top-right corner

![Page 1 - Audiobook](https://github.com/user-attachments/assets/e0282884-5b82-4e3f-b0a3-f4a144c355aa)

### Page 2: Hinglish Translator (New)
- URL: `http://localhost:5000/hinglish`
- Function: Translate large documents to Hindi text
- Features: Upload → Translate → Download as .txt
- Navigation: Link to "Audiobook Translator" in top-right corner

![Page 2 - Hinglish Translation](https://github.com/user-attachments/assets/70a6d476-0169-405a-8dd7-c889578236e0)

## Technical Architecture

### File Structure
```
src/
├── app.py                    # Flask routes (both pages)
├── hinglish_translator.py    # Hinglish translation service
├── translator.py             # Existing Hindi TTS translator
├── pipeline.py               # Existing audiobook pipeline
└── parser.py                 # Shared PDF/EPUB/TXT parser

templates/
├── index.html                # Page 1 - Audiobook (modified: added nav link)
└── hinglish.html             # Page 2 - Hinglish Translation (new)

output/                       # Hinglish translation outputs
```

### New Flask Routes

#### `/hinglish` (GET)
- Renders the Hinglish translation page
- Template: `templates/hinglish.html`

#### `/hinglish/upload` (POST)
- Accepts file upload (PDF, EPUB, TXT)
- Creates unique job ID
- Checks for existing progress (resume capability)
- Returns: `{success, job_id, total_pages, resume_from}`

#### `/hinglish/translate` (POST)
- Starts translation in background thread
- Request body: `{job_id}`
- Processes pages with chunking
- Returns: `{success, message}`

#### `/hinglish/progress/<job_id>` (GET)
- Returns current translation progress
- Response: `{success, progress: {total, completed, status, error}}`

#### `/hinglish/download/<job_id>` (GET)
- Downloads completed translation as .txt file
- Filename: `{original_name}_hinglish.txt`

### Key Components

#### 1. HinglishTranslator Class
Located in `src/hinglish_translator.py`

**Features:**
- Translates English to Hindi using Google Translate API
- Content-based caching (MD5 hash keys)
- Automatic chunking for large texts (4000 chars max per chunk)
- Exponential backoff retry logic
- Separate cache file: `cache/hinglish_translations.json`

**Methods:**
```python
translate_to_hinglish(text, retry_count=3)  # Single translation
translate_chunk(text, max_chunk_size=4000)  # Chunked translation
clear_cache()                                # Clear translation cache
```

#### 2. ChunkedTranslationProcessor Class
Located in `src/hinglish_translator.py`

**Features:**
- Processes books page-by-page with progress tracking
- Saves progress to JSON files after each page
- Auto-resumes from last completed page on errors
- Background thread processing
- Progress callback support

**Methods:**
```python
process_pages(parser, job_id, start_page=0, callback=None)
```

**Progress File Format:**
```json
{
  "job_id": "abc123...",
  "total_pages": 700,
  "last_completed_page": 100,
  "output_file": "output/abc123_hinglish.txt",
  "status": "in_progress"
}
```

### Error Handling & Resume Capability

#### Scenario 1: Network Error During Translation
1. User uploads 700-page file
2. Translation starts, processes pages 1-100
3. Network error occurs on page 101
4. Progress saved: `last_completed_page: 100`
5. User refreshes page or re-uploads same file
6. System detects existing progress
7. Resumes from page 101

#### Scenario 2: Server Restart
1. Translation in progress (completed 300/700 pages)
2. Server crashes or restarts
3. User returns to page, re-uploads file
4. System loads progress from `{job_id}_progress.json`
5. Shows: "Resuming from page 301"
6. Continues translation without re-processing

### Performance Optimizations

1. **Chunking Strategy**
   - Text split into 4000-character chunks
   - Prevents API timeout errors
   - Optimized for Google Translate limits

2. **Progress Persistence**
   - Progress saved after EACH page
   - Prevents data loss on errors
   - Enables instant resume

3. **Background Processing**
   - Translation runs in daemon thread
   - Frontend polls progress every 2 seconds
   - Non-blocking UI

4. **Caching**
   - MD5-based content caching
   - Prevents re-translation of duplicate text
   - Shared across jobs

## Usage Examples

### Basic Workflow
1. Navigate to `http://localhost:5000/hinglish`
2. Upload a document (PDF/EPUB/TXT)
3. Wait for translation to complete (progress bar updates)
4. Click "Download Hinglish Translation" button
5. Receive `.txt` file with Hindi translation

### Handling Large Files
```
File: 5000-page book
Pages processed: 1 → 2 → 3 → ... → 5000
Progress updates: Every 2 seconds
Output file: Updated after each page (append mode)
Resume: Automatic if interrupted
```

### Testing Commands
```bash
# Start server
python src/app.py

# Run comprehensive tests
python test_hinglish_feature.py

# Manual test workflow
# 1. Open http://localhost:5000/hinglish
# 2. Upload books/test_hinglish_story.txt
# 3. Wait for completion
# 4. Download result
```

## Output Format

### Downloaded File Structure
```
--- Page 1 ---
[Hindi translation of page 1 in Devanagari script]

--- Page 2 ---
[Hindi translation of page 2 in Devanagari script]

...
```

**Note:** The current implementation translates to Hindi in Devanagari script. For true "Hinglish" (Roman script), additional transliteration would be needed using libraries like `indic-transliteration`.

## Comparison: Page 1 vs Page 2

| Feature | Page 1 (Audiobook) | Page 2 (Hinglish) |
|---------|-------------------|-------------------|
| **Purpose** | Listen to Hindi audiobooks | Download Hindi text |
| **Output** | MP3 audio files | TXT file |
| **Display** | Shows translated text + audio player | No display (download only) |
| **Processing** | Page-by-page with prefetch | Batch processing all pages |
| **Resume** | Not needed (on-demand) | Auto-resume on errors |
| **Navigation** | Previous/Next page buttons | N/A (full file at once) |
| **Large files** | Works (processes on request) | Optimized (chunked + resume) |

## Configuration

### Environment Variables
```bash
OUTPUT_FOLDER=/tmp/output  # On Render (ephemeral)
OUTPUT_FOLDER=output       # Local development (persistent)
```

### Flask Config
```python
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
```

## Testing Status

### Automated Tests (test_hinglish_feature.py)
- ✅ Server running
- ✅ Hinglish page loads
- ✅ Existing audiobook feature untouched  
- ✅ File upload working
- ✅ Translation start working
- ⚠️ Translation completion (requires internet for Google Translate API)
- ⚠️ Download (requires completed translation)

### Manual Testing Checklist
- [ ] Upload small file (1-10 pages)
- [ ] Upload large file (500+ pages)
- [ ] Test resume after interruption
- [ ] Test concurrent jobs
- [ ] Test error handling
- [ ] Test on mobile devices
- [ ] Test with Brida file (as per requirements)

## Known Limitations

1. **Internet Dependency**
   - Requires active internet for Google Translate API
   - Sandboxed environments may not work

2. **Romanization**
   - Currently outputs Devanagari script (Hindi)
   - True Hinglish (Roman script) requires additional transliteration

3. **Rate Limiting**
   - Google Translate may rate-limit on large files
   - Exponential backoff helps but may slow down processing

4. **Memory Usage**
   - Large files kept in memory during processing
   - May need optimization for 10,000+ page files

## Future Enhancements

1. **True Hinglish (Roman Script)**
   - Add transliteration library (e.g., `indic-transliteration`)
   - Convert Devanagari to Roman script
   - Example: "नमस्ते" → "namaste"

2. **Better Progress UI**
   - Show estimated time remaining
   - Display current page being processed
   - Show error details with retry button

3. **Batch Processing**
   - Queue multiple files
   - Process in background with email notification

4. **Format Options**
   - Export as PDF with formatting
   - Support for DOCX output
   - Preserve original formatting

## Security Considerations

1. **File Upload Validation**
   - Extension whitelist: PDF, EPUB, TXT only
   - Size limit: 50MB max
   - Filename sanitization via `secure_filename()`

2. **Job ID Generation**
   - MD5 hash of filename + timestamp
   - Prevents predictable job IDs
   - Isolated per-job progress files

3. **Output File Access**
   - Job ID required for download
   - No directory traversal
   - Files served via Flask's `send_file()`

## Maintenance

### Clearing Caches
```python
# Hinglish translation cache
rm cache/hinglish_translations.json

# Output files
rm -rf output/

# All caches (including audiobook)
rm -rf cache/
rm -rf output/
```

### Monitoring Logs
```bash
# Server logs show translation progress
python src/app.py

# Look for:
# - "Translating to Hinglish (length: X, attempt: Y)"
# - "Completed page X/Y"
# - "Translation failed after N attempts: ..."
```

## Support & Troubleshooting

### Common Issues

**Issue: Translation fails immediately**
- Check internet connection
- Verify Google Translate API is accessible
- Check server logs for SSL/certificate errors

**Issue: Progress stuck at 0%**
- Check if translation thread started (server logs)
- Verify job ID is correct
- Check for errors in progress JSON file

**Issue: Download button not appearing**
- Wait for translation to complete (status = 'completed')
- Check browser console for errors
- Verify progress polling is working

**Issue: Resume not working**
- Check if progress JSON file exists in output folder
- Verify job ID matches (upload same file with same name)
- Check file timestamps in job ID generation

## Credits
- Translation: Google Translate API via `deep-translator`
- File Parsing: Shared with existing audiobook feature
- UI: Bootstrap-inspired custom CSS
- Architecture: Flask + Threading for async processing
