"""
Automated Video Builder for S1Gate Presentation.
Takes audio from Gemini TTS (MP3/WAV/M4A), aligns it with the 6 rendered 1080p slides,
and produces a high-definition MP4 video presentation.
"""
import sys
import json
import argparse
import subprocess
from pathlib import Path

PRESENTATION_DIR = Path(__file__).parent.resolve()
OUTPUT_DIR = PRESENTATION_DIR / "output"
SLIDES_DIR = PRESENTATION_DIR / "slides"

# Proportional weights of narration time per slide based on word count
SLIDE_WEIGHTS = {
    1: 0.10,  # Slide 1: Title & Hook (~30 words)
    2: 0.19,  # Slide 2: The Latency Problem (~55 words)
    3: 0.23,  # Slide 3: Kahneman Architecture (~65 words)
    4: 0.22,  # Slide 4: Actor-Critic Remediation Loop (~60 words)
    5: 0.16,  # Slide 5: Empirical Benchmarks (~45 words)
    6: 0.10,  # Slide 6: Live Deployment & Conclusion (~30 words)
}

def get_audio_duration(audio_path: Path) -> float:
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(result.stdout.strip())

def build_presentation(audio_file: Path, output_mp4: Path = None):
    if not audio_file.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")

    if output_mp4 is None:
        output_mp4 = PRESENTATION_DIR / "s1gate_presentation.mp4"

    # Ensure slides exist
    for i in range(1, 7):
        slide_img = OUTPUT_DIR / f"slide_{i}.png"
        if not slide_img.exists():
            print(f"Slide image {slide_img} not found. Running generate_slides.py first...")
            subprocess.run([sys.executable, str(PRESENTATION_DIR / "generate_slides.py")], check=True)
            break

    total_duration = get_audio_duration(audio_file)
    print(f"\n[+] Detected Audio File: {audio_file.name}")
    print(f"[+] Total Duration: {total_duration:.2f} seconds ({total_duration/60:.2f} minutes)")

    # Calculate exact duration for each slide
    durations = {}
    print("\n[+] Slide Timing Breakdown:")
    accumulated = 0.0
    for i in range(1, 7):
        if i == 6:
            # Round out any floating point remainder for the last slide
            durations[i] = round(total_duration - accumulated, 2)
        else:
            durations[i] = round(total_duration * SLIDE_WEIGHTS[i], 2)
            accumulated += durations[i]
        start_time = accumulated - durations[i] if i > 1 else 0.0
        print(f"    Slide {i}: {durations[i]:.2f}s  (from {start_time:.2f}s to {start_time + durations[i]:.2f}s)")

    # Create concat list for ffmpeg
    concat_file = PRESENTATION_DIR / "concat_list.txt"
    with open(concat_file, "w", encoding="utf-8") as f:
        for i in range(1, 7):
            slide_path = (OUTPUT_DIR / f"slide_{i}.png").resolve()
            f.write(f"file '{slide_path}'\n")
            f.write(f"duration {durations[i]:.2f}\n")
        # Concat demuxer requires the last file to be repeated without duration
        slide_6_path = (OUTPUT_DIR / "slide_6.png").resolve()
        f.write(f"file '{slide_6_path}'\n")

    print(f"\n[+] Compiling 1080p MP4 with ffmpeg...")
    cmd = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-i", str(audio_file),
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(output_mp4)
    ]
    
    subprocess.run(cmd, check=True)
    print(f"\n[SUCCESS] Presentation video compiled successfully!")
    print(f"          Target: {output_mp4}")
    print(f"          Resolution: 1920x1080 (Full HD)")
    print(f"          Duration: {total_duration:.2f}s")
    return output_mp4

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build S1Gate presentation video from audio")
    parser.add_argument("--audio", type=Path, default=PRESENTATION_DIR / "voiceover.mp3",
                        help="Path to Gemini TTS voiceover file (mp3, wav, m4a)")
    parser.add_argument("--output", type=Path, default=PRESENTATION_DIR / "s1gate_presentation.mp4",
                        help="Path to output MP4 file")
    args = parser.parse_args()

    if not args.audio.exists():
        # Check if voiceover.wav exists instead
        wav_fallback = PRESENTATION_DIR / "voiceover.wav"
        if wav_fallback.exists():
            args.audio = wav_fallback
        else:
            print(f"[!] Audio file not found at {args.audio}")
            print(f"    Please drop your Gemini TTS audio into:")
            print(f"    {PRESENTATION_DIR / 'voiceover.mp3'}  OR  {wav_fallback}")
            print(f"    or run: python {Path(__file__).name} --audio <path_to_audio_file>")
            sys.exit(1)

    build_presentation(args.audio, args.output)
