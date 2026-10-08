#!/usr/bin/env python3
"""MDX-Net (UVR Kim_Vocal_2) ile ses ayırma: girdi -> vokal (konuşma+şarkı vokali) ve enstrümantal.
    venv/bin/python -I mdx.py model.onnx in.wav vocals.wav instr.wav"""
import sys
import numpy as np, soundfile as sf, onnxruntime as ort

model, inp, out_v, out_i = sys.argv[1:5]
N_FFT, HOP, DIM_F, DIM_T = 6144, 1024, 3072, 256
CHUNK = HOP * (DIM_T - 1)
TRIM = N_FFT // 2
GEN = CHUNK - 2 * TRIM
win = (0.5 - 0.5 * np.cos(2 * np.pi * np.arange(N_FFT) / N_FFT)).astype(np.float32)   # periyodik hann


def stft(x):                                   # x: (L,) center=True reflect
    xp = np.pad(x, N_FFT // 2, mode="reflect")
    n = 1 + (len(xp) - N_FFT) // HOP
    idx = np.arange(N_FFT)[None, :] + HOP * np.arange(n)[:, None]
    return np.fft.rfft(xp[idx] * win, axis=1).T          # (F, T)


def istft(S, length):
    fr = np.fft.irfft(S.T, n=N_FFT, axis=1) * win
    n = fr.shape[0]; L = N_FFT + HOP * (n - 1)
    y = np.zeros(L); wsum = np.zeros(L)
    for i in range(n):
        y[i * HOP:i * HOP + N_FFT] += fr[i]; wsum[i * HOP:i * HOP + N_FFT] += win ** 2
    y /= np.maximum(wsum, 1e-8)
    return y[N_FFT // 2:N_FFT // 2 + length]


x, sr = sf.read(inp, dtype="float32", always_2d=True)
assert sr == 44100, sr
x = x.T                                         # (2, L)
L = x.shape[1]
pad = GEN - L % GEN if L % GEN else 0
mix = np.concatenate([np.zeros((2, TRIM)), x, np.zeros((2, pad + TRIM))], 1)
sess = ort.InferenceSession(model, providers=["CPUExecutionProvider"])
outs = []
for i in range(0, mix.shape[1] - 2 * TRIM, GEN):
    seg = mix[:, i:i + CHUNK]
    specs = [stft(seg[c])[:DIM_F] for c in range(2)]            # (F, T) complex
    inp_ = np.stack([specs[0].real, specs[0].imag, specs[1].real, specs[1].imag])[None].astype(np.float32)
    o = sess.run(None, {"input": inp_})[0][0]
    ys = []
    for c in range(2):
        S = np.zeros((N_FFT // 2 + 1, o.shape[2]), complex)
        S[:DIM_F] = o[2 * c] + 1j * o[2 * c + 1]
        ys.append(istft(S, CHUNK))
    outs.append(np.stack(ys)[:, TRIM:-TRIM])
voc = np.concatenate(outs, 1)[:, :L] * 1.009
inst = x - voc
sf.write(out_v, voc.T, sr); sf.write(out_i, inst.T, sr)
print("ayrıldı", L / sr, "sn")
