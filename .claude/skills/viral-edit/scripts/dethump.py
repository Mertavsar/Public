# Mikrofon sürtünmesi / tutma darbeleri: 250 Hz altındaki enerji, konuşma bandına (250-4000 Hz) göre
# baskınsa o anda yalnızca alçak frekans bastırılır. Konuşmanın kendisine dokunulmaz.
import sys, numpy as np
SR, N, HOP = 48000, 2048, 512
x = np.fromfile(sys.argv[1], np.float32).astype(np.float64)
win = np.sqrt(np.hanning(N + 1)[:N]); pad = np.concatenate([np.zeros(N), x, np.zeros(N)])
fr = np.lib.stride_tricks.sliding_window_view(pad, N)[::HOP] * win
X = np.fft.rfft(fr, axis=1); P = np.abs(X) ** 2 + 1e-12; f = np.fft.rfftfreq(N, 1 / SR)
lo, sp = (f >= 20) & (f < 250), (f >= 250) & (f < 4000)
d = 10 * np.log10(P[:, lo].sum(1)) - 10 * np.log10(P[:, sp].sum(1))       # alçak - konuşma (dB)
M = 10 * np.log10(P[:, sp].sum(1)); quiet = M < np.percentile(M, 70) - 25      # konuşma bandı sessizse
att = np.clip((d - 4) / 8, 0, 1) * 30 * quiet                              # 4 dB üstünde başlar, 12 dB'de tam 30 dB
att = np.convolve(att, np.ones(5) / 5, "same")                             # zamanda yumuşat
g = np.ones_like(P); ramp = np.clip((300 - f) / 100, 0, 1)                 # 200-300 Hz arası yumuşak geçiş
g = 10 ** (-(att[:, None] * ramp[None, :]) / 20)
Y = np.fft.irfft(X * g, axis=1) * win
out = np.zeros(len(pad))
for i, y in enumerate(Y): out[i * HOP:i * HOP + N] += y
out = out[N:N + len(x)] / 2.0                                              # kök-Hann + HOP=N/4 -> kazanç 2
out.astype(np.float32).tofile(sys.argv[2]); print("bastırılan kare:", int((att > 3).sum()), "/", len(att))
