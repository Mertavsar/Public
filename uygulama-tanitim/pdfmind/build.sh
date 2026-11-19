#!/bin/bash
# Kullanım: build.sh <çalışma_klasörü> <ham_video.mp4>
set -e
HERE=$(cd "$(dirname "$0")" && pwd); WD=$1; mkdir -p "$WD"; cp "$2" "$WD/ham.mp4"; cp "$HERE/ses.srt" "$WD/"; cd "$WD"
PY=${PY:-python3}
[ -f stab.mp4 ] || { ffmpeg -nostdin -y -v error -i ham.mp4 -vf "fps=30,vidstabdetect=shakiness=6:accuracy=12:result=tr.trf" -f null -
  ffmpeg -nostdin -y -v error -i ham.mp4 -vf "fps=30,vidstabtransform=input=tr.trf:smoothing=18:optzoom=1:interpol=bicubic" -c:v libx264 -crf 14 -preset fast -an stab.mp4; }
$PY "$HERE/edit.py" "$WD"
# ses: temizlik + kesimler
ffmpeg -nostdin -y -v error -i ham.mp4 -vn -ac 1 -ar 48000 -af "highpass=f=90,lowpass=f=12000,afftdn=nr=16:nf=-32:tn=1,equalizer=f=250:t=q:w=1:g=-3,equalizer=f=3200:t=q:w=1.2:g=3.5,equalizer=f=8000:t=q:w=1:g=1.5,deesser=i=0.35,acompressor=threshold=-22dB:ratio=3:attack=5:release=120:makeup=4dB" vclean.wav
$PY - <<'PYEOF'
import json, subprocess
p = json.load(open("plan.json")); L = []
for i, (a, b, v) in enumerate(p["SEG"]):
    d = b - a; subprocess.run(["ffmpeg", "-nostdin", "-y", "-v", "error", "-ss", str(a), "-t", str(d), "-i", "vclean.wav", "-af", f"afade=t=in:d=0.03,afade=t=out:st={d-0.04:.3f}:d=0.04", "-ar", "48000", "-ac", "1", f"p{i}.wav"], check=True); L.append(f"file 'p{i}.wav'")
open("parts.txt", "w").write("\n".join(L)); open("dur.txt", "w").write(str(p["DUR"]))
PYEOF
ffmpeg -nostdin -y -v error -f concat -safe 0 -i parts.txt -c copy voice.wav
D=$(cat dur.txt); FO=$(awk "BEGIN{print $D-1.4}")
[ -f Inspired.mp3 ] || curl -s -m 120 -o Inspired.mp3 "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Inspired.mp3"
ffmpeg -nostdin -y -v error -i voice.wav -ss 4 -i Inspired.mp3 -filter_complex "[1:a]aformat=sample_rates=48000:channel_layouts=mono,volume=0.16,highpass=f=60,afade=t=in:d=0.3,afade=t=out:st=$FO:d=1.4[m];[m][0:a]sidechaincompress=threshold=0.05:ratio=5:attack=10:release=250[md];[0:a][md]amix=inputs=2:normalize=0:duration=first[o]" -map "[o]" -ar 48000 mix_raw.wav
$PY /home/user/Public/.claude/skills/viral-edit/scripts/master.py mix_raw.wav mix.wav -14.0 -3.5
ffmpeg -nostdin -y -v error -i video_sessiz.mp4 -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -crf 21 -maxrate 6000k -bufsize 12000k -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart -shortest pdfmind_edit.mp4
ls -la pdfmind_edit.mp4
