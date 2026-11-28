"""WELCOME HOME - calm channel-welcome Short (1080x1920, 24 s), vintage film look.

One diya lights the dark; gentle words; Guardians and Bindu glimpse by; "Welcome home."
Score: original lo-fi (soft keys, dusty drums, vinyl crackle) with tanpura + bansuri.
Usage: python render.py
"""
import importlib.util
import math
import os
import random
import subprocess
import sys
import wave
from multiprocessing import Pool

import cairo
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


kit = _load("trailer_kit", "../trailer/render.py")
agni_ep = _load("agni_ep", "../ep01_agni_origin/render.py")
bindu_ep = _load("bindu_ep", "../ep05_bindu_origin/render.py")
sys.path.insert(0, os.path.join(HERE, "..", "..", "music"))
glow, hexc, text, prog, ease_io, ease_out, lerp, TAU = (kit.glow, kit.hexc, kit.text, kit.prog, kit.ease_io,
                                                         kit.ease_out, kit.lerp, kit.TAU)
FONT, FONT_BLACK = kit.FONT, kit.FONT_BLACK

W, H, FPS, DUR = 1080, 1920, 30, 24.0
NFRAMES = int(FPS * DUR)
FRAMES = os.path.join(HERE, "frames")
GOLD = hexc("#ffd166")
CREAM = (1.0, 0.95, 0.86)
DIYA_X, DIYA_Y = 555, 1283
T_LIGHT = 1.2

LINES = [  # (t0, t1, lines, style)
    (2.2, 5.6, ["Tired of the noise?"], "soft"),
    (6.0, 9.2, ["This is a quiet place."], "soft"),
    (9.6, 12.8, ["Old stories.", "New music."], "soft"),
    (13.2, 16.4, ["No voices.", "You are the narrator."], "soft"),
    (16.8, 19.8, ["Stay as long as you like."], "soft"),
]
T_WELCOME = 20.2

R = random.Random(9)
BOKEH = [(R.uniform(0, W), R.uniform(0, H), R.uniform(10, 46), R.uniform(8, 26), R.uniform(0, TAU),
          R.uniform(0.15, 0.45)) for _ in range(46)]
STARS = [(R.uniform(0, W), R.uniform(0, 900), R.uniform(0.8, 2.4), R.uniform(0, TAU)) for _ in range(160)]


def vintage(ctx, t):
    """Sepia wash, film flicker, scratches, dust specks."""
    ctx.set_source_rgba(0.45, 0.28, 0.1, 0.16)
    ctx.paint()
    r = random.Random(int(t * FPS))
    fl = r.uniform(-0.035, 0.035)
    ctx.set_source_rgba(1, 0.95, 0.85, max(0, fl)) if fl > 0 else ctx.set_source_rgba(0, 0, 0, -fl)
    ctx.paint()
    for _ in range(r.randint(0, 2)):
        x = r.uniform(0, W)
        ctx.set_source_rgba(1, 0.95, 0.85, r.uniform(0.05, 0.14))
        ctx.set_line_width(r.uniform(1, 2.2))
        ctx.move_to(x, 0)
        ctx.line_to(x + r.uniform(-20, 20), H)
        ctx.stroke()
    for _ in range(r.randint(2, 6)):
        ctx.set_source_rgba(0.1, 0.07, 0.04, r.uniform(0.2, 0.5))
        ctx.arc(r.uniform(0, W), r.uniform(0, H), r.uniform(1, 3.5), 0, TAU)
        ctx.fill()


def draw_frame(i):
    t = i / FPS
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    warm = ease_io(prog(t, T_LIGHT, 8.0))
    # background: from black to a deep warm night
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, *(c * warm for c in hexc("#120a18")))
    g.add_color_stop_rgb(0.6, *(c * warm for c in hexc("#2a1610")))
    g.add_color_stop_rgb(1, *(c * warm for c in hexc("#0c0806")))
    ctx.set_source(g)
    ctx.paint()
    sa = ease_io(prog(t, 6.0, 9.0))
    for sx, sy, r, ph in STARS:
        if sa <= 0:
            break
        ctx.set_source_rgba(1, 0.95, 0.85, sa * (0.4 + 0.4 * math.sin(t * 1.5 + ph)))
        ctx.arc(sx, sy, r, 0, TAU)
        ctx.fill()
    # slow camera drift
    z = 1.0 + 0.04 * t / DUR
    ctx.save()
    ctx.translate(W / 2, DIYA_Y)
    ctx.scale(z, z)
    ctx.translate(-W / 2, -DIYA_Y)
    # far glimpses of the Guardians (old stories)
    ga = ease_io(prog(t, 9.6, 11.0)) * (1 - 0.6 * ease_io(prog(t, 16.0, 17.5)))
    if ga > 0:
        ctx.push_group()
        for h, hx in zip(kit.HEROES, (180, 340, 740, 900)):
            u = 120
            bottom = max(l[-1][1] for l in kit.POSES[h["pose"]]["legs"])
            glow(ctx, hx, 1350 - 0.9 * u, 150, h["col"], 0.35)
            kit.draw_hero(ctx, h, hx, 1350 - bottom * u, u, t, 0.8)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(0.55 * ga)
    # floor + table glow
    ctx.set_source_rgba(0.05, 0.03, 0.02, warm)
    ctx.rectangle(-100, 1350, W + 200, 700)
    ctx.fill()
    light = ease_out(prog(t, T_LIGHT, T_LIGHT + 1.2))
    if light > 0:
        glow(ctx, DIYA_X, DIYA_Y - 30, 900 * light * (1 + 0.04 * math.sin(t * 2.3)), hexc("#ff9a40"), 0.42)
        ctx.save()
        ctx.translate(DIYA_X, 1352)
        ctx.scale(1, 0.25)
        glow(ctx, 0, 0, 500 * light, hexc("#ffb050"), 0.5)
        ctx.restore()
    # bokeh dust floating in the warm light
    for bx, by, rr, sp, ph, a in BOKEH:
        y = (by - sp * t) % (H + 100) - 50
        x = bx + 18 * math.sin(t * 0.4 + ph)
        glow(ctx, x, y, rr, hexc("#ffcf88"), a * light * 0.6)
    # the diya: a spark, then a flame
    ctx.save()
    ctx.translate(DIYA_X, DIYA_Y)
    ctx.scale(2.4, 2.4)
    ctx.translate(-DIYA_X, -DIYA_Y)
    if t < T_LIGHT:
        sp = ease_out(prog(t, 0.4, T_LIGHT))
        glow(ctx, DIYA_X + 30, DIYA_Y - 14, 40 * sp, GOLD, sp)
        agni_ep.diya(ctx, DIYA_X - 30, DIYA_Y + 8, 0.0, t)
    else:
        agni_ep.diya(ctx, DIYA_X - 30, DIYA_Y + 8, 0.25 + 0.75 * light, t)
    ctx.restore()
    # Bindu joins beside the lamp
    ba = ease_io(prog(t, 16.8, 18.0))
    if ba > 0:
        hop = 30 * math.sin(math.pi * prog(t, 16.8, 17.4))
        eyes = 1.0
        for bt in (18.6, 21.4):
            if abs(t - bt) < 0.08:
                eyes = 0.1
        ctx.push_group()
        bindu_ep.bindu(ctx, 790, 1352 - hop, 70, t, eyes, (-0.7, -0.1), "smile", 0.7, 1.0, 0.0)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(ba)
    ctx.restore()

    # words
    for t0, t1, ls, style in LINES:
        a = ease_io(prog(t, t0, t0 + 0.9)) * (1 - ease_io(prog(t, t1 - 0.8, t1)))
        if a <= 0:
            continue
        for j, ln in enumerate(ls):
            text(ctx, ln, W / 2, 560 + j * 96, 70, CREAM, a, FONT, 2)
    if t >= T_WELCOME:
        a = ease_io(prog(t, T_WELCOME, T_WELCOME + 1.2)) * (1 - ease_io(prog(t, DUR - 0.9, DUR)))
        text(ctx, "Welcome home.", W / 2, 600, 104, GOLD, a, FONT_BLACK, 3, glow_col=hexc("#ff9a40"))
        b = ease_io(prog(t, T_WELCOME + 1.0, T_WELCOME + 2.0)) * (1 - ease_io(prog(t, DUR - 0.9, DUR)))
        text(ctx, "G U A R D I A N S   O F   T H E   L A S T   L I G H T", W / 2, 700, 26, CREAM, b, FONT, 2)

    vintage(ctx, t)
    v = cairo.RadialGradient(W / 2, H / 2, H * 0.25, W / 2, H / 2, H * 0.7)
    v.add_color_stop_rgba(0, 0, 0, 0, 0)
    v.add_color_stop_rgba(1, 0.05, 0.02, 0.0, 0.7)
    ctx.set_source(v)
    ctx.paint()
    surf.flush()
    kit.post(surf, t, 0)
    surf.mark_dirty()
    surf.write_to_png(os.path.join(FRAMES, f"f{i:04d}.png"))


# ------------------------------------------------------------------ lo-fi score
def make_audio(path):
    import mass_kit as m
    BPM = 80
    beat = 60 / BPM
    bar = 4 * beat
    mx = m.Mix(DUR)

    def keys(notes, d):
        """Soft electric-piano chord (sine + bell partial, slow tremolo, low-passed)."""
        tt = m.tl(d)
        s = np.zeros(len(tt))
        for n in notes:
            f = float(m.note(n))
            s += (np.sin(m.TAU * f * tt) + 0.25 * np.sin(m.TAU * 2 * f * tt) * np.exp(-tt * 3)
                  + 0.1 * np.sin(m.TAU * 7.1 * f * tt) * np.exp(-tt * 9))
        s *= (1 + 0.15 * np.sin(m.TAU * 4.2 * tt)) * np.exp(-tt * 0.5) * np.minimum(1, tt / 0.01)
        s *= np.clip((d - tt) / 0.3, 0, 1)
        return m.lowpass(s / len(notes), 2400)

    def soft_kick():
        tt = m.tl(0.35)
        f = 48 + 70 * np.exp(-tt * 25)
        return np.sin(m.TAU * np.cumsum(f) / m.SR) * np.exp(-tt * 9)

    def rim():
        tt = m.tl(0.12)
        return m.bandpass(m.noise(0.12), 1700, 3) * np.exp(-tt * 35) + 0.4 * np.sin(m.TAU * 820 * tt) * np.exp(-tt * 50)

    def shaker():
        tt = m.tl(0.08)
        return m.highpass(m.noise(0.08), 6000) * np.exp(-tt * 45)

    # vinyl crackle bed
    n = int(DUR * m.SR)
    crackle = np.zeros(n)
    idx = np.random.default_rng(4).integers(0, n, 900)
    crackle[idx] = np.random.default_rng(5).uniform(-1, 1, 900)
    crackle = m.highpass(crackle, 1500) * 0.6 + m.lowpass(m.noise(DUR), 400) * 0.03
    mx.add(crackle, 0, 0.12, 0, 0.0)
    # match strike + flame catch at the diya
    mx.add(m.highpass(m.noise(0.25), 2500) * np.exp(-m.tl(0.25) * 12), T_LIGHT - 0.25, 0.25)
    tt = m.tl(1.2)
    mx.add(m.lowpass(m.noise(1.2), 900) * np.exp(-tt * 2) * np.minimum(1, tt / 0.05), T_LIGHT, 0.35)
    mx.add(m.bell(float(m.note(86)), 3.0), T_LIGHT, 0.08)
    # tanpura drone throughout
    mx.add(m.tanpura(62, DUR - 0.8, 1.6), 0.6, 0.22, 0, 0.35)
    # chords (D major 7 colour) from the light onward
    prog_ = [[62, 66, 69, 73], [59, 62, 66, 69], [55, 59, 62, 66], [57, 61, 64, 67]]
    t0 = T_LIGHT + 0.4
    b = 0
    while t0 < DUR - 1.0:
        mx.add(keys(prog_[b % 4], bar + 0.3), t0, 0.28, -0.15, 0.45)
        mx.add(m.sub808(prog_[b % 4][0] - 24, bar * 0.9), t0, 0.22, 0, 0.0)
        if t0 > 5.0:                                       # dusty drums enter gently
            g = min(1.0, (t0 - 5.0) / 4.0)
            for k in (0, 2.5):
                mx.add(soft_kick(), t0 + k * beat, 0.45 * g, 0, 0.05)
            for k in (1, 3):
                mx.add(rim(), t0 + k * beat + 0.02, 0.22 * g, 0.2, 0.25)
            for k in range(8):
                mx.add(shaker(), t0 + k * beat / 2 + (0.03 if k % 2 else 0), 0.06 * g, -0.3, 0.1)
        t0 += bar
        b += 1
    # bansuri phrases (calm, breathing space between)
    phrase1 = [(74, 0.9), (76, 0.45), (78, 0.45), (76, 0.9), (74, 1.6)]
    phrase2 = [(81, 0.9), (78, 0.45), (76, 0.45), (78, 0.9), (74, 0.6), (71, 0.6), (74, 1.8)]
    mx.add(m.bansuri(phrase1, 0.1, 0.01), 6.2, 0.22, 0.15, 0.5)
    mx.add(m.bansuri(phrase2, 0.1, 0.01), 13.4, 0.22, 0.15, 0.5)
    mx.add(m.bansuri([(74, 0.8), (78, 0.8), (81, 1.2), (78, 0.6), (74, 2.4)], 0.12, 0.01), T_WELCOME - 0.2, 0.24, 0.15, 0.5)
    # Bindu's little twinkle when it arrives
    for k, nn in enumerate((86, 90, 93)):
        mx.add(m.bell(float(m.note(nn)), 1.5), 17.0 + k * 0.1, 0.05, 0.3)
    out = mx.render(tail=2.6, drive=1.1, fade_out=1.4)
    st = (out.T * 32767 * 0.9).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(m.SR)
        w.writeframes(st.tobytes())


if __name__ == "__main__":
    os.makedirs(FRAMES, exist_ok=True)
    with Pool(os.cpu_count()) as p:
        p.map(draw_frame, range(NFRAMES), chunksize=6)
    wav = os.path.join(HERE, "soundtrack.wav")
    make_audio(wav)
    mp4 = os.path.join(HERE, "welcome_home.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
                    "-i", os.path.join(FRAMES, "f%04d.png"), "-i", wav,
                    "-c:v", "libx264", "-preset", "slow", "-crf", "27", "-tune", "grain",
                    "-maxrate", "6M", "-bufsize", "12M", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", mp4],
                   check=True)
    print("wrote", mp4)
