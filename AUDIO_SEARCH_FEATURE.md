# Audio Search Feature

## Overview

This feature adds audio transcription and search capabilities to the video search system. When videos are uploaded, the system now:

1. **Extracts audio** from video files
2. **Transcribes speech** using Whisper AI
3. **Stores transcriptions** separately from visual captions
4. **Searches both** video captions and audio transcriptions when using RAG search

## How It Works

### 1. Audio Processing Pipeline

When a video is processed (YouTube URL or file upload):

1. **Audio Extraction**: Uses `ffmpeg` to extract audio as WAV (16kHz mono)
2. **Speech-to-Text**: Uses OpenAI Whisper (base model) to transcribe speech
3. **Storage**: Saves transcriptions to `audio_transcriptions.txt` with format:
   ```
   video_prefix_audio_timestamp: transcription_text
   ```
4. **Embeddings**: Generates embeddings and stores in separate ChromaDB collection (`audio_transcriptions`)

### 2. Search Integration

When you search using RAG:

- **Dual Search**: Searches both `video_captions` and `audio_transcriptions` collections
- **Result Merging**: Combines results from both sources, deduplicates by timestamp
- **Source Indication**: Results include a `source` field (`"video"` or `"audio"`)
- **Unified Results**: Returns video clips where matching audio was found

## Files Modified/Created

### New Files
- **`audio_processor.py`**: Handles audio extraction, transcription, and storage

### Modified Files
- **`vector_store.py`**: Added `audio_transcriptions` collection and search functions
- **`process_video.py`**: Added audio processing step for YouTube videos
- **`process_clips.py`**: Added audio processing step for uploaded clips
- **`rag_search.py`**: Modified to search both video and audio embeddings
- **`app.py`**: Added audio transcription loading on startup
- **`requirements.txt`**: Added `openai-whisper` and `ffmpeg-python`

## Installation

1. **Install Whisper**:
   ```bash
   pip install openai-whisper
   ```

2. **Install ffmpeg** (if not already installed):
   - Windows: Download from https://ffmpeg.org/download.html
   - Linux: `sudo apt-get install ffmpeg`
   - Mac: `brew install ffmpeg`

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Processing Videos with Audio

When you upload a video (YouTube URL or file), audio processing happens automatically:

1. Video is processed (frames extracted, visual captions generated)
2. Audio is extracted from video
3. Speech is transcribed with timestamps
4. Transcriptions are stored and indexed

### Searching Audio

Use the existing RAG search interface. The system will automatically:

- Search both visual captions and audio transcriptions
- Return results from either source
- Show which source matched (video or audio) in the result

Example queries that work well with audio:
- "when they say hello"
- "the moment he explains the plan"
- "dialogue about the mission"
- "conversation before the action"

## File Structure

```
audio_extracts/          # Extracted audio files (.wav)
audio_transcriptions.txt # Transcriptions with timestamps
chroma_db/
  ├── video_captions/    # Visual caption embeddings
  └── audio_transcriptions/ # Audio transcription embeddings
```

## Configuration

### Whisper Model

The default model is `"base"` (good balance of speed and accuracy). To change:

Edit `audio_processor.py`:
```python
model = whisper.load_model("base")  # Options: tiny, base, small, medium, large
```

- **tiny**: Fastest, least accurate
- **base**: Balanced (default)
- **small**: Better accuracy
- **medium**: High accuracy
- **large**: Best accuracy, slowest

### Audio Extraction Settings

Audio is extracted at:
- **Sample Rate**: 16kHz (optimal for Whisper)
- **Channels**: Mono
- **Format**: PCM 16-bit WAV

## Performance Notes

- **First Run**: Whisper model download (~150MB for base model)
- **Processing Time**: ~1-2x video duration (depends on hardware)
- **Storage**: Audio files are kept in `audio_extracts/` (can be large)

## Troubleshooting

### "Whisper not installed"
```bash
pip install openai-whisper
```

### "ffmpeg not found"
Install ffmpeg and ensure it's in your PATH.

### Audio processing fails silently
Check the status messages during video processing. Audio errors are logged but don't stop video processing.

### No audio results in search
- Verify audio was transcribed (check `audio_transcriptions.txt`)
- Check that `load_transcriptions_to_vector_db()` was called
- Verify ChromaDB collection has data: `audio_collection.count()`

## Future Enhancements

- Language detection and multi-language support
- Speaker diarization (identify different speakers)
- Audio quality filtering (skip silent/noisy segments)
- Configurable Whisper model per video
- Audio-only search mode toggle

