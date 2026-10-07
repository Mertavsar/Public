#!/usr/bin/env python3
"""Kokoro (açık kaynak, insana yakın) TTS: tek satır -> wav. Kurulum (bir kez):
    python3 -m venv tts/venv && tts/venv/bin/pip install kokoro-onnx soundfile
    model: github.com/thewh1teagle/kokoro-onnx releases model-files-v1.0
           (kokoro-v1.0.onnx + voices-v1.0.bin) -> tts/
    tts/venv/bin/python -I tts_kokoro.py tts/ am_michael 1.05 out.wav "Number one."
Sesler: am_michael (doğal erkek), am_fenrir (kalın), am_puck, af_heart (kadın).
"""
import sys, soundfile as sf
from kokoro_onnx import Kokoro
k = Kokoro(sys.argv[1] + "/kokoro-v1.0.onnx", sys.argv[1] + "/voices-v1.0.bin")
voice, speed, out = sys.argv[2], float(sys.argv[3]), sys.argv[4]
text = sys.argv[5]
s, sr = k.create(text, voice=voice, speed=speed, lang="en-us")
sf.write(out, s, sr)
print(out, len(s) / sr)
