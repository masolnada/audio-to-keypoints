# audio-to-keypoints

Transcribes Catalan voice notes natively on Apple Silicon M4 using `mlx-whisper`, then extracts key points grouped by context via Google Gemini.

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
cd catalan-audio-transcriber

# Create a virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Gemini API key

The transcriber uses Google Gemini to clean up the raw transcription and extract key points.
Export your API key before running:

```bash
export GEMINI_API_KEY="your-key-here"
```

---

## Usage

1. Copy your WhatsApp voice notes (`.opus`, `.m4a`, `.wav`, `.mp3`) into the `audios/` folder.

2. Run the transcriber:

```bash
python transcriber.py
```

3. The resulting Markdown file appears in `transcripts/transcriptions_YYYYMMDD_HHMMSS.md`.

Audio files are deleted automatically after processing.

---

## Models

- **Speech-to-text:** `mlx-community/whisper-small-mlx` — downloaded automatically on first run (~250 MB).
- **LLM cleanup & key points:** `gemini-2.0-flash` via Google Gemini API.

To switch to a faster (lower accuracy) Whisper model, edit `MODEL` in `transcriber.py`:

```python
MODEL = "mlx-community/whisper-large-v3-turbo"
```

---

## Project structure

```
catalan-audio-transcriber/
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
- **Per-file sections** — raw timestamped transcription + cleaned text
- **Key points** — bullet-point summary at the end of the file
