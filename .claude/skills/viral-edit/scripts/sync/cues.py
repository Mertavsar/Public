import subprocess, numpy as np, json, cv2
from rapidocr_onnxruntime import RapidOCR
W, H, FPS = 960, 540, 10
p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', 'in/src.mp4', '-vf', f'fps={FPS},scale={W}:{H}', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE)
masks = []; frames = {}
k = 0
while True:
    b = p.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    f = np.frombuffer(b, np.uint8).reshape(H, W, 3)
    band = f[440:535, 120:840]
    bright = band.mean() > 170
    m = ((band.max(2) < 90) if bright else (band.min(2) > 215)).astype(np.uint8)
    masks.append(m); frames[k] = band.copy(); k += 1
masks = np.array(masks)
n = len(masks)
on = masks.reshape(n, -1).sum(1)
# segment: değişim = önceki kareden fark
diff = np.array([0] + [np.logical_xor(masks[i], masks[i - 1]).sum() for i in range(1, n)])
has = on > 150
cues = []; start = None
for i in range(n):
    change = diff[i] > max(120, 0.25 * max(on[i], on[i - 1] if i else 1))
    if start is None:
        if has[i]: start = i
    elif (not has[i]) or change:
        cues.append((start, i)); start = i if has[i] else None
if start is not None: cues.append((start, n))
cues = [c for c in cues if c[1] - c[0] >= 3]
o = RapidOCR(); out = []
for a, b in cues:
    mid = (a + b) // 2
    full = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{mid / FPS:.2f}', '-i', 'in/src.mp4', '-frames:v', '1', '-vf', 'crop=1440:200:240:870', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], capture_output=True).stdout
    im = np.frombuffer(full, np.uint8).reshape(200, 1440, 3)
    r = o(im)[0] or []
    r = sorted(r, key=lambda x: (round(x[0][0][1] / 20), x[0][0][0]))
    txt = ' '.join(x[1] for x in r)
    out.append({'s': round(a / FPS, 2), 'e': round(b / FPS, 2), 't': txt})
json.dump(out, open('w/cues.json', 'w'), ensure_ascii=False, indent=0)
print(len(out))
for c in out: print(c['s'], c['e'], c['t'])
