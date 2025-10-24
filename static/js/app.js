// Main application JavaScript
let currentPage = 0;
let totalPages = 0;
let currentFilename = '';
let audioElement = null;

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

const currentPageSpan = document.getElementById('current-page');
const totalPagesSpan = document.getElementById('total-pages');
const bookTitle = document.getElementById('book-title');
const translatedText = document.getElementById('translated-text');
const progressFill = document.getElementById('progress-fill');
const currentTimeSpan = document.getElementById('current-time');
const totalTimeSpan = document.getElementById('total-time');
const processingStatus = document.getElementById('processing-status');
const processingMessage = document.getElementById('processing-message');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    audioElement = document.getElementById('audio-element');
    setupEventListeners();
    console.log('App initialized');
});

// Setup Event Listeners
function setupEventListeners() {
    // Upload area events
    uploadArea.addEventListener('click', () => fileInput.click());
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
        uploadArea.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });
    
    // Player controls
    playPauseBtn.addEventListener('click', togglePlayPause);
    prevBtn.addEventListener('click', previousPage);
    nextBtn.addEventListener('click', nextPage);
    volumeSlider.addEventListener('input', (e) => {
        audioElement.volume = e.target.value / 100;
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
    const validTypes = ['application/pdf', 'application/epub+zip'];
    const validExtensions = ['.pdf', '.epub'];
    const fileName = file.name.toLowerCase();
    const isValid = validExtensions.some(ext => fileName.endsWith(ext));
    
    if (!isValid) {
        showError('Invalid file type. Please upload PDF or EPUB files only.');
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
            // Update translated text
            translatedText.textContent = data.translated_text;
            
            // Load audio
            audioElement.src = data.audio_url;
            audioElement.load();
            
            // Auto-play
            playAudio();
            
            processingStatus.classList.add('hidden');
            
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
    audioElement.play()
        .then(() => {
            playPauseBtn.textContent = '⏸️';
            playPauseBtn.title = 'Pause';
        })
        .catch(err => {
            console.error('Play error:', err);
            showError('Failed to play audio');
        });
}

// Pause Audio
function pauseAudio() {
    audioElement.pause();
    playPauseBtn.textContent = '▶️';
    playPauseBtn.title = 'Play';
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

// Log for debugging
console.log('App.js loaded');
