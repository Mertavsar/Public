set -e
D=$(python3 -c "import json;print(json.load(open('events.json'))['dur'])")
ffmpeg -nostdin -y -v error -i vo_tight.wav -i music.wav -i sfx.wav -filter_complex "
[0:a]aresample=48000,apad=whole_dur=$D,asplit=2[vo][sc];
[1:a]aresample=48000,highpass=f=50,volume=0.55[m];
[m][sc]sidechaincompress=threshold=0.09:ratio=2.5:attack=15:release=160[md];
[2:a]aresample=48000,highpass=f=50,volume=0.62[fx];
[vo][md][fx]amix=inputs=3:normalize=0:duration=first[a]" -map "[a]" -ac 2 -t $D mix_raw.wav
python3 /home/user/Public/.claude/skills/viral-edit/scripts/master.py mix_raw.wav mix.wav -14.0 -3.5
