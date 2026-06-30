# audio-to-keypoints

Transcribes voice notes natively on Apple Silicon using `mlx-whisper`, then extracts key points grouped by context via Google Gemini. Language is auto-detected from the audio.

---

## Prerequisites

### 1. ffmpeg (required)

```bash
brew install ffmpeg
```

### 2. Python 3.10+

```bash
python3 --version
```

---

## Installation

```bash
# Clone or unzip the project and enter the directory
cd audio-to-keypoints

# Create a virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Gemini API key

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your-key-here
```

---

## Usage

1. Copy your voice notes (`.opus`, `.m4a`, `.wav`, `.mp3`) into the `audios/` folder.

2. Run:

```bash
python transcriber.py
```

3. The resulting Markdown file appears in `transcripts/transcriptions_YYYYMMDD_HHMMSS.md`.

---

## Models

- **Speech-to-text:** `mlx-community/whisper-small-mlx` — downloaded automatically on first run (~250 MB).
- **Key point extraction:** `gemini-2.5-flash` via Google Gemini API.

To switch to a different Whisper model, edit `MODEL` in `transcriber.py`:

```python
MODEL = "mlx-community/whisper-large-v3-turbo"
```

---

## Project structure

```
audio-to-keypoints/
├── audios/             ← input files (.opus / .m4a / …)
├── transcripts/        ← generated Markdown output
├── transcriber.py      ← main script
├── requirements.txt    ← Python dependencies
└── README.md
```

---

## Output format

Each run produces a single Markdown file containing:

- **Session summary table** — one row per audio file with status
- **Per-file sections** — raw timestamped transcription
- **Key points** — all points grouped by context, in the language of the audio
