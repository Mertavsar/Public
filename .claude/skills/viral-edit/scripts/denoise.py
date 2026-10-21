# Spektral Wiener gürültü temizleme: gürültü profili konuşma öncesi boşluktan (n0-n1 sn) öğrenilir.
# Karar-yönlendirmeli (decision-directed) a priori SNR — "müzikal gürültü" cıvıltısını bastırır.
# kullanım: denoise.py giriş.f32 çıkış.f32 n0 n1   (48 kHz mono float32 ham)
import sys, numpy as np
SR, N, HOP = 48000, 2048, 512
x = np.fromfile(sys.argv[1], np.float32).astype(np.float64)
n0, n1 = float(sys.argv[3]), float(sys.argv[4])
win = np.sqrt(np.hanning(N + 1)[:N])                     # analiz+sentez için kök-Hann (COLA)
pad = np.concatenate([np.zeros(N), x, np.zeros(N)])
frames = np.lib.stride_tricks.sliding_window_view(pad, N)[::HOP] * win
X = np.fft.rfft(frames, axis=1); P = np.abs(X) ** 2
a, b = int((n0 * SR + N) / HOP), int((n1 * SR + N) / HOP)
noise = P[a:b].mean(0) * 1.4                             # biraz fazla tahmin: kalıntı uğultu kalmasın
G = np.empty_like(P); prev = np.ones(P.shape[1]); floor = 10 ** (-20 / 20)
for i in range(len(P)):
    post = P[i] / noise
    prio = 0.96 * (prev ** 2) * np.maximum(P[i - 1] / noise if i else post, 0) + 0.04 * np.maximum(post - 1, 0)
    g = prio / (1 + prio); g = np.maximum(g, floor); G[i] = g; prev = g
# zaman yönünde hafif yumuşatma (kenar cızırtısı olmasın)
k = np.array([0.25, 0.5, 0.25]); G = np.apply_along_axis(lambda c: np.convolve(c, k, "same"), 0, G)
Y = np.fft.irfft(X * G, axis=1) * win
out = np.zeros(len(pad))
for i, f in enumerate(Y): out[i * HOP:i * HOP + N] += f
out = out[N:N + len(x)]
out.astype(np.float32).tofile(sys.argv[2]); print("ok")
