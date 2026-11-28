"""AMMA - Prakash's Theme, FULL SCORE v2 (original, ~100 s).

Built from five feel references (see REFERENCE_NOTES.md; no copied audio or melody):
  KGF mother (#6)      -> slow 84 bpm lullaby, long tender start, love SWELLS to a climax before the loss
  Baahubali #4 (F maj) -> royal warmth of the memories
  Baahubali #5 (D min) -> grief and the long war
  Salaar "Deva" (#7)   -> villain ENTRY in A minor: sparse giant hits, silence, low chants
Sections (used as separate cues in the villain trilogy):
  A  Memories      F major, 84 bpm: santoor + piano -> violin melody -> her humming -> the love swell
  B  The break     cut at the peak, silence, heartbeat, mourning aalaap (D minor)
  C  The fall      cello sings the Amma melody slowly, organ, low choir, accelerating timpani
  D  The entry     A minor, 123 bpm: giant spaced hits, low male chants ("Deva" recipe)
  E  ANDHAKAAR     D minor war, 123 bpm: brass plays the Amma melody as the villain theme, her voice wails
  F  Afterglow     one violin remembers
Usage: python amma_prakash_theme_v2.py
"""
import os
import subprocess
import wave

import numpy as np

import mass_kit as m

HERE = os.path.dirname(os.path.abspath(__file__))

AMMA = [
    [(69, 1), (72, 1), (74, 1.5), (72, 0.5)],
    [(69, 1), (67, 1), (65, 2)],
    [(67, 1), (69, 1), (72, 1), (77, 1)],
    [(76, 1.5), (74, 0.5), (72, 2)],
    [(70, 1), (69, 1), (67, 1), (65, 1)],
    [(67, 1), (69, 1), (72, 2)],
    [(74, 1), (72, 1), (69, 1), (67, 1)],
    [(65, 4)],
]


def phrase(bars, beat, shift=0):
    return [(n + shift, d * beat) for bar in bars for n, d in bar]


B1 = 60 / 84
BAR1 = 4 * B1
T_VIOLIN = 2 * BAR1
T_VOICE = T_VIOLIN + 4 * BAR1
T_SWELL = T_VOICE + 4 * BAR1
T_BREAK = T_SWELL + 3 * BAR1 + 2 * B1          # cut at the very top of the swell
T_WAIL = T_BREAK + 2.2
T_FALL = T_WAIL + 6.5
B_FALL = 1.0
T_ENTRY = T_FALL + 16 * B_FALL
B2 = 60 / 123
BAR2 = 4 * B2
ENTRY_BARS = 4
T_WAR = T_ENTRY + ENTRY_BARS * BAR2
WAR_BARS = 10
T_HIT = T_WAR + WAR_BARS * BAR2
T_AFTER = T_HIT + 1.8
DUR = T_AFTER + 9.0
mx = m.Mix(DUR)

CH = {"F": [53, 57, 60, 65], "Dm": [50, 53, 57, 62], "Bb": [46, 50, 53, 58], "C": [48, 52, 55, 60],
      "Am": [45, 52, 57, 60], "Gm": [43, 50, 55, 58]}
PROG_A = ["F", "Dm", "F", "Dm", "Bb", "C", "Bb", "Am", "Gm", "C", "F", "Dm", "Bb", "C", "Dm", "Bb", "C"]

# ---------------------------------------------------------------- A: memories (with the love swell)
mx.add(m.tanpura(53, T_BREAK + 0.3, 1.7), 0.0, 0.14, 0, 0.35)
b = 0
while b * BAR1 < T_BREAK:
    bs = b * BAR1
    ch = CH[PROG_A[min(b, len(PROG_A) - 1)]]
    swell = bs >= T_SWELL
    arp = [ch[0] - 12, ch[1], ch[2], ch[3], ch[2] + 12, ch[3], ch[2], ch[1]]
    for k, n in enumerate(arp):
        t = bs + k * B1 / 2
        if t < T_BREAK - 0.05:
            mx.add(m.piano(n, 3.0, 0.5 + 0.3 * swell), t, 0.45 + 0.15 * swell, -0.2 + 0.05 * k, 0.45)
            if bs < T_VOICE and k % 2 == 0:
                mx.add(m.santoor(n + 24, 1.6, 0.6), t + 0.02, 0.18, 0.35, 0.4)
    if b >= 2:
        mx.add(m.bowed([(ch[0] - 12, BAR1 + 0.2)], "cello", attack=0.6), bs, 0.25 + 0.15 * swell, -0.3, 0.4)
    if swell:
        mx.add(m.choir([n + 12 for n in ch], BAR1 + 0.3, "ah", 4, 0.6), bs, 0.35)
        mx.add(m.bowed([(ch[2] + 12, BAR1 + 0.1)], "violin", attack=0.5), bs, 0.2, -0.4, 0.4)
        mx.add(m.timpani(ch[0] - 12, 1.5), bs, 0.35)
    b += 1
mx.add(m.bowed(phrase(AMMA[:4], B1), "violin", vib=0.007, attack=0.5), T_VIOLIN, 0.55, 0.15, 0.5)
mx.add(m.voice(phrase(AMMA[4:8], B1), "oo", vib=0.012), T_VOICE, 0.36, 0.0, 0.55)
mx.add(m.bowed(phrase([[(65, 2), (69, 2)], [(72, 4)], [(70, 2), (69, 2)], [(65, 4)]], B1), "violin", attack=0.8),
       T_VOICE, 0.16, 0.4, 0.5)
mx.add(m.choir([53, 57, 60, 65], T_SWELL - T_VOICE, "oo", 3, 2.0), T_VOICE, 0.16)
# the swell: violin + voice together, an octave up, timpani roll + cymbal swell into the cut
swell_line = phrase(AMMA[:4], B1, 12)
cut = T_BREAK - T_SWELL
acc, line = 0.0, []
for n, d in swell_line:
    if acc + d > cut:
        line.append((n, cut - acc))
        break
    line.append((n, d))
    acc += d
mx.add(m.bowed(line, "violin", vib=0.009, attack=0.3, release=0.02), T_SWELL, 0.55, 0.1, 0.5)
mx.add(m.voice(line, "ah", vib=0.015), T_SWELL, 0.3, -0.1, 0.55)
mx.add(m.timpani(41, cut, 1.2) * np.linspace(0.3, 1.0, int(cut * m.SR)), T_SWELL, 0.45)
mx.add(m.cymbal_swell(cut), T_SWELL, 0.5)

# ---------------------------------------------------------------- B: the break
mx.add(m.heartbeat(), T_BREAK + 0.8, 0.9, 0, 0.1)
mx.add(m.heartbeat(), T_BREAK + 1.6, 0.7, 0, 0.1)
mx.add(m.tremolo_strings([38, 45], T_ENTRY - T_BREAK, "cello"), T_BREAK + 1.2, 0.33, 0, 0.3)
mx.add(m.voice([(74, 1.8), (72, 0.5), (69, 1.2), (74, 0.8), (70, 0.6), (69, 1.8)], "ah", glide=0.16, vib=0.02),
       T_WAIL, 0.45, 0.0, 0.7)
mx.add(m.choir([38, 45, 50, 53], T_FALL - T_WAIL + 1, "oo", 3, 1.5), T_WAIL, 0.3)
mx.add(m.piano(38, 5.0, 0.9), T_WAIL, 0.45)
mx.add(m.piano(26, 5.0, 0.9), T_WAIL, 0.35)

# ---------------------------------------------------------------- C: the fall
mx.add(m.bowed(phrase(AMMA[:4], B_FALL, -12), "cello", vib=0.006, attack=0.6), T_FALL, 0.7, -0.1, 0.45)
FALL_CH = [[38, 45, 50, 53], [34, 41, 46, 50], [31, 38, 43, 46], [33, 40, 45, 49]]
for k in range(4):
    bs = T_FALL + k * 4 * B_FALL
    mx.add(m.organ(FALL_CH[k], 4 * B_FALL + 0.4, 1.2), bs, 0.25 + 0.08 * k, 0, 0.4)
    mx.add(m.choir([n + 12 for n in FALL_CH[k]], 4 * B_FALL + 0.3, "oh", 3, 0.8), bs, 0.25 + 0.08 * k, 0, 0.3)
t, step = T_FALL, 2.0
while t < T_ENTRY - 0.4:
    mx.add(m.timpani(38), t, 0.4 + 0.4 * np.clip((t - T_FALL) / (T_ENTRY - T_FALL), 0, 1))
    t += step
    step = max(0.3, step * 0.86)
mx.add(m.bowed([(81, 4.0), (82, 2.0), (86, 2.0)], "violin", vib=0.012, attack=1.0), T_ENTRY - 8.0, 0.22, 0.4, 0.4)
mx.add(m.riser(5.0, 120, 3500), T_ENTRY - 5.0, 0.45)

# ---------------------------------------------------------------- D: the entry (A minor, sparse giant hits)
tt = m.tl(T_WAR - T_ENTRY)
mx.add(m.lowpass(m.saw(55.0, tt) + m.saw(55.4, tt), 180) * np.minimum(1, tt / 0.2), T_ENTRY, 0.5, 0, 0.2)
mx.add(m.choir([33, 40, 45, 48], T_WAR - T_ENTRY, "oh", 4, 0.5), T_ENTRY, 0.4)
for k in range(ENTRY_BARS):
    for beat in (0, 2.5) if k < ENTRY_BARS - 1 else (0, 1.5, 2.5, 3.25):
        tb = T_ENTRY + k * BAR2 + beat * B2
        mx.add(m.taiko(0.55), tb, 1.0)
        mx.add(m.timpani(33, 1.6), tb, 0.7)
        mx.add(m.braam([21, 28, 33], 1.8), tb, 0.55)
        mx.add(m.chant_hey(40), tb, 0.55, 0, 0.5)
mx.add(m.bowed([(93, T_WAR - T_ENTRY)], "violin", vib=0.004, attack=2.0), T_ENTRY, 0.1, 0.5, 0.4)

# ---------------------------------------------------------------- E: ANDHAKAAR (D minor war)
WAR_CH = [([50, 53, 57, 62], 38), ([46, 50, 53, 58], 34), ([43, 50, 55, 58], 31), ([45, 49, 52, 57], 33)]
for k in range(WAR_BARS):
    bs = T_WAR + k * BAR2
    ch, root = WAR_CH[k % 4]
    big = k >= 4
    mx.add(m.choir(ch, BAR2 + 0.3, "ah", 4, 0.1), bs, 0.45 + 0.1 * big)
    mx.add(m.organ([n - 12 for n in ch], BAR2 + 0.2, 0.05), bs, 0.2)
    mx.add(m.sub808(root - 12, BAR2 * 0.95), bs, 0.5, 0, 0.05)
    mx.add(m.timpani(root + 12, 1.5), bs, 0.7)
    for beat in (0, 0.75, 1.5, 2, 3, 3.5):
        mx.add(m.taiko(0.9 if beat in (0, 2) else 1.2), bs + beat * B2, 0.55 if beat in (0, 2) else 0.35,
               0.25 * (1 if beat % 1 else -1), 0.2)
    for e in range(8):
        mx.add(m.dhol_slap(), bs + e * B2 / 2, 0.12 + 0.08 * (e % 2), 0.35 * (1 if e % 2 else -1), 0.1)
    if k % 4 == 0:
        mx.add(m.cymbal(3.5), bs, 0.45)
        mx.add(m.braam([root - 12, root - 5, root], 2.5), bs, 0.7)
    if big:
        mx.add(m.chant_hey(45), bs + 2 * B2, 0.5, 0, 0.4)
    if k >= WAR_BARS - 3:
        for e in range(8):
            mx.add(m.piano(38, 0.6, 1.0), bs + e * B2 / 2, 0.35, -0.2, 0.2)
            mx.add(m.piano(50, 0.6, 0.9), bs + e * B2 / 2, 0.25, 0.2, 0.2)
for rep in range(2):
    tm = T_WAR + rep * 4 * BAR2 + (0 if rep == 0 else BAR2)
    for n, d in phrase(AMMA[:4], B2):
        if tm > T_HIT - 0.2:
            break
        shift = -12 if rep == 0 else 0
        mx.add(m.brass(n + shift, d * 0.95), tm, 0.5, 0.1, 0.35)
        mx.add(m.brass(n + shift - 12, d * 0.95, 0.7), tm, 0.3, -0.1, 0.35)
        tm += d
mx.add(m.voice(phrase(AMMA[:3], B2, 12), "ah", glide=0.08, vib=0.02), T_WAR + 5 * BAR2, 0.4, 0.0, 0.6)
for f in range(8):
    mx.add(m.taiko(1.2 + 0.08 * f), T_HIT - 2 * B2 + f * B2 / 4, 0.4)
mx.add(m.braam([26, 33, 38, 41, 45], 4.0), T_HIT, 1.4)
mx.add(m.timpani(26, 3.0, 0.5), T_HIT, 1.0)
mx.add(m.taiko(0.55), T_HIT, 1.3)
mx.add(m.cymbal(4.5), T_HIT, 0.6)
mx.add(m.choir([38, 45, 50, 53, 57], 3.0, "ah", 4, 0.05), T_HIT, 0.55)

# ---------------------------------------------------------------- F: afterglow
for k, n in enumerate((50, 57, 65)):
    mx.add(m.piano(n, 7.0, 0.5 - 0.05 * k), T_AFTER + 0.05 * k, 0.35 - 0.05 * k)
mx.add(m.bowed(phrase([AMMA[6], AMMA[7]], B1 * 1.1), "violin", vib=0.008, attack=0.8, release=1.5),
       T_AFTER + 0.6, 0.45, 0.15, 0.6)

out = mx.render(tail=2.8, drive=1.25, fade_out=2.5)
wav = os.path.join(HERE, "amma_prakash_theme_v2.wav")
with wave.open(wav, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(m.SR)
    w.writeframes((out.T * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-codec:a", "libmp3lame", "-b:a", "256k",
                os.path.join(HERE, "amma_prakash_theme_v2.mp3")], check=True)
CUES = dict(violin=T_VIOLIN, voice=T_VOICE, swell=T_SWELL, BREAK=T_BREAK, wail=T_WAIL, fall=T_FALL,
            ENTRY=T_ENTRY, WAR=T_WAR, HIT=T_HIT, after=T_AFTER, end=DUR)
print(" | ".join("%s %.1f" % kv for kv in CUES.items()))
