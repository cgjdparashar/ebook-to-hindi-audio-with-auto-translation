# 🎧 AI-Powered Audiobook Translator

Convert PDF, EPUB, and TXT files into Hindi audiobooks with real-time translation and streaming playback.

**🌐 Live Demo:** https://ebook-to-hindi-audio-with-auto.onrender.com/

## ✨ Features

- 📚 **Multi-format Support**: PDF, EPUB, and TXT files
- 📄 **Smart TXT Pagination**: Large text files automatically split into 250-word pages for fast processing
- 🌐 **English to Hindi Translation**: Automatic page-by-page translation
- 🎵 **Text-to-Speech**: Convert translated text to clear Hindi audio
- ▶️ **Auto-Play**: Audio starts automatically when page loads
- ⏭️ **Auto-Advance**: Automatically moves to next page when audio ends
- ⚡ **Playback Speed Control**: Adjust reading speed from 0.5x to 2.0x
- 📚 **Bookshelf Management**: Browse, load, and delete books from library
- 🔄 **Async Processing**: Background preparation of upcoming pages (3 pages ahead)
- 🎨 **Modern UI**: Beautiful gradient purple theme with smooth animations
- 📱 **Mobile-Ready**: Full iOS Safari support with touch optimizations
- � **PWA Installable**: Add to home screen for native app experience
- �💾 **Smart Caching**: Resume where you left off with translation & audio caching
- 🙌 **Hands-Free Experience**: Seamless continuous playback across all pages
- ☁️ **Cloud Deployed**: Production-ready on Render.com with auto-deployment

## 🚀 Quick Start

### Live Demo
Visit **https://ebook-to-hindi-audio-with-auto.onrender.com/** to use the app immediately!

**Note:** iOS users - tap the play button on the first page to enable autoplay for subsequent pages.

### Local Development

#### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

#### Installation

1. **Clone the repository**
```bash
git clone https://github.com/vickyparashar/ebook-to-hindi-audio-with-auto-translation.git
cd ebook-to-hindi-audio-with-auto-translation
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python src/app.py
```

4. **Open in browser**
```
http://localhost:5000
```

### Production Deployment (Render)

The app auto-deploys to Render.com from the `feature/auto-play` branch:

1. **Fork/Clone** the repository
2. **Connect to Render** via GitHub integration
3. **Configure** using included `render.yaml`
4. **Deploy** - Render automatically builds and deploys

See `render.yaml` for deployment configuration details.

## 📦 Dependencies

All dependencies are **free and open-source** with **no API keys required**:

- **Flask 3.0.0** - Lightweight web framework
- **Gunicorn 21.2.0** - Production WSGI server (for Render deployment)
- **PyPDF2 3.0.1** - PDF text extraction
- **ebooklib 0.18** - EPUB parsing with BeautifulSoup
- **deep-translator 1.11.4** - Google Translate (free, no API key)
- **gTTS 2.5.4** - Google Text-to-Speech for Hindi audio with retry logic
- **ThreadPoolExecutor** - Asynchronous background processing

## 🎯 How It Works

1. **Upload**: Drag & drop a PDF/EPUB/TXT file or browse to select
2. **Processing**: App extracts text, translates to Hindi, and generates audio
3. **Playback**: Listen immediately while subsequent pages process in background
4. **Navigate**: Use player controls to pause, skip, adjust volume, or change speed
5. **Bookshelf**: Manage your library - load previous books or delete unwanted files

### iOS Safari Users
On iPhone/iPad, tap the play button (▶️) on the first page to enable audio. Subsequent pages will auto-play automatically.

### 📱 Install as Progressive Web App (PWA)
Add the app to your iPhone/iPad home screen for a native-like experience!

**Installation Steps:**
1. Open https://ebook-to-hindi-audio-with-auto.onrender.com/ in **Safari** (not Chrome)
2. Tap the **Share** button (square with arrow pointing up)
3. Scroll down and tap **"Add to Home Screen"**
4. Tap **"Add"** in the top right corner
5. Find the app icon on your home screen with the purple headphone logo

**Benefits:**
- ✨ Full-screen experience (no Safari toolbars)
- 🚀 Launches instantly like a native app
- 📱 Beautiful app icon on home screen
- 💾 Offline caching for faster loading

## 📁 Project Structure

```
ebook-to-hindi-audio-with-auto-translation/
├── books/              # Input PDF/EPUB/TXT files
├── cache/             # Translated text & audio cache
├── src/
│   ├── app.py         # Flask web server with Render support
│   ├── parser.py      # PDF/EPUB/TXT text extraction
│   ├── translator.py  # Translation service with SSL bypass
│   ├── tts.py         # TTS engine with rate limit retry logic
│   └── pipeline.py    # Async processing with prefetching
├── static/
│   ├── css/style.css  # Gradient purple theme with iOS optimizations
│   └── js/app.js      # Player controls with iOS Safari support
├── templates/
│   └── index.html     # Single-page app with bookshelf modal
├── .github/
│   └── copilot-instructions.md  # AI agent development guide
├── render.yaml        # Render.com deployment configuration
├── requirements.txt   # Python dependencies
├── COMPREHENSIVE_TEST_REPORT.md  # 32/32 tests passing
├── atomic-smoke-tests.md         # 80 legacy smoke tests
├── prd.md            # Product requirements document
└── README.md
```

## 🧪 Testing

The project includes comprehensive testing at multiple levels - **ALL PASSING ✅**

**Comprehensive Test Suite:**
- ✅ **Atomic Level** (7 tests): Component-level testing (parsers, translators, TTS)
- ✅ **Minor Level** (15 tests): Feature integration testing
- ✅ **Major Level** (10 tests): End-to-end workflows including iOS Safari

**Total: 32/32 Tests PASSED** 🎉

**Legacy Smoke Tests:**
- ✅ 80 atomic smoke tests using Playwright MCP
- ✅ Covers all features: upload, parsing, translation, TTS, playback, bookshelf, UI/UX

**Production Testing:**
- ✅ Tested on Render.com deployment
- ✅ Verified iOS Safari compatibility (iPhone/iPad)
- ✅ Rate limiting handled with exponential backoff
- ✅ Memory-based audio serving on ephemeral filesystem

See `COMPREHENSIVE_TEST_REPORT.md` and `atomic-smoke-tests.md` for complete test details.

## 🛠️ Development

### Architecture
- **Modular Design**: Separate parsing, translation, TTS, and playback components
- **Async Pipeline**: Process pages 2-3 ahead of current playback for seamless transitions
- **Caching Strategy**: MD5-based caching for translations and audio files
- **Environment-aware**: Auto-detects local vs Render deployment (`RENDER` env var)
- **Rate Limit Handling**: Exponential backoff retry (5→10→20→40→80s) for TTS API
- **iOS Compatibility**: User interaction tracking for Safari autoplay policies

### Key Workflows
- Upload → Parse → Translate → Generate Audio → Stream & Play
- Background prefetch with rate-limit delays (1.5s between pages)
- Smart caching with content-based hashing (MD5)
- Memory-based audio serving on Render's ephemeral filesystem

### Deployment Environments

**Local Development:**
- Uses `books/` and `cache/` directories
- Debug mode with detailed logging
- Port: 5000

**Production (Render):**
- Uses `/tmp/books` and `/tmp/cache` (ephemeral)
- Gunicorn WSGI server (2 workers, 120s timeout)
- Memory-based audio caching via BytesIO
- Auto-deploy from `feature/auto-play` branch
- Port: Dynamic (set by Render via `$PORT`)

See `.github/copilot-instructions.md` for detailed development guidelines and critical implementation patterns.

## 📝 Configuration

No configuration needed! The app works out-of-the-box with:
- **Translation**: deep-translator with Google Translate (free, no API key)
- **TTS**: gTTS for high-quality Hindi audio (free, no API key, with retry logic)
- **Storage**: 
  - Local: `books/` and `cache/` directories
  - Render: `/tmp/books` and `/tmp/cache` (ephemeral filesystem)
- **SSL**: Custom bypass for corporate network environments
- **Rate Limiting**: Automatic exponential backoff on TTS API limits
- **iOS Support**: Automatic detection and autoplay policy compliance

### Environment Variables (Render)
```yaml
RENDER=true              # Auto-detected on Render platform
PORT=10000              # Set by Render dynamically
PYTHON_VERSION=3.11.0   # Specified in render.yaml
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a pull request

## 📄 License

This project is open-source and available under the MIT License.

## ✨ Current Status

**🎉 Production Ready - Deployed & All Features Working!**

**Live URL:** https://ebook-to-hindi-audio-with-auto.onrender.com/

- ✅ PDF/EPUB/TXT parsing with multi-page support (250-word TXT pagination)
- ✅ English → Hindi translation with MD5-based smart caching
- ✅ High-quality Hindi audio generation (gTTS with rate limit retry)
- ✅ Real-time streaming playback with memory-based serving
- ✅ Async prefetching (3 pages ahead with 1.5s delays)
- ✅ Beautiful gradient purple theme with smooth animations
- ✅ Complete playback controls (play/pause, next/prev, volume, speed)
- ✅ Auto-play with iOS Safari compatibility (user interaction tracking)
- ✅ Auto-advance to next page when audio completes (500ms delay)
- ✅ Bookshelf management (browse, load, delete books)
- ✅ Progress tracking with time display
- ✅ Error handling with exponential backoff (5→80s retry delays)
- ✅ Fast performance (<2s page loads, <3s translation)
- ✅ Mobile-ready with iOS touch optimizations
- ✅ Production deployment on Render.com with auto-deploy
- ✅ Comprehensive test coverage (32/32 tests passing)

## 🎯 Future Roadmap

- [ ] Support for more target languages (Spanish, French, etc.)
- [ ] Multiple TTS voice options
- [ ] Batch processing multiple books
- [ ] Export audiobook files for offline listening
- [ ] Cloud storage integration
- [ ] User accounts and preferences

## 🐛 Known Issues & Solutions

**None!** All tests passing. The application is production-ready and deployed.

### Platform-Specific Notes

**iOS Safari (iPhone/iPad):**
- ✅ First page requires manual play button tap (Safari autoplay policy)
- ✅ Subsequent pages auto-play automatically after user interaction
- ✅ Touch optimizations applied (`-webkit-tap-highlight-color: transparent`)

**Render.com Deployment:**
- ✅ Ephemeral filesystem handled (uses `/tmp/` directories)
- ✅ Rate limiting mitigated with exponential backoff retry
- ✅ Memory-based audio serving (no persistent disk required)
- ✅ Gunicorn timeout set to 120s for retry delays

**Recent Improvements:**
- ✅ Smart TXT pagination (250-word max pages for fast processing)
- ✅ Large text files automatically split into manageable chunks
- ✅ Bookshelf feature (manage books from library)
- ✅ iOS Safari full compatibility with autoplay workarounds
- ✅ Render.com production deployment with auto-deploy
- ✅ Rate limit handling with 5-attempt exponential backoff
- ✅ Mobile-responsive design with touch optimizations
- ✅ Streaming mode - on-demand page processing
- ✅ Auto-play and auto-advance for hands-free listening
- ✅ Playback speed control (0.5x to 2.0x)

**Earlier Fixes:**
- ✅ Replaced pyttsx3 with gTTS for cross-platform compatibility
- ✅ Implemented custom SSL bypass for corporate networks
- ✅ Fixed audio file path resolution (relative → absolute)
- ✅ Disabled Flask auto-reloader to prevent state loss
- ✅ Removed Unicode emojis for Windows terminal compatibility

## 📧 Support

For issues and questions:
- **GitHub Issues**: https://github.com/vickyparashar/ebook-to-hindi-audio-with-auto-translation/issues
- **Live Demo**: https://ebook-to-hindi-audio-with-auto.onrender.com/
- **Documentation**: See `.github/copilot-instructions.md` for development details

---

**Note**: This project uses only free, open-source tools requiring no API keys or accounts. Perfect for personal use and deployed on Render's free tier!
