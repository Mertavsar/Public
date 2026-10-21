# Boğuklaşan bölümü temiz bölümün tını dengesine geri getirir (zamana göre değişen eşleştirme EQ'su).
# Referans: temiz kısmın konuşma karelerinin uzun süreli ortalama spektrumu (LTAS).
# Her 0.5 s'lik pencerede yerel LTAS ölçülür; fark (yumuşatılmış, sınırlı) o pencerenin karelerine uygulanır.
# kullanım: matcheq.py giriş.f32 çıkış.f32 ref0 ref1
import sys, numpy as np
SR, N, HOP = 48000, 2048, 512
x = np.fromfile(sys.argv[1], np.float32).astype(np.float64); r0, r1 = float(sys.argv[3]), float(sys.argv[4])
win = np.sqrt(np.hanning(N + 1)[:N]); pad = np.concatenate([np.zeros(N), x, np.zeros(N)])
X = np.fft.rfft(np.lib.stride_tricks.sliding_window_view(pad, N)[::HOP] * win, axis=1)
P = np.abs(X) ** 2 + 1e-12; f = np.fft.rfftfreq(N, 1 / SR); T = (np.arange(len(P)) * HOP - N) / SR
spb = (f >= 300) & (f < 3000); S = 10 * np.log10(P[:, spb].sum(1)); speech = S > np.percentile(S, 45)

# 1/3 oktav bantları
edges = 80 * 2 ** (np.arange(0, 24) / 3); edges = edges[edges < 18000]
bands = [(a, b) for a, b in zip(edges[:-1], edges[1:])]
def ltas(m):
    # konuşma bandına göre normalize edilmiş bant seviyeleri (dB)
    Pm = P[m]; ref = Pm[:, spb].sum(1, keepdims=True)
    return np.array([10 * np.log10((Pm[:, (f >= a) & (f < b)].sum(1, keepdims=True) / ref).mean()) for a, b in bands])
REF = ltas(speech & (T >= r0) & (T < r1))
fc = np.array([np.sqrt(a * b) for a, b in bands])

corr_t = []; tw = np.arange(0, T[-1] + 0.5, 0.5)
for t0 in tw:
    m = speech & (T >= t0 - 0.5) & (T < t0 + 1.0)           # 1.5 s pencere, 0.5 s adım
    if m.sum() < 8: corr_t.append(np.zeros(len(bands))); continue
    d = REF - ltas(m)
    d[fc < 200] = np.minimum(d[fc < 200], 0)                  # alçakta yalnızca kısma (el darbesi/boğukluk)
    d = np.clip(d, -10, 14)
    d = np.convolve(np.pad(d, 1, mode="edge"), [0.25, 0.5, 0.25], "valid")   # bantlar arası yumuşat
    # yalnızca belirgin sapmada düzelt: küçük farklar doğal tını değişimidir
    hf = d[fc > 3000].mean()
    corr_t.append(d * np.clip((hf - 3) / 6, 0, 1) if hf > 0 else d * 0)
corr_t = np.array(corr_t)
# zamanda yumuşat (ani tını sıçraması olmasın)
k = np.array([1, 2, 3, 2, 1], float); k /= k.sum()
corr_t = np.array([np.convolve(np.pad(c, 2, mode="edge"), k, "valid") for c in corr_t.T]).T
G = np.empty_like(P)
for i, t in enumerate(T):
    c = np.array([np.interp(t, tw, corr_t[:, j]) for j in range(len(bands))])
    G[i] = 10 ** (np.interp(np.log(np.maximum(f, 1)), np.log(fc), c) / 20)
Y = np.fft.irfft(X * G, axis=1) * win
out = np.zeros(len(pad))
for i, y in enumerate(Y): out[i * HOP:i * HOP + N] += y
out = out[N:N + len(x)] / 2.0
out.astype(np.float32).tofile(sys.argv[2])
for t0 in range(0, int(T[-1]), 2):
    j = int(t0 / 0.5); print(f"{t0:2d}s düzeltme 4-12k: {corr_t[j][(fc > 4000) & (fc < 12000)].mean():+5.1f} dB  <150: {corr_t[j][fc < 150].mean():+5.1f}")
