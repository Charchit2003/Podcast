# AI Podcast Generator

A FastAPI-based backend service that converts PDF documents into engaging podcast-style conversations or news anchor monologues using AI.

## 🌟 Features

### 1. Dual Generation Modes
- **Podcast Conversations**
  - Natural dialogues between host and guest
  - Dynamic voice switching
  - Proper pacing and transitions
  - Thoughtful pauses between speakers

- **News Anchor Monologues**
  - Professional broadcast-style delivery
  - Clear and concise presentation
  - Natural pauses and emphasis
  - Single-voice consistency

### 2. Advanced Audio Processing
- High-quality text-to-speech synthesis
- Multiple voice options
  - Host Voice: Professional female anchor
  - Guest Voice: Male interview subject
- Natural pauses and emphasis
- Output in WAV format (44.1kHz, 16-bit PCM)

### 3. Smart PDF Processing
- Multiple page support
- Intelligent text extraction
- Content optimization (2000 character limit)
- Error handling for malformed PDFs

## 🚀 Technical Stack

- **Backend Framework**: FastAPI
- **AI Services**:
  - Together AI (LLM): Meta-Llama-3.1-70B-Instruct-Turbo
  - Cartesia (TTS): sonic-2 model
- **Audio Processing**: FFmpeg
- **File Formats**:
  - Input: PDF
  - Output: WAV (16-bit PCM)

## 🔧 Setup

1. **Environment Setup**
```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\activate
```

2. **Install Dependencies**
```powershell
pip install -r requirements.txt
```

3. **Configure Environment**
Create `.env.local`:
```env
TOGETHER_API_KEY=your_together_api_key
CARTESIA_API_KEY=your_cartesia_api_key
```

4. **Install FFmpeg**
- Download from [FFmpeg website](https://ffmpeg.org/download.html)
- Add to system PATH

5. **Start Server**
```powershell
cd src
python main.py
```

## 📁 Project Structure
```
Backend/
├── src/
│   ├── config/
│   │   └── settings.py         # API keys and configuration
│   ├── models/
│   │   ├── podcast.py         # Podcast data models
│   │   └── anchor.py          # Anchor data models
│   ├── utils/
│   │   ├── podcast_processor.py  # Podcast generation
│   │   └── anchor_processor.py   # Anchor generation
│   └── main.py                # FastAPI application
├── output/                    # Generated audio files
├── uploads/                   # Temporary PDF storage
└── .env.local                 # Environment variables
```

## 🎯 API Endpoints

### Podcast Generation
```http
POST /api/process-podcast
```
Parameters:
- `pdf_file`: PDF document (multipart/form-data)
- `topic`: Optional topic focus
- `language`: Language selection (default: "english")

Response:
```json
{
    "audio_url": "path/to/generated/podcast.wav",
    "transcript": {
        "scratchpad": "outro notes",
        "name_of_guest": "Guest name",
        "script": [{"speaker": "Host/Guest", "text": "dialogue"}]
    },
    "summary": "podcast summary"
}
```

### News Anchor Generation
```http
POST /api/process-anchor
```
Parameters:
- `pdf_file`: PDF document (multipart/form-data)
- `topic`: Optional topic focus
- `language`: Language selection (default: "english")

Response:
```json
{
    "audio_url": "path/to/generated/anchor.wav",
    "transcript": {
        "scriptNotes": "broadcast notes",
        "script": [{"speaker": "Anchor", "text": "monologue"}]
    },
    "summary": "broadcast summary"
}
```

## ⚠️ Error Handling
- PDF processing errors
- Script generation failures
- Audio conversion issues
- Network timeouts
- Invalid input handling

## 🎵 Voice Configuration
```python
HOST_VOICE_ID = "3cbf8fed-74d5-4690-b715-711fcf8d825f"    # Female host
GUEST_VOICE_ID = "6b92f628-be90-497c-8f4c-3b035002df71"   # Male guest
MODEL_ID = "sonic-2"                                       # TTS model
```

## 📝 Note
This is a development version. For production:
- Implement authentication
- Add rate limiting
- Set up proper logging
- Configure CORS appropriately
- Add input validation
- Implement caching
- Add proper error recovery


## 📞 Contact
charchitpaharia@gmail.com
ch21b023@smail.iitm.ac.in
