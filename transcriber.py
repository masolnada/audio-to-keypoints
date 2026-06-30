#!/usr/bin/env python3
"""
Catalan WhatsApp Voice Note Transcriber
Runs natively on Apple Silicon via mlx-whisper.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

try:
    import mlx_whisper
except ImportError:
    print("Error: mlx-whisper not found. Run: pip install -r requirements.txt")
    sys.exit(1)

try:
    from google import genai
    from google.genai import types as genai_types
except ImportError:
    print("Error: google-genai not found. Run: pip install -r requirements.txt")
    sys.exit(1)

BASE_DIR = Path(__file__).parent
AUDIO_DIR = BASE_DIR / "audios"
OUTPUT_DIR = BASE_DIR / "transcripts"
SUPPORTED_EXTENSIONS = {".opus", ".m4a", ".wav", ".mp3"}
MODEL = "mlx-community/whisper-small-mlx"
GEMINI_MODEL = "gemini-2.5-flash"

_gemini_api_key = os.environ.get("GEMINI_API_KEY")
if not _gemini_api_key:
    print("Error: GEMINI_API_KEY environment variable not set.")
    sys.exit(1)
_gemini_client = genai.Client(api_key=_gemini_api_key)

TAKEAWAYS_PROMPT = (
    "You are analyzing a set of WhatsApp voice note transcriptions in Catalan. "
    "Each message is labeled with its filename. "
    "Extract EVERY key point from ALL messages — do not skip or summarize away any detail, no matter how small. "
    "Group the key points by context or topic using clear markdown headings. "
    "Within each group, list every individual point as a bullet. "
    "Write each point as a direct statement — no third-person, no reporting phrases like 'it was mentioned', 'the speaker said', 'it was discussed', etc. "
    "Write all key points in Catalan. "
    "Return only the grouped key points, no introduction or closing remarks."
)


def format_timestamp(seconds: float) -> str:
    total = int(seconds)
    h, remainder = divmod(total, 3600)
    m, s = divmod(remainder, 60)
    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def transcribe_file(audio_path: Path) -> tuple:
    """Returns (segments, error_message). On success error_message is None."""
    try:
        result = mlx_whisper.transcribe(
            str(audio_path),
            language="ca",
            path_or_hf_repo=MODEL,
        )
        segments = result.get("segments", [])
        if not segments and result.get("text", "").strip():
            segments = [{"start": 0.0, "end": 0.0, "text": result["text"].strip()}]
        return segments, None
    except Exception as exc:
        return [], str(exc)


def extract_takeaways(transcripts: dict) -> str:
    combined = "\n\n".join(
        f"--- {name} ---\n{text}" for name, text in transcripts.items()
    )
    response = _gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=combined,
        config=genai_types.GenerateContentConfig(system_instruction=TAKEAWAYS_PROMPT),
    )
    return response.text.strip()


def build_markdown(audio_files, results, generated_at, takeaways: str = ""):
    lines = []
    lines.append("# WhatsApp Audio Transcriptions")
    lines.append(f"*Date: {generated_at.strftime('%Y-%m-%d %H:%M:%S')}*")
    lines.append("")
    lines.append("| # | Audio File | Status |")
    lines.append("| :--- | :--- | :--- |")
    for i, (audio, (segments, err)) in enumerate(zip(audio_files, results), start=1):
        status = "❌ Error" if err else "✅ OK"
        lines.append(f"| {i} | `{audio.name}` | {status} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    for i, (audio, (segments, err)) in enumerate(zip(audio_files, results), start=1):
        lines.append(f"### {i}. `{audio.name}`")
        if err:
            lines.append(f"❌ *Error processing this audio file ({err}).*")
        elif not segments:
            lines.append("*(No content detected)*")
        else:
            for seg in segments:
                start = format_timestamp(seg.get("start", 0))
                end = format_timestamp(seg.get("end", 0))
                text = seg.get("text", "").strip()
                if text:
                    lines.append(f"* `[{start} -> {end}]` {text}")
        lines.append("")
    if takeaways:
        lines.append("---")
        lines.append("")
        lines.append("## Key Points")
        lines.append("")
        lines.append(takeaways)
    return "\n".join(lines)


def main() -> None:
    if not AUDIO_DIR.exists():
        AUDIO_DIR.mkdir(parents=True)
        print(f"Directory created: {AUDIO_DIR}")
        print("Add .opus/.m4a/.wav/.mp3 files to whatsapp_audios/ and run again.")
        sys.exit(0)

    audio_files = sorted(
        f for f in AUDIO_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not audio_files:
        print(f"No audio files found in {AUDIO_DIR}.")
        print("Supported formats: .opus, .m4a, .wav, .mp3")
        sys.exit(0)

    print(f"Model: {MODEL}")
    print(f"Files detected: {len(audio_files)}")
    print()

    results = []
    transcripts = {}
    for i, audio in enumerate(audio_files, start=1):
        print(f"[{i}/{len(audio_files)}] Transcribing: {audio.name} ...", end=" ", flush=True)
        segments, err = transcribe_file(audio)
        if err:
            print(f"❌  ({err})")
            results.append((None, err))
            continue
        print(f"✅  ({len(segments)} segments)")
        results.append((segments, None))
        raw_text = " ".join(
            seg.get("text", "").strip() for seg in segments if seg.get("text", "").strip()
        )
        if raw_text:
            transcripts[audio.name] = raw_text

    takeaways = ""
    if transcripts:
        print(f"\nExtracting key points with {GEMINI_MODEL} ...", end=" ", flush=True)
        try:
            takeaways = extract_takeaways(transcripts)
            print("✅")
        except Exception as exc:
            print(f"❌  ({exc})")

    generated_at = datetime.now()
    timestamp = generated_at.strftime("%Y%m%d_%H%M%S")
    OUTPUT_DIR.mkdir(exist_ok=True)

    output_path = OUTPUT_DIR / f"transcriptions_{timestamp}.md"
    output_path.write_text(
        build_markdown(audio_files, results, generated_at, takeaways), encoding="utf-8"
    )

    print()
    print(f"Done → {output_path}")


if __name__ == "__main__":
    main()
