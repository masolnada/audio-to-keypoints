---
name: audio-to-keypoints
description: "Transcribe voice notes and extract grouped key points (Apple Silicon)."
version: 1.0.0
platforms: [macos]
metadata:
  hermes:
    tags: [audio, transcription, whisper, voice-notes, key-points, gemini, mlx]
    related_skills: [note-taking]
---

# Audio to Key Points

Transcribes voice notes locally on Apple Silicon using `mlx-whisper`, then extracts key points grouped by topic via Google Gemini. Language is auto-detected.

**Project directory:** `~/audio-to-keypoints/`
**Source:** `https://github.com/masolnada/audio-to-keypoints`

## Requirements

- macOS with Apple Silicon
- `ffmpeg` (`brew install ffmpeg`)
- `git`, `python3` (3.10+)
- A Google Gemini API key (free tier works)

## First-time setup

Run these steps once before the first transcription. Skip any step already done.

```bash
# 1. Clone the project
git clone https://github.com/masolnada/audio-to-keypoints.git ~/audio-to-keypoints

# 2. Create the virtual environment and install dependencies
cd ~/audio-to-keypoints
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Configure your Gemini API key
echo "GEMINI_API_KEY=your-key-here" > ~/audio-to-keypoints/.env
```

Get a free Gemini API key at https://aistudio.google.com/apikey

## Inputs

The user provides one or more audio files (`.opus`, `.m4a`, `.wav`, `.mp3`). They may:
- Give an explicit file path
- Describe a location (e.g. "the voice note I just recorded in ~/Downloads")
- Mention a filename by name

## Workflow

### Step 1: Locate the audio files

Resolve all file paths the user mentioned. If a path is ambiguous, use `find` or `ls` to locate it.

### Step 2: Copy files to the audios/ directory

Clear any leftover files from the previous run, then copy the user's files in:

```bash
rm -f ~/audio-to-keypoints/audios/*
cp <source_file> ~/audio-to-keypoints/audios/
```

### Step 3: Run the transcriber

```bash
cd ~/audio-to-keypoints && source .venv/bin/activate && python transcriber.py
```

The script will:
1. Transcribe each file locally with mlx-whisper (downloads ~250 MB model on first run)
2. Send transcripts to `gemini-2.5-flash` for key point extraction
3. Write output to `~/audio-to-keypoints/transcripts/transcriptions_YYYYMMDD_HHMMSS.md`

### Step 4: Present the output

```bash
cat "$(ls -t ~/audio-to-keypoints/transcripts/*.md | head -1)"
```

Present the **Key Points** section to the user. Include the raw timestamped transcription only if they ask for it.

## Error handling

| Error | Fix |
|-------|-----|
| `mlx-whisper not found` | `cd ~/audio-to-keypoints && source .venv/bin/activate && pip install -r requirements.txt` |
| `GEMINI_API_KEY not set` | Confirm `~/audio-to-keypoints/.env` contains `GEMINI_API_KEY=<key>` |
| `ffmpeg not found` | `brew install ffmpeg` |
| No audio files detected | Only `.opus`, `.m4a`, `.wav`, `.mp3` are supported |
| Model download (~250 MB) | Normal on first run — wait for it |

## Notes

- Language is auto-detected by Whisper — works for Catalan, Spanish, English, etc.
- For higher accuracy (slower), edit `MODEL` in `transcriber.py` to `"mlx-community/whisper-large-v3-turbo"`
- Each run appends a new timestamped file to `transcripts/` — nothing is deleted automatically
