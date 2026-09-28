# Kullanıcı kuralı (SKILL.md §0): efekt sesi ve sentetik müzik YOK. Ses = seslendirme.
set -e
D=$(python3 -c "import json;print(json.load(open('events.json'))['dur'])")
ffmpeg -nostdin -y -v error -i vo_tight.wav -af "aresample=48000,apad=whole_dur=$D" -ac 2 -t $D mix_raw.wav
python3 /home/user/Public/.claude/skills/viral-edit/scripts/master.py mix_raw.wav mix.wav -14.0 -4.5
