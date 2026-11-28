"""AURA PHONK #01 - original phonk-style track (130 bpm, F minor, ~35 s).

Cowbell lead, sliding 808 bass, trap hats, clap, an "aura" break, and a second drop.
Everything is synthesized here; the track is fully original.
Usage: python aura_phonk_01.py  -> aura_phonk_01.wav / .mp3
"""
import os
import subprocess
import wave

import numpy as np

SR = 44100
BPM = 130
BEAT = 60 / BPM
BAR = 4 * BEAT
S16 = BEAT / 4
DUR = 35.0
HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(7)
N = int(SR * DUR)
out = np.zeros(N)


def note(n):
    return 440 * 2 ** ((n - 69) / 12)


def tl(d):
    return np.arange(int(d * SR)) / SR


def add(sig, start, gain=1.0):
    s = int(start * SR)
    e = min(N, s + len(sig))
    if e > s >= 0:
        out[s:e] += gain * sig[:e - s]


def lp(x, k):
    return np.convolve(x, np.ones(k) / k, mode="same")


def square(f, tt):
    return np.sign(np.sin(2 * np.pi * f * tt))


# ---------------------------------------------------------------- instruments
def cowbell(n, d=0.22, bright=1.0):
    tt = tl(d)
    f = note(n)
    s = square(f, tt) + 0.8 * square(f * 1.483, tt)
    s = s - lp(s, int(6 / bright) + 1)          # crude high-pass, keeps it metallic
    return s * np.exp(-tt * 14) * np.minimum(1, tt / 0.002)


def kick(punch=1.0):
    tt = tl(0.45)
    f = 45 + 160 * np.exp(-tt * 30)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 7)
    return np.tanh(s * 2.5 * punch)


def clap():
    tt = tl(0.3)
    n = rng.standard_normal(len(tt))
    n = n - lp(n, 4)
    env = np.exp(-tt * 18)
    for off in (0.0, 0.012, 0.024):                # three quick slaps
        env += 0.6 * np.exp(-np.maximum(0, tt - off) * 120) * (tt >= off)
    return n * env * 0.5 + 0.3 * np.sin(2 * np.pi * 190 * tt) * np.exp(-tt * 25)


def hat(d=0.05, open_=False):
    tt = tl(0.25 if open_ else d)
    n = rng.standard_normal(len(tt))
    n = n - lp(n, 2)
    return n * np.exp(-tt * (12 if open_ else 70))


def bass808(n, d, glide_to=None):
    tt = tl(d)
    f0 = note(n)
    if glide_to is not None:
        f1 = note(glide_to)
        g = np.clip((tt - d * 0.55) / (d * 0.3), 0, 1)
        f = f0 * (f1 / f0) ** g
    else:
        f = np.full(len(tt), f0)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR)
    env = np.minimum(1, tt / 0.005) * np.exp(-tt * 0.6) * np.minimum(1, (d - tt) / 0.03)
    return np.tanh(s * 2.2) * env


def pad(notes, d):
    tt = tl(d)
    s = sum(np.sin(2 * np.pi * note(n) * dt * tt) + 0.3 * np.sin(4 * np.pi * note(n) * dt * tt)
            for n in notes for dt in (1, 1.005, 0.995))
    return s * np.minimum(1, tt / 0.6) * np.minimum(1, (d - tt) / 0.6) / (3 * len(notes))


def riser(d):
    tt = tl(d)
    f = np.linspace(200, 2400, len(tt))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.4 + rng.standard_normal(len(tt)) * 0.5
    return s * (tt / d) ** 2.5


# ---------------------------------------------------------------- arrangement
# F minor riff (16ths, None = rest) - two bars
RIFF = [77, None, 80, None, 84, 80, None, 79, 77, None, 75, None, 77, 80, 79, None,
        77, None, 80, None, 84, 85, None, 84, 82, None, 80, None, 79, 75, 77, None]
CHORDS = [(65, "F"), (61, "Db"), (63, "Eb"), (60, "C")]     # bass roots per bar (MIDI 41.. via -24)
PAD_CH = {"F": [53, 56, 60], "Db": [49, 53, 56], "Eb": [51, 55, 58], "C": [48, 52, 55]}

INTRO, DROP_A, BREAK, DROP_B = 2, 8, 2, 6           # bars
t0 = 0.05
bars_total = INTRO + DROP_A + BREAK + DROP_B


def section(b):
    if b < INTRO:
        return "intro"
    if b < INTRO + DROP_A:
        return "dropA"
    if b < INTRO + DROP_A + BREAK:
        return "break"
    return "dropB"


for b in range(bars_total):
    bs = t0 + b * BAR
    if bs > DUR:
        break
    sec = section(b)
    root, name = CHORDS[b % 4]
    # cowbell riff
    for k in range(16):
        n = RIFF[(b % 2) * 16 + k]
        if n is None:
            continue
        g = {"intro": 0.10, "dropA": 0.16, "break": 0.12, "dropB": 0.17}[sec]
        add(cowbell(n + (12 if sec == "dropB" and k % 4 == 0 else 0), 0.22,
                    0.6 if sec == "intro" else 1.0), bs + k * S16, g)
    # pad (aura)
    add(pad(PAD_CH[name], BAR + 0.3), bs, 0.10 if sec in ("intro", "break") else 0.06)
    if sec in ("dropA", "dropB"):
        # 808: root with a slide into the next bar's root on the last 8th
        nxt = CHORDS[(b + 1) % 4][0]
        add(bass808(root - 24, BAR * 0.62), bs, 0.45)
        add(bass808(root - 24, BAR * 0.38, glide_to=nxt - 24), bs + BAR * 0.62, 0.45)
        # drums
        for k in (0, 6, 10):
            add(kick(), bs + k * S16, 0.6)
        for k in (4, 12):
            add(clap(), bs + k * S16, 0.45)
        for k in range(16):
            add(hat(), bs + k * S16, 0.10 + 0.04 * (k % 2 == 0))
        if b % 2 == 1:                               # trap hat roll at the end of every 2 bars
            for j in range(6):
                add(hat(0.03), bs + 12 * S16 + j * (S16 * 4 / 6), 0.09)
            add(hat(open_=True), bs + 14 * S16, 0.08)
    if sec == "intro" and b == INTRO - 1:
        add(riser(BAR), bs, 0.25)
    if sec == "break" and b == INTRO + DROP_A + BREAK - 1:
        add(riser(BAR), bs, 0.3)
        for j in range(8):                           # snare build
            add(clap(), bs + BAR * 0.5 + j * S16 * 1.0, 0.15 + 0.03 * j)

# impacts at each drop
for b in (INTRO, INTRO + DROP_A + BREAK):
    tt = tl(2.5)
    boom = np.sin(2 * np.pi * np.cumsum(30 + 90 * np.exp(-tt * 4)) / SR) * np.exp(-tt * 1.5)
    add(boom, t0 + b * BAR, 0.7)

# ---------------------------------------------------------------- master
t = np.arange(N) / SR
out *= np.clip((DUR - t) / 1.2, 0, 1)
out = np.tanh(out * 1.6)                              # phonk-style saturation
out /= np.max(np.abs(out)) * 1.05
dl = int(0.011 * SR)
right = np.concatenate([np.zeros(dl), out[:-dl]]) * 0.75 + out * 0.25
st = (np.stack([out, right], 1) * 32767).astype(np.int16)
wav = os.path.join(HERE, "aura_phonk_01.wav")
with wave.open(wav, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(st.tobytes())
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-codec:a", "libmp3lame", "-b:a", "256k",
                os.path.join(HERE, "aura_phonk_01.mp3")], check=True)
print("drop A at %.2fs, break at %.2fs, drop B at %.2fs" % (
    t0 + INTRO * BAR, t0 + (INTRO + DROP_A) * BAR, t0 + (INTRO + DROP_A + BREAK) * BAR))
