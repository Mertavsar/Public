# Seslendirmedeki cumle/virgul duraksamalarini kisaltir.
# Sadece >=0.25s gercek sessizlikler (-35 dB) ele alinir; kelime ici unsuz
# kapanislari (<0.12s) bu esigin cok altinda kaldigi icin hic dokunulmaz.
import subprocess, re, json, numpy as np
SR=44100; KEEP=0.13; XF=0.012
raw=subprocess.run(["ffmpeg","-v","error","-i","vo.mp3","-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True,check=True).stdout
x=np.frombuffer(raw,dtype=np.float32).copy()
log=subprocess.run(["ffmpeg","-nostdin","-i","vo.mp3","-af","silencedetect=noise=-35dB:d=0.25","-f","null","-"],capture_output=True,text=True).stderr
st=[float(v) for v in re.findall(r"silence_start: ([0-9.]+)",log)]
en=[float(v) for v in re.findall(r"silence_end: ([0-9.]+)",log)]
gaps=[(s,e) for s,e in zip(st,en) if s>0.05]
# bastaki sessizlik: 0.05s birak
lead=next((e for s,e in zip(st,en) if s<=0.05),0)
segs=[]; cur=max(0,lead-0.05)
for s,e in gaps:
    segs.append((cur,s+KEEP/2)); cur=e-KEEP/2
segs.append((cur,len(x)/SR))
n=int(XF*SR); ramp=np.linspace(0,1,n,dtype=np.float32)
out=x[int(segs[0][0]*SR):int(segs[0][1]*SR)].copy(); tmap=[]
for a,b in segs[1:]:
    p=x[int(a*SR):int(b*SR)]
    tmap.append((a,len(out)/SR))
    out[-n:]=out[-n:]*(1-ramp)+p[:n]*ramp
    out=np.concatenate([out,p[n:]])
subprocess.run(["ffmpeg","-v","error","-y","-f","f32le","-ar",str(SR),"-ac","1","-i","-","vo_tight.wav"],input=out.tobytes(),check=True)
print(f"{len(gaps)} duraksama kisaltildi · {len(x)/SR:.2f}s -> {len(out)/SR:.2f}s")
