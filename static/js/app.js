// Main application JavaScript
let currentPage = 0;
let totalPages = 0;
let currentFilename = '';
let audioElement = null;
let isIOS = false;
let hasUserInteracted = false;

// DOM Elements
const uploadSection = document.getElementById('upload-section');
const playerSection = document.getElementById('player-section');
const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const uploadStatus = document.getElementById('upload-status');
const errorDisplay = document.getElementById('error-display');

const playPauseBtn = document.getElementById('play-pause-btn');
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');
const volumeSlider = document.getElementById('volume-slider');
const speedSlider = document.getElementById('speed-slider');
const speedValue = document.getElementById('speed-value');

const currentPageSpan = document.getElementById('current-page');
const totalPagesSpan = document.getElementById('total-pages');
const bookTitle = document.getElementById('book-title');
const translatedText = document.getElementById('translated-text');
const progressFill = document.getElementById('progress-fill');
const currentTimeSpan = document.getElementById('current-time');
const totalTimeSpan = document.getElementById('total-time');
const processingStatus = document.getElementById('processing-status');
const processingMessage = document.getElementById('processing-message');

// Bookshelf elements
const bookshelfBtn = document.getElementById('bookshelf-btn');
const bookshelfModal = document.getElementById('bookshelf-modal');
const closeModalBtn = document.getElementById('close-modal');
const booksList = document.getElementById('books-list');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    audioElement = document.getElementById('audio-element');
    
    // Detect iOS
    isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    
    // Configure iOS background audio session
    if (isIOS) {
        setupiOSBackgroundAudio();
    }
    
    setupEventListeners();
    
    // Initialize playback speed - default to 0.8x
    const savedSpeed = localStorage.getItem('playbackSpeed');
    const initialSpeed = savedSpeed ? parseFloat(savedSpeed) : 0.8;
    speedSlider.value = initialSpeed * 100;
    speedValue.textContent = initialSpeed.toFixed(1) + 'x';
    audioElement.playbackRate = initialSpeed;
    
    // Register Service Worker for PWA
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/sw.js')
            .then(registration => {
                console.log('Service Worker registered:', registration.scope);
            })
            .catch(error => {
                console.log('Service Worker registration failed:', error);
            });
    }
    
    console.log('App initialized', isIOS ? '(iOS detected)' : '');
});

// Setup iOS Background Audio Session
function setupiOSBackgroundAudio() {
    console.log('Setting up iOS background audio...');
    
    // Enable background audio playback by preventing iOS from pausing audio
    // when the app goes to background or screen locks
    if (audioElement) {
        // Set audio session for continuous playback
        audioElement.addEventListener('loadstart', () => {
            console.log('iOS: Audio loading, requesting background playback');
            // Request background playback permission
            if (navigator.mediaSession) {
                navigator.mediaSession.setActionHandler('play', () => {
                    console.log('iOS: Media session play');
                    playAudio();
                });
                
                navigator.mediaSession.setActionHandler('pause', () => {
                    console.log('iOS: Media session pause');
                    pauseAudio();
                });
                
                navigator.mediaSession.setActionHandler('previoustrack', () => {
                    console.log('iOS: Media session previous');
                    previousPage();
                });
                
                navigator.mediaSession.setActionHandler('nexttrack', () => {
                    console.log('iOS: Media session next');
                    nextPage();
                });
            }
        });
        
        // Prevent iOS from suspending audio when app goes to background
        audioElement.addEventListener('playing', () => {
            console.log('iOS: Audio playing, maintaining wake lock');
            // Update media session metadata for background controls
            if (navigator.mediaSession && currentFilename) {
                navigator.mediaSession.metadata = new MediaMetadata({
                    title: `Page ${currentPage + 1} of ${totalPages}`,
                    artist: 'AI Audiobook Translator',
                    album: currentFilename,
                    artwork: [
                        { src: '/static/icon-192.svg', sizes: '192x192', type: 'image/svg+xml' },
                        { src: '/static/icon-512.svg', sizes: '512x512', type: 'image/svg+xml' }
                    ]
                });
            }
        });
        
        // Handle visibility change (app going to background/foreground)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                console.log('iOS: App went to background, audio should continue');
                // Keep audio playing in background
                if (!audioElement.paused) {
                    console.log('iOS: Ensuring audio continues in background');
                }
            } else {
                console.log('iOS: App came to foreground');
                // Refresh UI state when app comes back to foreground
                updateProgress();
            }
        });
        
        // Handle page show/hide events (iOS Safari specific)
        window.addEventListener('pageshow', (e) => {
            if (e.persisted) {
                console.log('iOS: Page restored from cache, checking audio state');
                updateProgress();
            }
        });
        
        window.addEventListener('pagehide', () => {
            console.log('iOS: Page hiding, maintaining audio session');
        });
    }
}

// Setup Event Listeners
function setupEventListeners() {
    // Bookshelf events
    bookshelfBtn.addEventListener('click', openBookshelf);
    closeModalBtn.addEventListener('click', closeBookshelf);
    bookshelfModal.addEventListener('click', (e) => {
        if (e.target === bookshelfModal) {
            closeBookshelf();
        }
    });
    
    // Upload area events
    uploadArea.addEventListener('click', () => {
        hasUserInteracted = true;
        fileInput.click();
    });
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        hasUserInteracted = true;
        uploadArea.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });
    
    // Player controls - mark user interaction
    playPauseBtn.addEventListener('click', () => {
        hasUserInteracted = true;
        togglePlayPause();
    });
    prevBtn.addEventListener('click', () => {
        hasUserInteracted = true;
        previousPage();
    });
    nextBtn.addEventListener('click', () => {
        hasUserInteracted = true;
        nextPage();
    });
    volumeSlider.addEventListener('input', (e) => {
        audioElement.volume = e.target.value / 100;
    });
    speedSlider.addEventListener('input', (e) => {
        const speed = e.target.value / 100;
        audioElement.playbackRate = speed;
        speedValue.textContent = speed.toFixed(1) + 'x';
        // Save speed to localStorage for persistence
        localStorage.setItem('playbackSpeed', speed);
    });
    
    // Audio events
    audioElement.addEventListener('timeupdate', updateProgress);
    audioElement.addEventListener('ended', handleAudioEnded);
    audioElement.addEventListener('loadedmetadata', () => {
        totalTimeSpan.textContent = formatTime(audioElement.duration);
    });
}

// File Selection Handler
function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

// File Upload Handler
async function handleFile(file) {
    // Validate file type
    const validTypes = ['application/pdf', 'application/epub+zip', 'text/plain'];
    const validExtensions = ['.pdf', '.epub', '.txt'];
    const fileName = file.name.toLowerCase();
    const isValid = validExtensions.some(ext => fileName.endsWith(ext));
    
    if (!isValid) {
        showError('Invalid file type. Please upload PDF, EPUB, or TXT files only.');
        return;
    }
    
    // Show upload status
    uploadStatus.textContent = 'Uploading...';
    uploadStatus.className = 'upload-status';
    
    // Create form data
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            currentFilename = data.filename;
            totalPages = data.total_pages;
            
            uploadStatus.textContent = `✓ Uploaded: ${data.filename} (${data.total_pages} pages)`;
            uploadStatus.classList.add('success');
            
            // Load first page
            setTimeout(() => {
                uploadSection.classList.add('hidden');
                playerSection.classList.remove('hidden');
                bookTitle.textContent = data.filename;
                totalPagesSpan.textContent = totalPages;
                loadPage(0);
            }, 1000);
            
        } else {
            showError(data.error || 'Upload failed');
        }
        
    } catch (error) {
        showError('Upload failed: ' + error.message);
    }
}

// Load Page
async function loadPage(pageNum) {
    if (pageNum < 0 || pageNum >= totalPages) {
        console.log('Page out of range');
        return;
    }
    
    currentPage = pageNum;
    currentPageSpan.textContent = pageNum + 1;
    
    // Show processing status
    processingStatus.classList.remove('hidden');
    processingMessage.textContent = `Processing page ${pageNum + 1}...`;
    
    try {
        const response = await fetch(`/process/${pageNum}`);
        const data = await response.json();
        
        if (response.ok && data.success) {
            // Update translated text FIRST
            translatedText.textContent = data.translated_text;
            
            // Load audio
            audioElement.src = data.audio_url;
            audioElement.load();
            
            // Restore playback speed after loading new audio
            const savedSpeed = localStorage.getItem('playbackSpeed');
            const currentSpeed = savedSpeed ? parseFloat(savedSpeed) : 0.8;
            audioElement.playbackRate = currentSpeed;
            
            // Wait for DOM to update and audio metadata to load before auto-play
            // This ensures users see the text before hearing audio
            audioElement.addEventListener('loadedmetadata', function autoPlayHandler() {
                // Remove listener after first trigger to prevent duplicate calls
                audioElement.removeEventListener('loadedmetadata', autoPlayHandler);
                
                // Small delay to ensure text is visibly rendered (fixes Issue #2)
                setTimeout(() => {
                    // Auto-play only if user has interacted (required for iOS)
                    if (hasUserInteracted) {
                        playAudio();
                    } else {
                        // On iOS, show play button and wait for user interaction
                        if (isIOS) {
                            playPauseBtn.textContent = '▶️';
                            playPauseBtn.title = 'Tap to Play';
                            console.log('iOS: Waiting for user interaction to play');
                        } else {
                            playAudio();
                        }
                    }
                    
                    processingStatus.classList.add('hidden');
                }, 100); // 100ms delay ensures text is visible before audio starts
            }, { once: true });
            
        } else {
            showError(data.error || 'Failed to process page');
            processingStatus.classList.add('hidden');
        }
        
    } catch (error) {
        showError('Error loading page: ' + error.message);
        processingStatus.classList.add('hidden');
    }
}

// Play Audio
function playAudio() {
    console.log('Attempting to play audio...');
    
    // For iOS, ensure we have a proper user interaction before playing
    if (isIOS && !hasUserInteracted) {
        console.log('iOS: Waiting for user interaction before auto-play');
        playPauseBtn.textContent = '▶️';
        playPauseBtn.title = 'Tap to Play';
        return;
    }
    
    const playPromise = audioElement.play();
    
    if (playPromise !== undefined) {
        playPromise
            .then(() => {
                console.log('Audio playback started successfully');
                playPauseBtn.textContent = '⏸️';
                playPauseBtn.title = 'Pause';
                hasUserInteracted = true; // Mark as interacted after successful play
                
                // Update media session metadata for iOS background controls
                if (isIOS && navigator.mediaSession && currentFilename) {
                    navigator.mediaSession.metadata = new MediaMetadata({
                        title: `Page ${currentPage + 1} of ${totalPages}`,
                        artist: 'AI Audiobook Translator',
                        album: currentFilename,
                        artwork: [
                            { src: '/static/icon-192.svg', sizes: '192x192', type: 'image/svg+xml' },
                            { src: '/static/icon-512.svg', sizes: '512x512', type: 'image/svg+xml' }
                        ]
                    });
                    
                    // Set playback state
                    navigator.mediaSession.playbackState = 'playing';
                }
            })
            .catch(err => {
                console.error('Play error:', err);
                // On iOS, this is expected if user hasn't interacted yet
                if (isIOS && !hasUserInteracted) {
                    playPauseBtn.textContent = '▶️';
                    playPauseBtn.title = 'Tap to Play';
                    console.log('iOS: User must tap play button first');
                } else {
                    showError('Failed to play audio. Tap play button to start.');
                }
            });
    }
}

// Pause Audio
function pauseAudio() {
    console.log('Pausing audio...');
    audioElement.pause();
    playPauseBtn.textContent = '▶️';
    playPauseBtn.title = 'Play';
    
    // Update iOS media session state
    if (isIOS && navigator.mediaSession) {
        navigator.mediaSession.playbackState = 'paused';
    }
}

// Toggle Play/Pause
function togglePlayPause() {
    if (audioElement.paused) {
        playAudio();
    } else {
        pauseAudio();
    }
}

// Previous Page
function previousPage() {
    if (currentPage > 0) {
        loadPage(currentPage - 1);
    }
}

// Next Page
function nextPage() {
    if (currentPage < totalPages - 1) {
        loadPage(currentPage + 1);
    }
}

// Handle Audio Ended
function handleAudioEnded() {
    playPauseBtn.textContent = '▶️';
    playPauseBtn.title = 'Play';
    
    // Auto-advance to next page
    if (currentPage < totalPages - 1) {
        setTimeout(() => {
            nextPage();
        }, 500);
    }
}

// Update Progress
function updateProgress() {
    if (audioElement.duration) {
        const progress = (audioElement.currentTime / audioElement.duration) * 100;
        progressFill.style.width = progress + '%';
        currentTimeSpan.textContent = formatTime(audioElement.currentTime);
    }
}

// Format Time
function formatTime(seconds) {
    if (isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// Show Error
function showError(message) {
    errorDisplay.textContent = '❌ ' + message;
    errorDisplay.classList.remove('hidden');
    uploadStatus.textContent = message;
    uploadStatus.className = 'upload-status error';
    
    setTimeout(() => {
        errorDisplay.classList.add('hidden');
    }, 5000);
}

// Bookshelf Functions
async function openBookshelf() {
    bookshelfModal.classList.remove('hidden');
    await loadBookshelf();
}

function closeBookshelf() {
    bookshelfModal.classList.add('hidden');
}

async function loadBookshelf() {
    booksList.innerHTML = '<p class="loading-text">Loading books...</p>';
    
    try {
        const response = await fetch('/books');
        const data = await response.json();
        
        if (data.books && data.books.length > 0) {
            displayBooks(data.books);
        } else {
            booksList.innerHTML = `
                <div class="empty-bookshelf">
                    <div class="empty-bookshelf-icon">📚</div>
                    <p>Your bookshelf is empty</p>
                    <p style="font-size: 0.9em; margin-top: 10px;">Upload some books to get started!</p>
                </div>
            `;
        }
    } catch (error) {
        booksList.innerHTML = '<p class="loading-text">Error loading books</p>';
        console.error('Error loading bookshelf:', error);
    }
}

function displayBooks(books) {
    const bookIcons = {
        'PDF': '📕',
        'EPUB': '📗',
        'TXT': '📘'
    };
    
    booksList.innerHTML = books.map(book => `
        <div class="book-card" data-filename="${book.filename}">
            <div class="book-icon">${bookIcons[book.type] || '📖'}</div>
            <div class="book-title" title="${book.filename}">${book.filename}</div>
            <div class="book-info">
                <span class="book-type">${book.type}</span>
                <span>${book.size_kb} KB</span>
            </div>
            <div class="book-actions">
                <button class="book-btn load-btn" onclick="loadBookFromShelf('${book.filename}')">
                    ▶️ Load
                </button>
                <button class="book-btn delete-btn" onclick="deleteBookFromShelf('${book.filename}')">
                    🗑️ Delete
                </button>
            </div>
        </div>
    `).join('');
}

async function loadBookFromShelf(filename) {
    try {
        closeBookshelf();
        uploadStatus.textContent = `Loading ${filename}...`;
        uploadStatus.className = 'upload-status';
        uploadStatus.classList.remove('hidden');
        
        const response = await fetch(`/books/${encodeURIComponent(filename)}/load`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentFilename = data.filename;
            totalPages = data.total_pages;
            currentPage = 0;
            
            // Update UI
            bookTitle.textContent = currentFilename;
            totalPagesSpan.textContent = totalPages;
            
            // Show player, hide upload
            uploadSection.classList.add('hidden');
            playerSection.classList.remove('hidden');
            uploadStatus.classList.add('hidden');
            
            // Load first page
            await loadPage(0);
        } else {
            showError(data.error || 'Failed to load book');
        }
    } catch (error) {
        showError('Error loading book: ' + error.message);
    }
}

async function deleteBookFromShelf(filename) {
    if (!confirm(`Are you sure you want to delete "${filename}"?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/books/${encodeURIComponent(filename)}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            await loadBookshelf(); // Reload the bookshelf
        } else {
            alert('Error: ' + (data.error || 'Failed to delete book'));
        }
    } catch (error) {
        alert('Error deleting book: ' + error.message);
    }
}

// Log for debugging
console.log('App.js loaded');
