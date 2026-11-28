"""DHARMA RISING - original fusion BGM (~73 s).

Combines two "recipes" from REFERENCE_NOTES.md (feel only, no copied audio or melody):
  Varanasi-style epic build (A minor, slow rise, choir + strings + braams)
  -> Raaka-style royal hero drop (F major, half-time groove, 808, chants, brass).
Usage: python dharma_rising_fusion.py  -> dharma_rising_fusion.mp3
"""
import os
import subprocess
import wave

import numpy as np

import mass_kit as m

HERE = os.path.dirname(os.path.abspath(__file__))
BEAT = 60 / 144
BAR = 4 * BEAT
S16 = BEAT / 4
INTRO, BUILD, DROP1, BREAK, DROP2 = 7, 10, 10, 5, 10          # bars
T_BUILD = INTRO * BAR
T_DROP1 = T_BUILD + BUILD * BAR
T_BREAK = T_DROP1 + DROP1 * BAR
T_DROP2 = T_BREAK + BREAK * BAR
T_OUTRO = T_DROP2 + DROP2 * BAR
DUR = T_OUTRO + 4.5
mx = m.Mix(DUR)

# ---------------------------------------------------------------- intro: A minor, distant and sacred
mx.add(m.tanpura(57, T_BUILD + 2, 1.5), 0.0, 0.3, 0, 0.35)
tt = m.tl(T_DROP1)
drone = m.lowpass(m.saw(55.0, tt) + m.saw(55.3, tt), 220) * np.minimum(1, tt / 3.0)
mx.add(drone, 0, 0.35, 0, 0.25)
mx.add(m.choir([45, 52, 57], T_BUILD + 1, "oh", 3, 3.0), 1.0, 0.35)
for b in range(0, INTRO, 2):
    mx.add(m.taiko(0.7), b * BAR, 0.45 + 0.05 * b)
mx.add(m.bansuri([(69, 0.8), (72, 0.4), (71, 0.4), (69, 0.8), (67, 0.6), (64, 1.4),
                  (65, 0.6), (67, 0.4), (64, 0.4), (62, 0.6), (64, 2.0)], 0.1, 0.012), 2.6, 0.28, 0.2, 0.5)

# ---------------------------------------------------------------- build: Am - F - Dm - E, tightening
BUILD_CH = [([45, 52, 57, 60], 33), ([41, 48, 53, 57], 29), ([38, 45, 50, 53], 26), ([40, 47, 52, 56], 28)]
patt = [0, 0, 12, 0, 3, 0, 12, 0, 2, 0, 10, 0, 3, 0, 7, 0]
for b in range(BUILD):
    bs = T_BUILD + b * BAR
    ch, root = BUILD_CH[b % 4]
    prog = b / BUILD
    for k in range(16):
        mx.add(m.strings_stacc(root + 24 + patt[k], 0.1), bs + k * S16, 0.1 + 0.18 * prog,
               0.3 * (1 if k % 2 else -1), 0.25)
    mx.add(m.choir(ch, BAR + 0.5, "ah", 3, 0.6), bs, 0.3 + 0.25 * prog)
    if b % 2 == 0:
        mx.add(m.braam([ch[0] - 12, ch[0] - 5, ch[0]], 2.6), bs, 0.55 + 0.3 * prog)
        mx.add(m.taiko(0.7), bs, 0.7)
    beats = 2 if prog < 0.4 else (4 if prog < 0.75 else 8)
    for k in range(beats):
        mx.add(m.dhol_bass(), bs + k * BAR / beats, 0.3 + 0.3 * prog)
        if prog > 0.4:
            mx.add(m.dhol_slap(), bs + k * BAR / beats + BAR / beats / 2, 0.15 + 0.15 * prog, 0.3)
mx.add(m.riser(3 * BAR, 150, 3500), T_DROP1 - 3 * BAR, 0.45)
for k in range(8):                                       # snare-roll style clap build
    mx.add(m.clap(), T_DROP1 - BAR + k * BEAT / 2, 0.12 + 0.05 * k, 0, 0.3)
mx.add(m.heartbeat(), T_DROP1 - 1.1, 0.8, 0, 0.1)


# ---------------------------------------------------------------- the royal hero groove (F major)
DROP_CH = [("F", [53, 57, 60, 65], 41), ("Dm", [50, 53, 57, 62], 38), ("Bb", [46, 50, 53, 58], 34),
           ("C", [48, 52, 55, 60], 36)]
THEME = [(65, 1), (72, 1), (69, 0.5), (70, 0.5), (72, 1),
         (74, 1.5), (72, 0.5), (70, 1), (69, 1),
         (67, 1), (69, 0.5), (70, 0.5), (72, 1), (77, 1),
         (76, 1.5), (74, 0.5), (72, 2)]


def drop(t0, bars, big):
    for b in range(bars):
        bs = t0 + b * BAR
        name, ch, root = DROP_CH[b % 4]
        nxt = DROP_CH[(b + 1) % 4][2]
        mx.add(m.choir(ch, BAR + 0.4, "ah", 3, 0.2), bs, 0.4 + 0.1 * big)
        mx.add(m.sub808(root - 12, BAR * 0.7), bs, 0.55, 0, 0.05)
        mx.add(m.sub808(root - 12, BAR * 0.3, glide_to=nxt - 12), bs + BAR * 0.7, 0.5, 0, 0.05)
        for beat in (0, 1.5, 2.75):
            mx.add(m.kick(), bs + beat * BEAT, 0.75, 0, 0.05)
        for beat in (0, 2.5):
            mx.add(m.dhol_bass(0.9), bs + beat * BEAT, 0.5)
        mx.add(m.clap(), bs + 2 * BEAT, 0.6, 0, 0.35)
        mx.add(m.taiko(1.1), bs + 2 * BEAT, 0.35 + 0.15 * big)
        for e in range(8):
            mx.add(m.dhol_slap(), bs + e * BEAT / 2, 0.15 + 0.12 * (e % 4 == 3), 0.35 * (1 if e % 2 else -1), 0.1)
        if big:
            for e in range(16):
                mx.add(m.dhol_slap(0.08), bs + e * S16, 0.07, -0.4 if e % 2 else 0.4, 0.05)
        if b % 2 == 1 or (big and b % 2 == 0):
            mx.add(m.chant_hey(50), bs + 2 * BEAT, 0.55 + 0.15 * big, 0, 0.4)
        if b % 4 == 3:
            for f in range(6):
                mx.add(m.taiko(1.3 + 0.1 * f), bs + 2.5 * BEAT + f * BEAT / 4, 0.35 + 0.1 * big)
    tm = t0
    while tm < t0 + bars * BAR - 0.3:
        for n, d in THEME:
            if tm > t0 + bars * BAR - 0.3:
                break
            mx.add(m.brass(n + 12 * big, d * BEAT * 0.95), tm, 0.45, 0.1, 0.35)
            mx.add(m.brass(n - 12 + 12 * big, d * BEAT * 0.95, 0.7), tm, 0.25, -0.1, 0.35)
            if big:
                mx.add(m.bansuri([(n + 12, d * BEAT * 0.9)], 0.05, 0.01), tm, 0.12, 0.25, 0.4)
            tm += d * BEAT
    for t in (t0,):
        mx.add(m.braam([41, 48, 53, 57, 60], 3.5), t, 1.1)
        mx.add(m.taiko(0.6), t, 1.1)
        mx.add(m.cymbal(4), t, 0.6)
        mx.add(m.chant_hey(46), t, 0.8, 0, 0.5)


drop(T_DROP1, DROP1, 0)

# ---------------------------------------------------------------- break: the theme, alone and sacred
mx.add(m.tanpura(53, BREAK * BAR + 1, 1.4), T_BREAK, 0.3, 0, 0.35)
mx.add(m.choir([41, 48, 53, 57], BREAK * BAR, "oh", 4, 1.0), T_BREAK, 0.45)
mx.add(m.bansuri([(n, d * BEAT * 1.15) for n, d in THEME[:9]], 0.1, 0.012), T_BREAK + 0.3, 0.3, 0.15, 0.55)
mx.add(m.riser(2 * BAR, 200, 3500), T_DROP2 - 2 * BAR, 0.45)
for k in range(16):
    mx.add(m.clap(), T_DROP2 - BAR + k * S16, 0.08 + 0.03 * k, 0, 0.3)
mx.add(m.taiko(0.9), T_DROP2 - BEAT, 0.6)

drop(T_DROP2, DROP2, 1)

# ---------------------------------------------------------------- outro
mx.add(m.braam([41, 48, 53, 57, 60, 65], 4.5), T_OUTRO, 1.2)
mx.add(m.taiko(0.6), T_OUTRO, 1.2)
mx.add(m.cymbal(4.5), T_OUTRO, 0.6)
mx.add(m.chant_hey(46), T_OUTRO, 0.9, 0, 0.6)
mx.add(m.choir([53, 57, 60, 65, 69], 4.5, "ah", 4, 0.1), T_OUTRO, 0.55)
for k, n in enumerate((77, 81, 84, 89)):
    mx.add(m.bell(float(m.note(n)), 3.0), T_OUTRO + 0.3 + k * 0.12, 0.07, 0.25 * (k - 1.5))

out = mx.render(tail=2.4, drive=1.4, fade_out=2.5)
wav = os.path.join(HERE, "dharma_rising_fusion.wav")
with wave.open(wav, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(m.SR)
    w.writeframes((out.T * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-codec:a", "libmp3lame", "-b:a", "256k",
                os.path.join(HERE, "dharma_rising_fusion.mp3")], check=True)
print("build %.1fs | drop1 %.1fs | break %.1fs | drop2 %.1fs | outro %.1fs | total %.1fs"
      % (T_BUILD, T_DROP1, T_BREAK, T_DROP2, T_OUTRO, DUR))
