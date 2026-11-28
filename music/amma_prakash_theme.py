"""AMMA - Prakash's Theme (original, ~88 s): from a mother's lullaby to the birth of darkness.

Feel references (REFERENCE_NOTES #4, #5): F major (royal/noble) and D minor (tragic) share the same
notes, so the SAME original Amma melody is sung happily in F major and turns tragic over D minor.

  A  Memories (F major, 72 bpm): piano -> solo violin melody -> female voice hums the second half
  B  The loss: the voice breaks mid-phrase, silence, heartbeat, a mourning aalaap over low strings
  C  The fall (D minor): cello plays the Amma melody slowly, organ + low choir, timpani accelerates
  D  ANDHAKAAR (D minor, 111 bpm): war drums, brass plays the Amma melody as the villain theme,
     choir, 808, the voice wails above it all
  E  Afterglow: one violin remembers the last phrase
Usage: python amma_prakash_theme.py
"""
import os
import subprocess
import wave

import numpy as np

import mass_kit as m

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- the Amma melody (original, F major)
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


B1 = 60 / 72                     # memories tempo
BAR1 = 4 * B1
T_VIOLIN = 2 * BAR1              # after 2 bars of piano
T_VOICE = T_VIOLIN + 4 * BAR1
T_BREAK = T_VOICE + 2 * BAR1 + 2 * B1          # the voice is cut in bar 7, after two notes
T_WAIL = T_BREAK + 2.2
T_FALL = T_WAIL + 6.5
B_FALL = 1.0
T_WAR = T_FALL + 16 * B_FALL
B2 = 60 / 111                    # war tempo
BAR2 = 4 * B2
WAR_BARS = 10
T_HIT = T_WAR + WAR_BARS * BAR2
T_AFTER = T_HIT + 1.6
DUR = T_AFTER + 9.0
mx = m.Mix(DUR)

HAPPY = {"F": [53, 57, 60, 65], "Dm": [50, 53, 57, 62], "Bb": [46, 50, 53, 58], "C": [48, 52, 55, 60],
         "Am": [45, 52, 57, 60], "Gm": [43, 50, 55, 58]}
HAPPY_PROG = ["F", "Dm", "Bb", "C", "Bb", "Am", "Gm", "C", "F"]

# ---------------------------------------------------------------- A: memories
mx.add(m.tanpura(53, T_BREAK + 0.5, 1.6), 0.0, 0.15, 0, 0.35)
for b in range(int(T_BREAK / BAR1) + 1):
    bs = b * BAR1
    if bs >= T_BREAK:
        break
    ch = HAPPY[HAPPY_PROG[min(b, len(HAPPY_PROG) - 1)]] if b >= 2 else HAPPY["F" if b == 0 else "Dm"]
    arp = [ch[0] - 12, ch[1], ch[2], ch[3], ch[2] + 12, ch[3], ch[2], ch[1]]
    for k, n in enumerate(arp):
        t = bs + k * B1 / 2
        if t < T_BREAK - 0.05:
            mx.add(m.piano(n, 3.0, 0.55 if k else 0.7), t, 0.5, -0.2 + 0.05 * k, 0.45)
    if b >= 2:
        mx.add(m.bowed([(ch[0] - 12, BAR1 + 0.2)], "cello", attack=0.6), bs, 0.25, -0.3, 0.4)
mx.add(m.bowed(phrase(AMMA[:4], B1), "violin", vib=0.007, attack=0.5), T_VIOLIN, 0.55, 0.15, 0.5)
voice_line = phrase(AMMA[4:6], B1) + phrase([AMMA[6][:2]], B1)
mx.add(m.voice(voice_line, "oo", vib=0.012), T_VOICE, 0.38, 0.0, 0.55)
mx.add(m.bowed(phrase([[(65, 2), (69, 2)], [(72, 4)], [(70, 2), (69, 2)]], B1), "violin", attack=0.8),
       T_VOICE, 0.18, 0.4, 0.5)
# string pad grows warm under the voice
mx.add(m.choir([53, 57, 60, 65], T_BREAK - T_VOICE, "oo", 3, 2.0), T_VOICE, 0.18)

# ---------------------------------------------------------------- B: the loss
mx.add(m.heartbeat(), T_BREAK + 0.8, 0.9, 0, 0.1)
mx.add(m.heartbeat(), T_BREAK + 1.6, 0.7, 0, 0.1)
mx.add(m.tremolo_strings([38, 45], DUR - T_BREAK - 2, "cello"), T_BREAK + 1.2, 0.35, 0, 0.3)
mx.add(m.voice([(74, 1.8), (72, 0.5), (69, 1.2), (74, 0.8), (70, 0.6), (69, 1.8)], "ah", glide=0.16, vib=0.02),
       T_WAIL, 0.45, 0.0, 0.7)
mx.add(m.choir([38, 45, 50, 53], T_FALL - T_WAIL + 1, "oo", 3, 1.5), T_WAIL, 0.3)
mx.add(m.piano(38, 5.0, 0.9), T_WAIL, 0.45)
mx.add(m.piano(26, 5.0, 0.9), T_WAIL, 0.35)

# ---------------------------------------------------------------- C: the fall (D minor)
mx.add(m.bowed(phrase(AMMA[:4], B_FALL, -12), "cello", vib=0.006, attack=0.6), T_FALL, 0.7, -0.1, 0.45)
FALL_CH = [[38, 45, 50, 53], [34, 41, 46, 50], [31, 38, 43, 46], [33, 40, 45, 49]]
for b in range(4):
    bs = T_FALL + b * 4 * B_FALL
    mx.add(m.organ(FALL_CH[b], 4 * B_FALL + 0.4, 1.2), bs, 0.25 + 0.08 * b, 0, 0.4)
    mx.add(m.choir([n + 12 for n in FALL_CH[b]], 4 * B_FALL + 0.3, "oh", 3, 0.8), bs, 0.25 + 0.08 * b, 0, 0.3)
t, step = T_FALL, 2.0
while t < T_WAR - 0.2:                          # timpani heartbeat that keeps accelerating
    mx.add(m.timpani(38), t, 0.4 + 0.4 * m.np.clip((t - T_FALL) / (T_WAR - T_FALL), 0, 1))
    t += step
    step = max(0.27, step * 0.86)
j, t = 0, T_FALL + 8 * B_FALL
while t < T_WAR:                                 # war-tempo string ostinato creeping in
    n = [50, 50, 62, 50, 53, 50, 57, 50][j % 8]
    mx.add(m.strings_stacc(n, 0.1), t, 0.08 + 0.18 * (t - T_FALL - 8) / 8, 0.3 * (1 if j % 2 else -1), 0.2)
    j += 1
    t += B2 / 4
mx.add(m.bowed([(81, 4.0), (82, 2.0), (86, 2.0)], "violin", vib=0.012, attack=1.0), T_WAR - 8.0, 0.22, 0.4, 0.4)
mx.add(m.riser(5.0, 120, 3500), T_WAR - 5.0, 0.45)
mx.add(m.heartbeat(), T_WAR - 1.2, 0.9, 0, 0.1)

# ---------------------------------------------------------------- D: ANDHAKAAR (111 bpm, D minor)
WAR_CH = [("Dm", [50, 53, 57, 62], 38), ("Bb", [46, 50, 53, 58], 34), ("Gm", [43, 50, 55, 58], 31),
          ("A", [45, 49, 52, 57], 33)]
for b in range(WAR_BARS):
    bs = T_WAR + b * BAR2
    name, ch, root = WAR_CH[b % 4]
    big = b >= 4
    mx.add(m.choir(ch, BAR2 + 0.3, "ah", 4, 0.1), bs, 0.45 + 0.1 * big)
    mx.add(m.organ([n - 12 for n in ch], BAR2 + 0.2, 0.05), bs, 0.2)
    mx.add(m.sub808(root - 12, BAR2 * 0.95), bs, 0.5, 0, 0.05)
    mx.add(m.timpani(root + 12, 1.5), bs, 0.7)
    for beat in (0, 0.75, 1.5, 2, 3, 3.5):                 # war rhythm on the taiko ensemble
        mx.add(m.taiko(0.9 if beat in (0, 2) else 1.2), bs + beat * B2, 0.55 if beat in (0, 2) else 0.35,
               0.25 * (1 if beat % 1 else -1), 0.2)
    for e in range(8):
        mx.add(m.dhol_slap(), bs + e * B2 / 2, 0.12 + 0.08 * (e % 2), 0.35 * (1 if e % 2 else -1), 0.1)
    if b % 4 == 0:
        mx.add(m.cymbal(3.5), bs, 0.45)
        mx.add(m.braam([root - 12, root - 5, root], 2.5), bs, 0.7)
    if big:
        mx.add(m.chant_hey(45), bs + 2 * B2, 0.5, 0, 0.4)
    if b >= WAR_BARS - 3:                                   # hammering piano octaves at the climax
        for e in range(8):
            mx.add(m.piano(38, 0.6, 1.0), bs + e * B2 / 2, 0.35, -0.2, 0.2)
            mx.add(m.piano(50, 0.6, 0.9), bs + e * B2 / 2, 0.25, 0.2, 0.2)
# the Amma melody becomes the villain theme on brass (twice; second time an octave up with the voice)
for rep in range(2):
    tm = T_WAR + rep * 4 * BAR2 + (0 if rep == 0 else BAR2)
    for n, d in phrase(AMMA[:4], B2):
        if tm > T_HIT - 0.2:
            break
        shift = -12 if rep == 0 else 0
        mx.add(m.brass(n + shift, d * 0.95), tm, 0.5, 0.1, 0.35)
        mx.add(m.brass(n + shift - 12, d * 0.95, 0.7), tm, 0.3, -0.1, 0.35)
        tm += d
mx.add(m.voice(phrase(AMMA[:3], B2 * 1.0, 12), "ah", glide=0.08, vib=0.02), T_WAR + 5 * BAR2, 0.4, 0.0, 0.6)
for f in range(8):
    mx.add(m.taiko(1.2 + 0.08 * f), T_HIT - 2 * B2 + f * B2 / 4, 0.4)
mx.add(m.braam([26, 33, 38, 41, 45], 4.0), T_HIT, 1.4)
mx.add(m.timpani(26, 3.0, 0.5), T_HIT, 1.0)
mx.add(m.taiko(0.55), T_HIT, 1.3)
mx.add(m.cymbal(4.5), T_HIT, 0.6)
mx.add(m.choir([38, 45, 50, 53, 57], 3.0, "ah", 4, 0.05), T_HIT, 0.55)

# ---------------------------------------------------------------- E: afterglow
mx.add(m.piano(50, 7.0, 0.5), T_AFTER, 0.35)
mx.add(m.piano(57, 7.0, 0.45), T_AFTER + 0.05, 0.3)
mx.add(m.piano(65, 7.0, 0.4), T_AFTER + 0.1, 0.25)
mx.add(m.bowed(phrase([AMMA[6], AMMA[7]], B1 * 1.1), "violin", vib=0.008, attack=0.8, release=1.5),
       T_AFTER + 0.6, 0.45, 0.15, 0.6)

out = mx.render(tail=2.8, drive=1.25, fade_out=2.5)
wav = os.path.join(HERE, "amma_prakash_theme.wav")
with wave.open(wav, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(m.SR)
    w.writeframes((out.T * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-codec:a", "libmp3lame", "-b:a", "256k",
                os.path.join(HERE, "amma_prakash_theme.mp3")], check=True)
print("violin %.1f | voice %.1f | BREAK %.1f | wail %.1f | fall %.1f | WAR %.1f | hit %.1f | after %.1f | end %.1f"
      % (T_VIOLIN, T_VOICE, T_BREAK, T_WAIL, T_FALL, T_WAR, T_HIT, T_AFTER, DUR))
