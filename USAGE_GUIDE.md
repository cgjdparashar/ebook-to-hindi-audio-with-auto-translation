# Quick Usage Guide - New Features

## 🎉 What's New?

### 1. Text File Support
You can now upload `.txt` files in addition to PDF and EPUB!

### 2. Auto-Play
Audio automatically starts playing when a page loads - no need to click play!

### 3. Auto-Advance
When audio finishes, the app automatically moves to the next page and starts playing!

## 🚀 How to Use

### Starting the App
```bash
python src/app.py
```
Then open http://localhost:5000 in your browser.

### Uploading Files
1. **Drag & Drop** or **Click** the upload area
2. Select your file:
   - `.pdf` - PDF documents
   - `.epub` - EPUB ebooks
   - `.txt` - Plain text files (NEW!)
3. Wait for upload to complete

### Listening Experience

#### **Auto-Play** (Automatic)
- Upload completes → First page loads → Audio starts playing immediately
- No need to press play button!

#### **Auto-Advance** (Automatic)
- Page 1 audio finishes → Page 2 loads automatically → Audio starts
- Page 2 audio finishes → Page 3 loads automatically → Audio starts
- Continues until the last page
- Creates a seamless, hands-free listening experience!

### Manual Controls (Still Available)
- **Play/Pause**: Click the ▶️/⏸️ button
- **Previous**: Click ⏮️ to go back
- **Next**: Click ⏭️ to skip ahead
- **Volume**: Adjust the slider

## 📝 Text File Tips

### How Text Files are Split into Pages
- Text is automatically divided into pages of ~500 words
- Splits happen at paragraph boundaries (double line breaks)
- Ensures each audio segment is a reasonable length

### Best Practices for Text Files
- Use double line breaks (`\n\n`) between paragraphs
- Keep paragraphs reasonably sized (50-200 words)
- UTF-8 encoding recommended
- Works with any language (will translate to Hindi)

## 🧪 Testing the Features

### Test Auto-Play
1. Upload `books/test_story.txt` (provided)
2. Watch as the page loads
3. Audio should start playing automatically within 2-3 seconds
4. ✅ If you hear audio without clicking play, it's working!

### Test Auto-Advance
1. Upload a multi-page file (PDF or TXT with multiple pages)
2. Let the first page audio play completely
3. Wait for it to finish
4. Watch the page number change automatically
5. Second page audio should start playing
6. ✅ If it advances without clicking next, it's working!

### Test Text Files
1. Upload `books/test_story.txt`
2. Check that it shows "1 page" (or more depending on content)
3. Verify Hindi translation appears
4. Verify audio plays in Hindi
5. ✅ If all work, text file support is working!

## 🎯 Quick Test Checklist

- [ ] Server starts at http://localhost:5000
- [ ] Can upload `.txt` file
- [ ] Can upload `.pdf` file  
- [ ] Can upload `.epub` file
- [ ] Audio auto-plays on page load
- [ ] Audio auto-advances to next page when finished
- [ ] Manual controls still work (play, pause, next, prev)
- [ ] Translation to Hindi works
- [ ] Audio generation works

## 🐛 Troubleshooting

### Audio doesn't auto-play?
- Check browser console for errors (F12)
- Some browsers block autoplay - look for a permission prompt
- Click anywhere on the page first to enable autoplay

### Auto-advance not working?
- Let the audio play completely to the end
- Check that you're not on the last page
- Verify in browser console that `handleAudioEnded` event fires

### Text file upload fails?
- Check file has `.txt` extension
- Verify file is UTF-8 encoded
- Make sure file is not empty
- Check file size (max 50MB)

### Processing takes too long?
- First page of each file needs translation and audio generation
- Subsequent pages are prefetched in background
- Text files with very long content may take longer
- Wait at least 30-60 seconds for first page

## 📊 Performance Notes

- **First Page**: Takes 10-30 seconds (translation + audio generation)
- **Subsequent Pages**: Much faster (prefetched while current page plays)
- **Caching**: Translations and audio are cached for reuse
- **Background Processing**: Next 3 pages are processed in advance

## 🎓 Example Workflow

```
1. Start server: python src/app.py
2. Open browser: http://localhost:5000
3. Upload: books/test_story.txt
4. Watch: File uploads → Processing starts
5. Wait: ~15 seconds for translation + audio
6. Enjoy: Audio auto-plays in Hindi
7. Relax: Pages auto-advance when audio ends
8. Listen: Hands-free audiobook experience!
```

## ✨ Benefits

- **Hands-Free**: No need to click next after each page
- **Seamless**: Continuous listening experience
- **Flexible**: Works with PDF, EPUB, and TXT files
- **Smart**: Automatic pagination for text files
- **Fast**: Background prefetching keeps audio ready

## 📚 Sample Files

Included test files:
- `books/test_story.txt` - Sample text file (9 paragraphs)
- `books/The Alchemist mini.pdf` - Sample PDF (7 pages)

Create your own:
- Any `.txt` file with English content
- Any PDF or EPUB book in English
- Content will be translated to Hindi automatically

---

**Enjoy your automated audiobook experience! 🎧**
