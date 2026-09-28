# Bu videoda kullanıcı müzik + efekt istedi (SKILL.md §0 kuralının istisnası).
# Seviyeler ölçülerek: müzik (duck sonrası) seslendirmenin ~18 LU altında.
set -e
D=$(python3 -c "import json;print(json.load(open('events.json'))['dur'])")
lufs(){ ffmpeg -nostdin -i "$1" -af ebur128 -f null - 2>&1 | awk '/^ +I:/{print $2}' | tail -1; }
ffmpeg -nostdin -y -v error -i music_raw.wav -af "lowpass=f=6000,highpass=f=60" music.wav
VO=$(lufs vo_tight.wav); MU=$(lufs music.wav)
MG=$(python3 -c "print(10**((($VO-12.5)-($MU))/20))")
echo "seslendirme $VO LUFS · müzik $MU LUFS -> kazanç $MG"
ffmpeg -nostdin -y -v error -i vo_tight.wav -i music.wav -i sfx.wav -filter_complex "
[0:a]aresample=48000,apad=whole_dur=$D,asplit=2[vo][sc];
[1:a]aresample=48000,volume=$MG[m];
[m][sc]sidechaincompress=threshold=0.05:ratio=2.2:attack=30:release=350[md];
[2:a]aresample=48000,highpass=f=60,volume=0.55[fx];
[vo][md][fx]amix=inputs=3:normalize=0:duration=first[a]" -map "[a]" -ac 2 -t $D mix_raw.wav
python3 /home/user/Public/.claude/skills/viral-edit/scripts/master.py mix_raw.wav mix.wav -14.0 -4.5
