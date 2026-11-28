"""ANDHAKAAR - Part 1: PRAKASH  (1080x1920, 55 s)

Before he was darkness, his name meant light. A kind lamp-maker's son, his mother's whole world,
until the king's soldiers burned their home and every door in the village stayed shut.
Score: sections of ../../music/amma_prakash_theme_v2 (original).  Usage: python render.py
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
sys.path.insert(0, os.path.join(HERE, "..", "..", "music"))
clamp, prog, ease_io, ease_out, ease_in, lerp, hexc, glow, text, TAU = (
    kit.clamp, kit.prog, kit.ease_io, kit.ease_out, kit.ease_in, kit.lerp, kit.hexc, kit.glow, kit.text, kit.TAU)
FONT, FONT_BLACK = kit.FONT, kit.FONT_BLACK

W, H, FPS, DUR = 1080, 1920, 30, 55.0
NFRAMES = int(FPS * DUR)
FRAMES = os.path.join(HERE, "frames")
AMBER, AMBER2 = hexc("#ffb347"), hexc("#ffe0a0")
RED = hexc("#ff3347")
GOLD = hexc("#ffd166")
PRAKASH = dict(name="PRAKASH", col=AMBER, col2=AMBER2, bg=hexc("#2a1608"), pose="pr_stand")

# ------------------------------------------------------------------ timeline (music offset = 3.0 s)
OFF = 3.0
M_VIOLIN, M_VOICE, M_SWELL, M_BREAK, M_WAIL, M_FALL, M_ENTRY = 5.71, 17.14, 28.57, 38.57, 40.77, 47.27, 63.27
T_TITLE, T_VILLAGE = 3.0, 5.5
T_DIYAS = OFF + M_VIOLIN
T_GROWN = OFF + M_VOICE
T_PROFILE = T_GROWN + 5.6
T_FEST = OFF + M_SWELL
T_TORCH = T_FEST + 6.2
T_BREAK = OFF + M_BREAK
T_FIRE = T_BREAK + 0.8
T_ASH = OFF + M_WAIL
T_TEASE = OFF + M_FALL
SHAKES = [(0.4, 18), (T_BREAK, 30), (T_FIRE, 14), (T_TEASE, 35), (T_TEASE + 1.22, 25)]


def shake(t):
    amp = sum(s * math.exp(-(t - ts) * 5) for ts, s in SHAKES if t >= ts)
    r = random.Random(int(t * FPS))
    return r.uniform(-amp, amp), r.uniform(-amp, amp)


# ------------------------------------------------------------------ poses
STAND = [[(-0.12, 0), (-0.15, 0.47), (-0.2, 0.95)], [(0.12, 0), (0.15, 0.47), (0.2, 0.95)]]
SIT = [[(-0.12, 0), (-0.48, 0.08), (-0.1, 0.24)], [(0.12, 0), (0.48, 0.08), (0.1, 0.24)]]
kit.POSES["pr_stand"] = dict(arms=[[(-0.25, -0.9), (-0.3, -0.5), (-0.27, -0.12)], [(0.25, -0.9), (0.3, -0.5), (0.27, -0.12)]],
                             legs=STAND, lean=0.0, broad=1.05, cape=False)
kit.POSES["pr_release"] = dict(arms=[[(-0.25, -0.9), (-0.22, -1.25), (-0.1, -1.55)], [(0.25, -0.9), (0.22, -1.25), (0.1, -1.55)]],
                               legs=STAND, lean=0.0, broad=1.05, cape=False)
kit.POSES["boy_sit"] = dict(arms=[[(-0.2, -0.88), (-0.2, -0.55), (0.02, -0.4)], [(0.2, -0.88), (0.22, -0.55), (0.06, -0.38)]],
                            legs=SIT, lean=0.0, broad=0.85, cape=False)
kit.POSES["boy_carry"] = dict(arms=[[(-0.2, -0.88), (-0.22, -0.6), (0.0, -0.62)], [(0.2, -0.88), (0.24, -0.6), (0.02, -0.62)]],
                              legs=STAND, lean=0.0, broad=0.85, cape=False)
kit.POSES["kneel"] = dict(arms=[[(-0.24, -0.88), (-0.2, -0.55), (0.0, -0.5)], [(0.24, -0.88), (0.2, -0.55), (0.04, -0.48)]],
                          legs=[[(-0.12, 0), (-0.17, 0.44), (-0.3, 0.5)], [(0.12, 0), (0.17, 0.44), (0.3, 0.5)]],
                          lean=0.12, broad=1.05, cape=False)
kit.POSES["soldier"] = dict(arms=[[(-0.25, -0.9), (-0.36, -0.6), (-0.4, -0.3)], [(0.25, -0.9), (0.4, -0.75), (0.45, -1.05)]],
                            legs=STAND, lean=0.0, broad=1.15, cape=True)


def pose_bottom(name):
    return max(l[-1][1] for l in kit.POSES[name]["legs"])


def figure(ctx, pose, h, x, ground, u, t, power, key=None):
    if key:
        kit.POSES[key] = pose
        pose = key
    return kit.draw_hero(ctx, dict(h, pose=pose), x, ground - pose_bottom(pose) * u, u, t, power)


# ------------------------------------------------------------------ characters
def rimfill(ctx, path_fn, rim, rim_a=1.0, dx=-4, dy=-3, dark=(0.03, 0.02, 0.02)):
    if rim_a > 0:
        ctx.save()
        ctx.translate(dx, dy)
        path_fn()
        ctx.set_source_rgba(*rim, rim_a)
        ctx.fill()
        ctx.restore()
    path_fn()
    ctx.set_source_rgb(*dark)
    ctx.fill()


def draw_amma(ctx, x, ground, u, t, sit=True, bless=0.0, rim=AMBER, rim_a=0.9):
    """Mother in a saree: bun, draped pallu, seated or standing."""
    sy = ground - (0.32 * u if sit else 0.95 * u)       # waist height
    sh = sy - 0.72 * u
    hx, hy = x, sh - 0.24 * u

    def body():
        if sit:   # saree spread on the floor
            ctx.move_to(x - 0.62 * u, ground)
            ctx.curve_to(x - 0.6 * u, sy + 0.05 * u, x - 0.3 * u, sy, x - 0.2 * u, sy)
            ctx.line_to(x + 0.2 * u, sy)
            ctx.curve_to(x + 0.3 * u, sy, x + 0.6 * u, sy + 0.05 * u, x + 0.6 * u, ground)
        else:     # standing pleated saree
            ctx.move_to(x - 0.36 * u, ground)
            ctx.line_to(x - 0.2 * u, sy)
            ctx.line_to(x + 0.2 * u, sy)
            ctx.line_to(x + 0.34 * u, ground)
        ctx.close_path()
        ctx.move_to(x - 0.24 * u, sh)
        ctx.line_to(x + 0.24 * u, sh)
        ctx.line_to(x + 0.19 * u, sy + 0.02 * u)
        ctx.line_to(x - 0.19 * u, sy + 0.02 * u)
        ctx.close_path()
        # pallu falling from the left shoulder behind her
        sway = 0.04 * u * math.sin(t * 1.6)
        ctx.move_to(x - 0.24 * u, sh)
        ctx.curve_to(x - 0.42 * u, sh + 0.3 * u, x - 0.5 * u + sway, sy, x - 0.48 * u + sway, sy + 0.25 * u)
        ctx.line_to(x - 0.3 * u + sway, sy + 0.2 * u)
        ctx.curve_to(x - 0.3 * u, sy - 0.2 * u, x - 0.1 * u, sh + 0.2 * u, x - 0.05 * u, sh)
        ctx.close_path()
        ctx.rectangle(x - 0.05 * u, sh - 0.12 * u, 0.1 * u, 0.14 * u)
        ctx.save()
        ctx.translate(hx, hy)
        ctx.scale(0.13 * u, 0.155 * u)
        ctx.arc(0, 0, 1, 0, TAU)
        ctx.restore()
        ctx.save()
        ctx.translate(hx - 0.12 * u, hy - 0.02 * u)
        ctx.scale(0.075 * u, 0.075 * u)
        ctx.arc(0, 0, 1, 0, TAU)
        ctx.restore()

    def arms():
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_width(0.1 * u)
        ctx.move_to(x - 0.22 * u, sh + 0.05 * u)
        ctx.line_to(x - 0.3 * u, sh + 0.35 * u)
        ctx.line_to(x - 0.06 * u, sy - 0.02 * u)
        ctx.move_to(x + 0.22 * u, sh + 0.05 * u)
        if bless > 0:
            ex = x + lerp(0.3, 0.55, bless) * u
            ey = sh + lerp(0.35, 0.05, bless) * u
            ctx.line_to(ex, ey)
            ctx.line_to(x + lerp(0.06, 0.85, bless) * u, lerp(sy - 0.02 * u, sh + 0.02 * u, bless))
        else:
            ctx.line_to(x + 0.3 * u, sh + 0.35 * u)
            ctx.line_to(x + 0.06 * u, sy - 0.02 * u)
        ctx.stroke_preserve()

    def all_():
        body()
        ctx.fill()
        arms()
        ctx.new_path()

    # rim pass then dark pass (arms stroked)
    for pass_ in (0, 1):
        ctx.save()
        if pass_ == 0:
            ctx.translate(-4, -3)
            ctx.set_source_rgba(*rim, rim_a)
        else:
            ctx.set_source_rgb(0.03, 0.02, 0.02)
        body()
        ctx.fill()
        if pass_ == 0:
            ctx.set_source_rgba(*rim, rim_a)
        else:
            ctx.set_source_rgb(0.03, 0.02, 0.02)
        arms()
        ctx.stroke()
        ctx.restore()
    # gentle eyes
    for side in (-1, 1):
        ctx.set_source_rgba(*AMBER2, 0.7)
        ctx.save()
        ctx.translate(hx + side * 0.045 * u, hy - 0.01 * u)
        ctx.scale(0.028 * u, 0.008 * u)
        ctx.arc(0, 0, 1, 0, TAU)
        ctx.restore()
        ctx.fill()


def draw_prakash(ctx, pose, x, ground, u, t, rim_a=1.0, key=None):
    """Young Prakash: long wavy hair, shawl across the chest, kind amber eyes."""
    p = pose if isinstance(pose, str) else key
    if not isinstance(pose, str):
        kit.POSES[key] = pose
    yb = ground - pose_bottom(p) * u
    hx, hy = x, yb - 1.17 * u

    def hair():
        ctx.move_to(hx - 0.15 * u, hy + 0.02 * u)
        ctx.curve_to(hx - 0.2 * u, hy - 0.22 * u, hx + 0.2 * u, hy - 0.24 * u, hx + 0.16 * u, hy + 0.02 * u)
        for k in range(5):
            yy = hy + 0.06 * u + k * 0.06 * u
            ctx.line_to(hx + (0.19 + 0.02 * math.sin(k * 2 + t * 2)) * u, yy)
        ctx.line_to(hx + 0.12 * u, hy + 0.36 * u)
        ctx.line_to(hx - 0.12 * u, hy + 0.36 * u)
        for k in range(5):
            yy = hy + 0.3 * u - k * 0.06 * u
            ctx.line_to(hx - (0.19 + 0.02 * math.sin(k * 2 + t * 2 + 1)) * u, yy)
        ctx.close_path()

    rimfill(ctx, hair, AMBER, 0.9 * rim_a)
    hands = kit.draw_hero(ctx, dict(PRAKASH, pose=p), x, yb, u, t, rim_a)

    def shawl():
        sway = 0.03 * u * math.sin(t * 1.4)
        ctx.move_to(x + 0.27 * u, yb - 0.92 * u)
        ctx.line_to(x + 0.12 * u, yb - 0.95 * u)
        ctx.line_to(x - 0.22 * u, yb - 0.05 * u)
        ctx.line_to(x - 0.08 * u, yb - 0.02 * u)
        ctx.close_path()
        ctx.move_to(x + 0.27 * u, yb - 0.92 * u)
        ctx.curve_to(x + 0.4 * u, yb - 0.6 * u, x + 0.42 * u + sway, yb - 0.3 * u, x + 0.38 * u + sway, yb - 0.1 * u)
        ctx.line_to(x + 0.3 * u + sway, yb - 0.12 * u)
        ctx.curve_to(x + 0.33 * u, yb - 0.5 * u, x + 0.3 * u, yb - 0.75 * u, x + 0.2 * u, yb - 0.9 * u)
        ctx.close_path()

    shawl()
    ctx.set_source_rgb(*hexc("#5a1410"))
    ctx.fill_preserve()
    ctx.set_source_rgba(*GOLD, 0.8 * rim_a)
    ctx.set_line_width(2.5)
    ctx.stroke()
    return hands


def draw_profile(ctx, x, y, s, t, light=1.0):
    """Close-up side profile of the young man, lit by festival light (shows his face)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)

    def head():
        ctx.move_to(-130, 460)
        ctx.curve_to(-120, 360, -110, 300, -140, 200)
        ctx.curve_to(-230, 60, -200, -170, -60, -240)
        ctx.curve_to(20, -270, 90, -220, 100, -150)
        ctx.curve_to(110, -100, 110, -70, 118, -45)
        ctx.curve_to(140, 0, 168, 30, 165, 48)
        ctx.curve_to(160, 62, 138, 66, 124, 70)
        ctx.curve_to(132, 82, 138, 92, 132, 100)
        ctx.curve_to(126, 106, 128, 112, 134, 120)
        ctx.curve_to(136, 132, 126, 142, 120, 150)
        ctx.curve_to(124, 175, 120, 195, 100, 210)
        ctx.curve_to(70, 230, 40, 240, 30, 250)
        ctx.curve_to(40, 300, 55, 360, 70, 460)
        ctx.close_path()

    # flowing hair behind
    sway = 10 * math.sin(t * 1.3)
    ctx.move_to(-60, -240)
    ctx.curve_to(-200, -230, -300, -100, -290 + sway, 60)
    ctx.curve_to(-280 + sway, 170, -240 + sway, 230, -200, 260)
    ctx.curve_to(-190, 180, -160, 100, -140, 30)
    ctx.close_path()
    ctx.set_source_rgb(0.02, 0.015, 0.015)
    ctx.fill()
    glow(ctx, 260, -200, 520, hexc("#ff9a40"), 0.35 * light)
    ctx.save()
    ctx.translate(6, -4)
    head()
    ctx.set_source_rgba(*AMBER, light)
    ctx.fill()
    ctx.restore()
    head()
    ctx.set_source_rgb(0.035, 0.025, 0.02)
    ctx.fill()
    # front-light catching forehead, nose, lips, chin
    ctx.set_source_rgba(*AMBER2, 0.75 * light)
    ctx.set_line_width(3)
    ctx.move_to(60, -232)
    ctx.curve_to(90, -220, 100, -170, 100, -150)
    ctx.curve_to(110, -100, 110, -70, 118, -45)
    ctx.curve_to(140, 0, 168, 30, 165, 48)
    ctx.stroke()
    ctx.move_to(132, 100)
    ctx.curve_to(126, 106, 128, 112, 134, 120)
    ctx.curve_to(136, 132, 126, 142, 120, 150)
    ctx.curve_to(124, 175, 120, 195, 100, 210)
    ctx.stroke()
    # kind eye with a reflected lantern
    ctx.save()
    ctx.translate(62, -42)
    ctx.scale(22, 8)
    ctx.arc(0, 0, 1, 0, TAU)
    ctx.restore()
    ctx.set_source_rgba(*AMBER2, 0.85 * light)
    ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.9 * light)
    ctx.arc(70, -44, 3.5, 0, TAU)
    ctx.fill()
    ctx.restore()


def draw_soldier(ctx, x, ground, u, t, ph):
    bob = 0.02 * u * abs(math.sin(t * 5 + ph))
    hands = figure(ctx, "soldier", dict(PRAKASH, col=hexc("#ff4020"), col2=hexc("#ffb080")), x, ground - bob, u, t, 0.7)
    hx, hy = hands[1]
    ctx.set_source_rgb(0.03, 0.02, 0.02)
    ctx.set_line_width(0.04 * u)
    ctx.move_to(hands[0][0], hands[0][1] + 0.3 * u)
    ctx.line_to(hands[0][0] - 0.05 * u, hands[0][1] - 1.1 * u)
    ctx.stroke()
    ctx.move_to(hands[0][0] - 0.1 * u, hands[0][1] - 1.1 * u)
    ctx.line_to(hands[0][0] - 0.05 * u, hands[0][1] - 1.3 * u)
    ctx.line_to(hands[0][0], hands[0][1] - 1.1 * u)
    ctx.close_path()
    ctx.fill()
    yb = ground - bob - pose_bottom("soldier") * u
    ctx.move_to(x - 0.17 * u, yb - 1.2 * u)
    ctx.curve_to(x - 0.17 * u, yb - 1.45 * u, x + 0.17 * u, yb - 1.45 * u, x + 0.17 * u, yb - 1.2 * u)
    ctx.close_path()
    ctx.fill()
    ctx.move_to(x - 0.03 * u, yb - 1.4 * u)
    ctx.line_to(x, yb - 1.58 * u)
    ctx.line_to(x + 0.03 * u, yb - 1.4 * u)
    ctx.fill()
    fl = 1 + 0.15 * math.sin(t * 25 + ph)
    glow(ctx, hx, hy - 0.1 * u, 0.9 * u * fl, hexc("#ff6a20"), 0.8)
    glow(ctx, hx, hy - 0.12 * u, 0.25 * u * fl, hexc("#ffd080"), 1.0)


def hut(ctx, x, ground, w, h, door=1.0, lit=1.0, burnt=0.0):
    ctx.set_source_rgb(*tuple(lerp(a, b, burnt) for a, b in zip(hexc("#2a1a10"), hexc("#0a0606"))))
    ctx.rectangle(x - w / 2, ground - h * 0.6, w, h * 0.6)
    ctx.fill()
    ctx.move_to(x - w * 0.62, ground - h * 0.58)
    ctx.line_to(x, ground - h * (1.15 - 0.35 * burnt))
    ctx.line_to(x + w * 0.62, ground - h * 0.58)
    ctx.close_path()
    ctx.fill()
    dw, dh = w * 0.26, h * 0.38
    if lit > 0:
        glow(ctx, x, ground - dh / 2, w * 0.8, hexc("#ffa040"), 0.45 * lit * door)
        ctx.set_source_rgba(1, 0.72, 0.35, lit)
        ctx.rectangle(x - dw / 2, ground - dh, dw, dh)
        ctx.fill()
    # door panel sliding shut
    ctx.set_source_rgb(0.06, 0.035, 0.02)
    ctx.rectangle(x - dw / 2, ground - dh, dw * (1 - door), dh)
    ctx.fill()


def flames(ctx, x, ground, w, h, t, a=1.0):
    r = random.Random(int(t * 12))
    for k in range(9):
        fx = x - w / 2 + w * (k + 0.5) / 9
        fh = h * (0.5 + 0.5 * abs(math.sin(t * 6 + k * 1.7))) * r.uniform(0.8, 1.1)
        for sc, col in ((1.0, hexc("#ff4a10")), (0.65, hexc("#ff9a30")), (0.35, hexc("#ffe080"))):
            ww = w / 9 * 0.9 * sc
            ctx.move_to(fx - ww, ground)
            ctx.curve_to(fx - ww, ground - fh * sc * 0.6, fx + 5 * math.sin(t * 9 + k), ground - fh * sc * 0.9,
                         fx, ground - fh * sc)
            ctx.curve_to(fx + 5 * math.sin(t * 7 + k), ground - fh * sc * 0.9, fx + ww, ground - fh * sc * 0.6,
                         fx + ww, ground)
            ctx.close_path()
            ctx.set_source_rgba(*col, a)
            ctx.fill()
    glow(ctx, x, ground - h * 0.5, w * 1.5, hexc("#ff5a20"), 0.5 * a)


# ------------------------------------------------------------------ static data
R = random.Random(13)
EMBERS = [(R.uniform(0, W), R.uniform(0, 1), R.uniform(60, 200), R.uniform(1.5, 4), R.uniform(0, TAU)) for _ in range(90)]
ASH = [(R.uniform(0, W), R.uniform(0, 1), R.uniform(40, 110), R.uniform(2, 5), R.uniform(0, TAU)) for _ in range(120)]
LANTERNS = [(R.uniform(80, W - 80), R.uniform(0, 1), R.uniform(40, 90), R.uniform(0.7, 1.3)) for _ in range(26)]
VILLAGE = [(x, R.uniform(140, 200), R.uniform(130, 180)) for x in (80, 290, 790, 1000)]
G = 1500


def golden_sky(ctx, dusk=0.0):
    g = cairo.LinearGradient(0, 0, 0, G)
    g.add_color_stop_rgb(0, *tuple(lerp(a, b, dusk) for a, b in zip(hexc("#f3b27a"), hexc("#1a0f2a"))))
    g.add_color_stop_rgb(0.7, *tuple(lerp(a, b, dusk) for a, b in zip(hexc("#ffd59a"), hexc("#4a2030"))))
    g.add_color_stop_rgb(1, *tuple(lerp(a, b, dusk) for a, b in zip(hexc("#ffe7b8"), hexc("#6a3020"))))
    ctx.set_source(g)
    ctx.paint()


def ground(ctx, col):
    ctx.set_source_rgb(*col)
    ctx.rectangle(-300, G, W + 600, 900)
    ctx.fill()


def narr(ctx, t, items, y0=380, base=(1, 0.96, 0.88)):
    for t0, t1, ls, acc in items:
        a = ease_io(prog(t, t0, t0 + 0.5)) * (1 - ease_io(prog(t, t1 - 0.5, t1)))
        if a <= 0:
            continue
        for j, ln in enumerate(ls):
            hi = acc and j == len(ls) - 1
            col = acc if hi and isinstance(acc, tuple) else base
            text(ctx, ln, W / 2, y0 + j * 90, 66 if not hi else 74, col, a, FONT_BLACK if hi else FONT, 2,
                 glow_col=col if hi else None)


# ------------------------------------------------------------------ scenes
def scene_hook(ctx, t):
    ctx.set_source_rgb(0.01, 0, 0.01)
    ctx.paint()
    eyes = ease_out(prog(t, 0.3, 0.6))
    kit.draw_villain(ctx, W / 2, 300, 1.1, t, eyes, 0.4 + 0.6 * eyes)
    a = ease_io(prog(t, 0.9, 1.3)) * (1 - ease_io(prog(t, 2.6, 3.0)))
    text(ctx, "Before he was darkness...", W / 2, 1500, 64, (1, 1, 1), a, FONT, 2)
    b = ease_io(prog(t, 1.6, 2.0)) * (1 - ease_io(prog(t, 2.6, 3.0)))
    text(ctx, "his name meant LIGHT.", W / 2, 1600, 76, GOLD, b, FONT_BLACK, 2, glow_col=hexc("#ffb000"))


def scene_title(ctx, t):
    s = prog(t, T_TITLE, T_VILLAGE)
    golden_sky(ctx, 0.0)
    ctx.set_source_rgba(0, 0, 0, 1 - ease_io(prog(t, T_TITLE, T_TITLE + 1.0)) * 0.6)
    ctx.paint()
    a = ease_io(prog(t, T_TITLE + 0.3, T_TITLE + 0.9)) * (1 - ease_io(prog(t, T_VILLAGE - 0.4, T_VILLAGE)))
    text(ctx, "A N D H A K A A R", W / 2, 820, 40, (0.5, 0.1, 0.12), a, FONT_BLACK, 4)
    text(ctx, "PART 1", W / 2, 900, 34, (0.3, 0.18, 0.1), a, FONT, 10)
    text(ctx, "PRAKASH", W / 2, 1040, 140, (0.25, 0.12, 0.04), a, FONT_BLACK, 14)


def village_bg(ctx, t, dusk=0.0, lamps=0.0):
    golden_sky(ctx, dusk)
    if dusk < 0.6:
        glow(ctx, 760, 1250, 500, hexc("#fff0c8"), 0.7 * (1 - dusk))
    ctx.set_source_rgb(*tuple(lerp(a, b, dusk) for a, b in zip(hexc("#c98a52"), hexc("#2a1420"))))
    ctx.move_to(-300, G)
    for x in range(-300, W + 320, 20):
        ctx.line_to(x, 1330 - 40 * math.sin(x * 0.006 + 1))
    ctx.line_to(W + 320, G)
    ctx.close_path()
    ctx.fill()
    for k, (vx, w, h) in enumerate(VILLAGE):
        hut(ctx, vx, G, w, h, 1.0, lamps)
    ground(ctx, tuple(lerp(a, b, dusk) for a, b in zip(hexc("#8a5a32"), hexc("#1a0c0a"))))


def scene_village(ctx, t):
    village_bg(ctx, t, 0.0, 0.0)
    hut(ctx, 540, G, 300, 280, 1.0, 0.3)
    for k in range(7):                                   # clay lamps drying on the porch
        ctx.set_source_rgb(*hexc("#8a4a24"))
        x = 420 + k * 40
        ctx.move_to(x - 14, G + 8)
        ctx.curve_to(x - 12, G + 20, x + 12, G + 20, x + 14, G + 8)
        ctx.close_path()
        ctx.fill()
    narr(ctx, t, [(T_VILLAGE + 0.2, T_DIYAS + 0.1, ["His name was PRAKASH.", "It means LIGHT."], hexc("#7a2a08"))],
         base=(0.2, 0.1, 0.04))


def scene_diyas(ctx, t):
    s = t - T_DIYAS
    z = 1.5
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.scale(z, z)
    ctx.translate(-540, -1330)
    village_bg(ctx, t, 0.15 * prog(t, T_DIYAS, T_GROWN), 0.0)
    hut(ctx, 540, G - 20, 420, 360, 1.0, 0.5)
    bless = ease_io(prog(t, T_DIYAS + 7.0, T_DIYAS + 8.0)) * (1 - ease_io(prog(t, T_GROWN - 1.2, T_GROWN - 0.4)))
    draw_amma(ctx, 430, G, 190, t, True, bless)
    figure(ctx, "boy_sit", PRAKASH, 640, G, 120, t, 0.7)
    # a row of diyas being lit one by one
    for k in range(6):
        x = 400 + k * 52
        on = ease_out(prog(t, T_DIYAS + 3.0 + k * 0.6, T_DIYAS + 3.4 + k * 0.6))
        agni_ep.diya(ctx, x - 22, G + 40, 0.35 * on, t + k)
    ctx.restore()
    narr(ctx, t, [(T_DIYAS + 0.3, T_DIYAS + 5.4, ["Every evening, Amma", "made clay lamps..."], False),
                  (T_DIYAS + 5.8, T_GROWN - 0.2, ["...and he lit them for", "the whole village."], False)],
         base=(0.2, 0.1, 0.04))


def scene_grown(ctx, t):
    if t >= T_PROFILE:
        return scene_profile(ctx, t)
    grow = ease_io(prog(t, T_GROWN, T_GROWN + 1.6))
    z = 1.35
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.scale(z, z)
    ctx.translate(-540, -1300)
    village_bg(ctx, t, 0.35, 0.6)
    hut(ctx, 540, G - 20, 420, 360, 1.0, 0.7)
    draw_amma(ctx, 400, G, 210, t, False, 0.0)
    ctx.push_group()
    figure(ctx, "boy_carry", PRAKASH, 650, G, 125, t, 0.7)
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(1 - grow)
    if grow > 0:
        ctx.push_group()
        draw_prakash(ctx, "pr_stand", 650, G, 215, t)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(grow)
    ctx.restore()
    narr(ctx, t, [(T_GROWN + 0.6, T_PROFILE + 0.2, ["He grew into a", "kind young man."], False)])


def scene_profile(ctx, t):
    s = t - T_PROFILE
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, *hexc("#1a0f2a"))
    g.add_color_stop_rgb(1, *hexc("#4a2010"))
    ctx.set_source(g)
    ctx.paint()
    for lx, ph, sz, sp in LANTERNS[:12]:
        y = 1500 - ((ph + s * 0.06 * sp) % 1.0) * 1600
        glow(ctx, lx, y, sz, hexc("#ffb050"), 0.6)
    draw_profile(ctx, 470 - 10 * s, 1000, 1.45, t, 1.0)
    narr(ctx, t, [(T_PROFILE + 0.3, T_FEST, ["Amma was", "his whole world."], GOLD)])


def scene_festival(ctx, t):
    s = t - T_FEST
    torch = ease_io(prog(t, T_TORCH, T_BREAK))
    z = 1.2
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.scale(z, z)
    ctx.translate(-540, -1200)
    village_bg(ctx, t, 1.0, 1.0)
    # festival lights along the path
    for k in range(14):
        x = 40 + k * 75
        agni_ep.diya(ctx, x - 22, G + 30, 0.3, t + k)
    for lx, ph, sz, sp in LANTERNS:
        y = 1350 - ((ph + s * 0.05 * sp) % 1.0) * 1500
        glow(ctx, lx, y, sz, hexc("#ffb050"), 0.7)
        ctx.set_source_rgba(1, 0.75, 0.4, 0.9)
        ctx.rectangle(lx - sz * 0.18, y - sz * 0.25, sz * 0.36, sz * 0.5)
        ctx.fill()
    hut(ctx, 540, G - 20, 420, 360, 1.0, 1.0)
    # their own lantern rising from their hands
    rise = ease_out(prog(t, T_FEST + 1.5, T_FEST + 9.0))
    lx, ly = 540, lerp(G - 470, 300, rise)
    glow(ctx, lx, ly, 160, hexc("#ffc060"), 0.9)
    ctx.set_source_rgba(1, 0.8, 0.45, 1)
    ctx.rectangle(lx - 26, ly - 36, 52, 72)
    ctx.fill()
    draw_amma(ctx, 440, G, 210, t, False, 0.0)
    draw_prakash(ctx, "pr_release" if t < T_FEST + 2.5 else "pr_stand", 640, G, 215, t)
    # soldiers' torches arriving
    if torch > 0:
        glow(ctx, W + 100, G - 200, 900 * torch, hexc("#ff3a10"), 0.5 * torch)
        for k in range(4):
            sx = lerp(W + 250 + k * 110, 860 + k * 90, torch)
            draw_soldier(ctx, sx, G, 150, t, k)
    ctx.restore()
    narr(ctx, t, [(T_FEST + 0.3, T_TORCH - 0.2, ["On the night of the", "festival of lights..."], False),
                  (T_TORCH + 0.2, T_BREAK, ["...the king's soldiers came", "for unpaid taxes."], RED)])


def scene_fire(ctx, t):
    ctx.set_source_rgb(0, 0, 0)
    ctx.paint()
    if t < T_FIRE:
        return
    a = ease_out(prog(t, T_FIRE, T_FIRE + 0.6))
    hut(ctx, 540, 1400, 600, 520, 1.0, 0.0, 0.6)
    flames(ctx, 540, 1400, 700, 650, t, a)
    for ex, ph, sp, sz, w in EMBERS:
        y = 1400 - ((ph + (t - T_FIRE) * sp / 1400) % 1.0) * 1400
        ctx.set_source_rgba(1, 0.6, 0.2, a * 0.9)
        ctx.arc(ex + 20 * math.sin(t * 2 + w), y, sz, 0, TAU)
        ctx.fill()
    narr(ctx, t, [(T_FIRE + 0.2, T_ASH + 0.1, ["They burned", "their home."], RED)])


def scene_ash(ctx, t):
    s = t - T_ASH
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, *hexc("#0a0608"))
    g.add_color_stop_rgb(1, *hexc("#2a1410"))
    ctx.set_source(g)
    ctx.paint()
    z = 1.3
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.scale(z, z)
    ctx.translate(-540, -1300)
    ground(ctx, hexc("#120a08"))
    hut(ctx, 220, G, 360, 320, 1.0, 0.0, 1.0)
    flames(ctx, 220, G, 300, 160 * (1 - 0.6 * prog(t, T_ASH, T_TEASE)), t, 0.6)
    # neighbours' doors closing one by one
    for k, x in enumerate((640, 860, 1060)):
        shut = ease_io(prog(t, T_ASH + 1.0 + k * 1.1, T_ASH + 1.6 + k * 1.1))
        hut(ctx, x, G, 190, 190, 1 - shut, 1.0)
    kh = figure(ctx, "kneel", dict(PRAKASH, col=hexc("#a05a30")), 470, G, 200, t, 0.5)
    # the broken diya in his hands: its last ember dies
    hx = (kh[0][0] + kh[1][0]) / 2
    hy = (kh[0][1] + kh[1][1]) / 2
    ctx.set_source_rgb(*hexc("#6a3418"))
    for side, rot in ((-1, -0.4), (1, 0.4)):
        ctx.save()
        ctx.translate(hx + side * 16, hy + 6)
        ctx.rotate(rot)
        ctx.move_to(-14, 0)
        ctx.curve_to(-12, 12, 12, 12, 14, 0)
        ctx.close_path()
        ctx.restore()
        ctx.fill()
    ember = 1 - ease_in(prog(t, T_ASH + 4.6, T_ASH + 5.6))
    if ember > 0:
        glow(ctx, hx, hy - 6, 40 * ember, hexc("#ff8a30"), ember)
    else:
        k2 = (t - T_ASH - 5.6)
        ctx.set_source_rgba(0.6, 0.6, 0.6, max(0, 0.5 - k2 * 0.4))
        ctx.set_line_width(3)
        ctx.move_to(hx, hy - 8)
        ctx.curve_to(hx + 10, hy - 40 - k2 * 40, hx - 10, hy - 70 - k2 * 60, hx + 5, hy - 110 - k2 * 80)
        ctx.stroke()
    ctx.restore()
    for ax, ph, sp, sz, w in ASH:
        y = ((ph + s * sp / 1800) % 1.0) * 1900
        ctx.set_source_rgba(0.6, 0.58, 0.55, 0.55)
        ctx.arc(ax + 20 * math.sin(t + w), y, sz, 0, TAU)
        ctx.fill()
    narr(ctx, t, [(T_ASH + 0.2, T_ASH + 3.3, ["He begged", "for help..."], False),
                  (T_ASH + 3.4, T_TEASE + 0.1, ["No door opened.", "His light went out."], RED)])


def scene_tease(ctx, t):
    s = t - T_TEASE
    ctx.set_source_rgb(0.01, 0, 0.01)
    ctx.paint()
    eyes = ease_out(prog(t, T_TEASE, T_TEASE + 0.2))
    ctx.push_group()
    kit.draw_villain(ctx, W / 2, 180, 1.0, t, eyes, 0.8)
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(0.55)
    figure(ctx, "kneel", dict(PRAKASH, col=RED), W / 2, 1520, 170, t, 0.4)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    reach = ease_io(prog(t, T_TEASE, T_TEASE + 2.5))
    for k in range(6):
        side = -1 if k % 2 else 1
        sx = W / 2 + side * (300 + 50 * k)
        ex, ey = lerp(sx, W / 2 + side * 60, reach), lerp(1600, 1250, reach)
        ctx.set_source_rgba(0.04, 0.0, 0.06, 0.95)
        ctx.set_line_width(22 - 2 * k)
        ctx.move_to(sx, 1800)
        ctx.curve_to(sx, 1600, ex + side * 100, ey + 100, ex, ey)
        ctx.stroke()
    if T_TEASE <= t < T_TEASE + 0.07:
        ctx.set_source_rgba(1, 0.1, 0.15, 0.7)
        ctx.paint()
    a = ease_io(prog(t, T_TEASE + 0.5, T_TEASE + 0.9))
    text(ctx, "The darkness whispered...", W / 2, 360, 60, (1, 0.85, 0.85), a, FONT, 2)
    b = ease_io(prog(t, T_TEASE + 1.22, T_TEASE + 1.4))
    text(ctx, "\"TAKE THEIRS.\"", W / 2, 460, 88, RED, b, FONT_BLACK, 4, glow_col=hexc("#ff0020"))
    c = ease_io(prog(t, T_TEASE + 2.4, T_TEASE + 2.9))
    text(ctx, "NEXT:  PART 2", W / 2, 1760, 40, (1, 0.85, 0.85), c, FONT, 8)
    text(ctx, "THE FALL", W / 2, 1860, 84, (1, 1, 1), c, FONT_BLACK, 10, glow_col=hexc("#ff0020"))


def vintage(ctx, t, amt=1.0):
    ctx.set_source_rgba(0.45, 0.28, 0.1, 0.16 * amt)
    ctx.paint()
    r = random.Random(int(t * FPS))
    fl = r.uniform(-0.03, 0.03) * amt
    if fl > 0:
        ctx.set_source_rgba(1, 0.95, 0.85, fl)
    else:
        ctx.set_source_rgba(0, 0, 0, -fl)
    ctx.paint()
    for _ in range(r.randint(0, 2)):
        x = r.uniform(0, W)
        ctx.set_source_rgba(1, 0.95, 0.85, r.uniform(0.05, 0.12) * amt)
        ctx.set_line_width(r.uniform(1, 2))
        ctx.move_to(x, 0)
        ctx.line_to(x + r.uniform(-20, 20), H)
        ctx.stroke()


def draw_frame(i):
    t = i / FPS
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    dx, dy = shake(t)
    ctx.translate(dx, dy)
    ctx.translate(W / 2, H / 2)
    ctx.scale(1.04, 1.04)
    ctx.translate(-W / 2, -H / 2)
    if t < T_TITLE:
        scene_hook(ctx, t)
    elif t < T_VILLAGE:
        scene_title(ctx, t)
    elif t < T_DIYAS:
        scene_village(ctx, t)
    elif t < T_GROWN:
        scene_diyas(ctx, t)
    elif t < T_FEST:
        scene_grown(ctx, t)
    elif t < T_BREAK:
        scene_festival(ctx, t)
    elif t < T_ASH:
        scene_fire(ctx, t)
    elif t < T_TEASE:
        scene_ash(ctx, t)
    else:
        scene_tease(ctx, t)
    ctx.identity_matrix()
    if T_TITLE <= t < T_BREAK:
        vintage(ctx, t)
    v = cairo.RadialGradient(W / 2, H / 2, H * 0.3, W / 2, H / 2, H * 0.72)
    v.add_color_stop_rgba(0, 0, 0, 0, 0)
    v.add_color_stop_rgba(1, 0, 0, 0, 0.6)
    ctx.set_source(v)
    ctx.paint()
    if t > DUR - 0.6:
        ctx.set_source_rgba(0, 0, 0, prog(t, DUR - 0.6, DUR))
        ctx.paint()
    surf.flush()
    kit.post(surf, t, 0)
    surf.mark_dirty()
    surf.write_to_png(os.path.join(FRAMES, f"f{i:04d}.png"))


# ------------------------------------------------------------------ soundtrack: hook + score sections + SFX
def make_audio(path):
    import mass_kit as m
    score_path = os.path.join(HERE, "..", "..", "music", "amma_prakash_theme_v2.wav")
    if not os.path.exists(score_path):
        subprocess.run([sys.executable, "amma_prakash_theme_v2.py"], cwd=os.path.dirname(score_path), check=True)
    with wave.open(score_path) as w:
        score = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).T / 32768.0
    SR = m.SR
    N = int(DUR * SR)
    out = np.zeros((2, N))

    def place(seg, t0, gain=1.0):
        i0 = int(t0 * SR)
        i1 = min(N, i0 + seg.shape[1])
        out[:, i0:i1] += seg[:, :i1 - i0] * gain

    def cut(a, b, fin=0.02, fout=0.3):
        seg = score[:, int(a * SR):int(b * SR)].copy()
        n = seg.shape[1]
        env = np.ones(n)
        fi, fo = int(fin * SR), int(fout * SR)
        env[:fi] = np.linspace(0, 1, fi)
        env[n - fo:] = np.linspace(1, 0, fo)
        return seg * env

    # hook (0-3 s): drone, heartbeat, eyes-open hit, a single bell for "light"
    hook = m.Mix(OFF + 0.6)
    tt = m.tl(OFF + 0.6)
    hook.add(m.lowpass(m.saw(36.7, tt) + m.saw(36.95, tt), 220) * np.minimum(1, tt / 0.2)
             * np.clip((OFF + 0.6 - tt) / 0.8, 0, 1), 0, 0.5)
    hook.add(m.heartbeat(), 0.05, 0.8, 0, 0.1)
    hook.add(m.braam([26, 33, 38]), 0.4, 0.9)
    hook.add(m.taiko(0.6), 0.4, 0.9)
    hook.add(m.bell(float(m.note(86)), 2.5), 1.6, 0.15)
    hook.add(m.choir([62, 65, 69], 1.6, "oo", 3, 0.3), 1.6, 0.35)
    h = hook.render(tail=1.5, drive=1.2, fade_out=0.5)
    place(h * 0.85, 0.0)
    # score: memories -> swell -> break -> mourning (music 0 .. 47.27)
    place(cut(0.0, M_FALL, 0.4, 0.6), OFF)
    # tease: the villain entry hits (music 63.27 .. 63.27+4.7)
    place(cut(M_ENTRY, M_ENTRY + (DUR - T_TEASE), 0.01, 0.8), T_TEASE)
    # SFX: festival crowd murmur, soldiers' march, fire, doors, ember hiss
    sfx = m.Mix(DUR)
    crowd = m.lowpass(m.noise(T_BREAK - T_FEST), 900) * (0.6 + 0.4 * np.sin(m.TAU * 0.7 * m.tl(T_BREAK - T_FEST)))
    sfx.add(crowd * np.minimum(1, m.tl(T_BREAK - T_FEST) / 1.0), T_FEST, 0.05, 0, 0.3)
    k, tm = 0, T_TORCH
    while tm < T_BREAK - 0.1:
        sfx.add(m.lowpass(m.noise(0.12), 400) * np.exp(-m.tl(0.12) * 30), tm, 0.25 + 0.2 * (tm - T_TORCH) / 3, 0.4, 0.2)
        tm += 0.5
    tt = m.tl(T_ASH - T_FIRE + 3)
    fire = m.lowpass(m.noise(len(tt) / SR), 700) * (0.7 + 0.3 * np.abs(np.sin(m.TAU * 5 * tt)))
    crack = m.highpass(m.noise(len(tt) / SR), 3000) * (np.random.default_rng(1).random(len(tt)) < 0.002) * 8
    sfx.add((fire + crack) * np.minimum(1, tt / 0.4) * np.clip((len(tt) / SR - tt) / 2.0, 0, 1), T_FIRE, 0.35, 0, 0.2)
    for k in range(3):
        sfx.add(m.lowpass(m.noise(0.25), 300) * np.exp(-m.tl(0.25) * 18), T_ASH + 1.6 + k * 1.1, 0.5, 0.3 + 0.2 * k, 0.3)
    sfx.add(m.highpass(m.noise(0.8), 2000) * np.exp(-m.tl(0.8) * 4), T_ASH + 5.5, 0.15, 0, 0.3)
    sfx_out = sfx.render(tail=1.2, drive=1.0, fade_out=0.5)
    out += sfx_out * 0.35
    out /= np.max(np.abs(out)) * 1.05
    t = np.arange(N) / SR
    out *= np.clip((DUR - t) / 0.6, 0, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((out.T * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    os.makedirs(FRAMES, exist_ok=True)
    with Pool(os.cpu_count()) as p:
        p.map(draw_frame, range(NFRAMES), chunksize=6)
    wav = os.path.join(HERE, "soundtrack.wav")
    make_audio(wav)
    mp4 = os.path.join(HERE, "andhakaar_part1_prakash.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
                    "-i", os.path.join(FRAMES, "f%04d.png"), "-i", wav,
                    "-c:v", "libx264", "-preset", "slow", "-crf", "27", "-tune", "grain",
                    "-maxrate", "6M", "-bufsize", "12M", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", mp4],
                   check=True)
    print("wrote", mp4)
