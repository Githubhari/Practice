"""GUARDIANS OF THE LAST LIGHT - Origin #4: BHUMI, The Unbreakable  (1080x1920, 35 s)

They called him weak... he held up a mountain.
Visuals reuse the rig in ../trailer/render.py; the score uses ../../music/mass_kit.py
(an original Telugu-mass style BGM: tanpura + bansuri -> choir build -> half-time hero drop).
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
_spec = importlib.util.spec_from_file_location(
    "trailer_kit", os.path.join(HERE, "..", "trailer", "render.py"))
kit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(kit)
globals().update({k: getattr(kit, k) for k in (
    "clamp", "prog", "ease_io", "ease_out", "ease_in", "lerp", "hexc", "glow", "text",
    "speed_lines", "draw_hero", "draw_villain", "lightning", "post", "FONT", "FONT_BLACK", "TAU")})
sys.path.insert(0, os.path.join(HERE, "..", "..", "music"))

W, H, FPS, DUR = 1080, 1920, 30, 35.0
NFRAMES = int(FPS * DUR)
FRAMES = os.path.join(HERE, "frames")
BHUMI = kit.HEROES[3]
GREEN, GOLD = BHUMI["col"], BHUMI["col2"]

# music grid (144 bpm, half-time hero groove after the drop)
BEAT = 60 / 144
BAR = 4 * BEAT
# ------------------------------------------------------------------ timeline
T_CATCH0 = 0.6
T_REWIND, T_QUARRY, T_QUAKE = 2.8, 3.6, 9.0
T_DROPSTONE = 6.5
T_RUN, T_CATCH, T_GLOW, T_DROP = 15.0, 17.5, 19.0, 19.8
T_RISE = T_DROP + BAR
T_HERO = T_DROP + 3.5 * BAR
T_SLAM = T_DROP + 4 * BAR
T_END = T_DROP + 7 * BAR
SHAKES = [(T_CATCH0, 40), (T_REWIND, 10), (T_DROPSTONE, 6), (10.0, 18), (12.3, 14), (14.0, 14),
          (T_CATCH, 45), (T_DROP, 50), (T_RISE, 20), (T_HERO, 20), (T_SLAM, 30), (T_END + 1.0, 14)]


def shake(t):
    amp = sum(s * math.exp(-(t - ts) * 5) for ts, s in SHAKES if t >= ts)
    if T_QUAKE + 0.5 < t < T_CATCH:
        amp += 7 + 4 * math.sin(t * 3)
    if T_CATCH < t < T_DROP:
        amp += 3 + 6 * prog(t, T_CATCH, T_DROP)
    r = random.Random(int(t * FPS))
    return r.uniform(-amp, amp), r.uniform(-amp, amp)


# ------------------------------------------------------------------ poses
def run_pose(phase, lean=0.22, broad=0.9):
    legs, arms = [], []
    for ph in (phase, phase + math.pi):
        thigh = 0.75 * math.sin(ph)
        bend = 0.2 + 1.2 * max(0.0, math.cos(ph))
        knee = (0.47 * math.sin(thigh), 0.47 * math.cos(thigh))
        sh = thigh - bend
        legs.append([(0, 0), knee, (knee[0] + 0.48 * math.sin(sh), knee[1] + 0.48 * math.cos(sh))])
        ua = -0.9 * math.sin(ph)
        el = (0.3 * math.sin(ua), -0.86 + 0.3 * math.cos(ua))
        fa = ua + 1.6
        arms.append([(0, -0.86), el, (el[0] + 0.28 * math.sin(fa), el[1] + 0.28 * math.cos(fa))])
    return dict(arms=arms, legs=legs, lean=lean, broad=broad, cape=False)


STAND_LEGS = [[(-0.12, 0), (-0.15, 0.47), (-0.2, 0.95)], [(0.12, 0), (0.15, 0.47), (0.2, 0.95)]]
kit.POSES["carry"] = dict(arms=[[(-0.22, -0.88), (-0.32, -1.12), (-0.1, -1.36)],
                                [(0.22, -0.88), (0.32, -1.12), (0.1, -1.36)]],
                          legs=STAND_LEGS, lean=0.0, broad=0.95, cape=False)
kit.POSES["struggle"] = dict(arms=[[(-0.2, -0.88), (-0.12, -0.55), (0.05, -0.45)],
                                   [(0.2, -0.88), (0.25, -0.55), (0.1, -0.45)]],
                             legs=[[(-0.12, 0), (-0.25, 0.45), (-0.22, 0.95)], [(0.12, 0), (0.25, 0.45), (0.22, 0.95)]],
                             lean=0.25, broad=0.85, cape=False)
kit.POSES["boy_stand"] = dict(arms=[[(-0.2, -0.88), (-0.28, -0.5), (-0.3, -0.15)],
                                    [(0.2, -0.88), (0.28, -0.5), (0.3, -0.15)]],
                              legs=STAND_LEGS, lean=0.06, broad=0.85, cape=False)
kit.POSES["strain"] = dict(kit.POSES["bhumi"], broad=0.95, cape=False,
                           legs=[[(-0.15, 0), (-0.46, 0.3), (-0.55, 0.78)], [(0.15, 0), (0.46, 0.3), (0.55, 0.78)]])


def pose_bottom(name):
    return max(l[-1][1] for l in kit.POSES[name]["legs"])


def draw_posed(ctx, name, h, x, ground_y, u, t, power, key=None):
    if key:
        kit.POSES[key] = name
        name = key
    return draw_hero(ctx, dict(h, pose=name), x, ground_y - pose_bottom(name) * u, u, t, power)


def rock_poly(ctx, x, y, w, h, seed, rot=0.0):
    r = random.Random(seed)
    pts = []
    for k in range(9):
        a = k * TAU / 9
        pts.append((math.cos(a) * w / 2 * r.uniform(0.8, 1.1), math.sin(a) * h / 2 * r.uniform(0.75, 1.1)))
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.close_path()
    ctx.restore()


def slab(ctx, cx, bottom_y, t, glow_a=0.0):
    ctx.move_to(cx - 330, bottom_y)
    for k, (dx, dy) in enumerate(((-300, -110), (-180, -160), (-40, -150), (90, -185), (240, -140), (320, -60))):
        ctx.line_to(cx + dx, bottom_y + dy)
    ctx.line_to(cx + 340, bottom_y)
    ctx.close_path()
    g = cairo.LinearGradient(0, bottom_y - 190, 0, bottom_y)
    g.add_color_stop_rgb(0, *hexc("#4a3c2c"))
    g.add_color_stop_rgb(1, *hexc("#221a12"))
    ctx.set_source(g)
    ctx.fill_preserve()
    ctx.set_source_rgba(*GOLD, 0.25 + 0.6 * glow_a)
    ctx.set_line_width(3 + 3 * glow_a)
    ctx.stroke()


def cracks(ctx, x, y, length, col, a, seed, n=9, width=5):
    r = random.Random(seed)
    ctx.set_line_width(width)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(n):
        ang = math.pi + k * math.pi / (n - 1) + r.uniform(-0.12, 0.12)
        px, py = x, y
        ctx.move_to(px, py)
        for j in range(6):
            px += -math.cos(ang) * length / 6 + r.uniform(-18, 18)
            py += abs(math.sin(ang)) * length / 6 * 0.22 + r.uniform(-6, 6)
            ctx.line_to(px, py)
        ctx.set_source_rgba(*col, a)
        ctx.stroke()
    glow(ctx, x, y, length * 0.6, col, 0.35 * a)


# ------------------------------------------------------------------ static data
R = random.Random(55)
FALLING = [(R.uniform(0, W), R.uniform(0, 1), R.uniform(500, 900), R.uniform(12, 40), R.uniform(-3, 3), R.randint(0, 999))
           for _ in range(28)]
DUST = [(R.uniform(-1, 1), R.uniform(0, 1), R.uniform(2, 6)) for _ in range(80)]
ORBIT = [(R.uniform(0, TAU), R.uniform(180, 420), R.uniform(16, 46), R.uniform(0.5, 1.4), R.randint(0, 999))
         for _ in range(22)]
WORKERS = [(140, 0.0), (820, 1.3), (960, 2.1)]


# ------------------------------------------------------------------ scenes
def scene_hook(ctx, t):
    ctx.set_source_rgb(*hexc("#141206"))
    ctx.paint()
    p = ease_out(prog(t, T_CATCH0 - 0.1, T_CATCH0 + 0.2))
    glow(ctx, W / 2, 1000, 1100, GREEN, 0.2 + 0.5 * p)
    speed_lines(ctx, W / 2, 900, t, 0.25 * p, GOLD)
    ctx.set_source_rgb(0.03, 0.03, 0.02)
    ctx.rectangle(-200, 1400, W + 400, 800)
    ctx.fill()
    u = 290
    y = 1400 - pose_bottom("bhumi") * u
    hands = draw_hero(ctx, BHUMI, W / 2, y, u, t, p)
    fist_y = min(h[1] for h in hands) - 0.09 * u
    fall = ease_in(prog(t, 0.0, T_CATCH0))
    bottom = lerp(-300, fist_y, fall) if t < T_CATCH0 else fist_y + 10 * math.exp(-(t - T_CATCH0) * 8) * math.sin((t - T_CATCH0) * 40)
    slab(ctx, W / 2, bottom, t, p)
    if t >= T_CATCH0:
        cracks(ctx, W / 2, 1400, 520 * ease_out(prog(t, T_CATCH0, T_CATCH0 + 0.4)), GOLD, p, 3)
        for dx, dy, sz in DUST:
            d = (t - T_CATCH0) * 300
            ctx.set_source_rgba(0.8, 0.7, 0.5, 0.6 * max(0, 1 - (t - T_CATCH0) / 1.5))
            ctx.arc(W / 2 + dx * (80 + d), 1400 - dy * 60 - d * 0.1, sz, 0, TAU)
            ctx.fill()
    if T_CATCH0 <= t < T_CATCH0 + 0.08:
        ctx.set_source_rgba(1, 0.95, 0.8, 0.8)
        ctx.paint()
    a = ease_io(prog(t, 1.0, 1.3))
    text(ctx, "He held up", W / 2, 1600, 72, (1, 1, 1), a, FONT_BLACK, 2)
    text(ctx, "a MOUNTAIN...", W / 2, 1690, 80, GOLD, a, FONT_BLACK, 3, glow_col=GREEN)


def scene_rewind(ctx, t):
    ctx.set_source_rgb(0.06, 0.06, 0.04)
    ctx.paint()
    speed_lines(ctx, W / 2, H / 2, t * 3, 0.5, (1, 1, 1))
    for k in range(14):
        y = random.Random(int(t * 60) + k).uniform(0, H)
        ctx.set_source_rgba(1, 0.95, 0.8, 0.15)
        ctx.rectangle(0, y, W, random.Random(k).uniform(2, 12))
        ctx.fill()
    text(ctx, "10 YEARS AGO", W / 2, 980, 92, (1, 1, 1), ease_io(prog(t, T_REWIND + 0.1, T_REWIND + 0.3)),
         FONT_BLACK, 12)


QG = 1450      # quarry ground


def quarry_bg(ctx, t, dusk=0.0):
    g = cairo.LinearGradient(0, 0, 0, QG)
    g.add_color_stop_rgb(0, *tuple(lerp(a, b, dusk) for a, b in zip(hexc("#c9a46a"), hexc("#1a0608"))))
    g.add_color_stop_rgb(1, *tuple(lerp(a, b, dusk) for a, b in zip(hexc("#f2d39b"), hexc("#5a1410"))))
    ctx.set_source(g)
    ctx.paint()
    # stepped quarry cliffs
    for k, (top, col_day, col_dusk) in enumerate(((760, "#9a7a52", "#2a1412"), (930, "#86663f", "#200e0d"),
                                                  (1100, "#6e5232", "#170a09"))):
        col = tuple(lerp(a, b, dusk) for a, b in zip(hexc(col_day), hexc(col_dusk)))
        ctx.set_source_rgb(*col)
        ctx.move_to(-200, QG)
        x = -200
        y = top
        ctx.line_to(x, y)
        r = random.Random(k)
        while x < W + 200:
            x += r.uniform(80, 160)
            ctx.line_to(x, y)
            y = top + r.choice((-40, 0, 40))
            ctx.line_to(x, y)
        ctx.line_to(W + 200, QG)
        ctx.close_path()
        ctx.fill()


def scene_quarry(ctx, t):
    s = t - T_QUARRY
    quarry_bg(ctx, t)
    ctx.set_source_rgb(*hexc("#5a4428"))
    ctx.rectangle(-200, QG, W + 400, 800)
    ctx.fill()
    z = 1.35
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.scale(z, z)
    ctx.translate(-560, -1250)
    # workers carrying rocks, laughing after the boy drops his stone
    for k, (wx, ph) in enumerate(WORKERS):
        laugh = 6 * abs(math.sin(t * 14 + ph)) if t > T_DROPSTONE + 0.2 else 0
        hands = draw_posed(ctx, "carry", BHUMI, wx, QG - laugh, 150, t, 0.0)
        hy = min(h[1] for h in hands)
        ctx.set_source_rgb(*hexc("#7a6248"))
        rock_poly(ctx, wx, hy - 30, 120, 70, 10 + k)
        ctx.fill()
    # the boy
    bx = 520
    if t < T_DROPSTONE:
        wob = 4 * math.sin(t * 18)
        hands = draw_posed(ctx, "struggle", BHUMI, bx + wob, QG, 125, t, 0.0)
        hx = sum(h[0] for h in hands) / 2
        hy = min(h[1] for h in hands)
        ctx.set_source_rgb(*hexc("#8a7256"))
        rock_poly(ctx, hx + 20, hy - 15, 70, 50, 77)
        ctx.fill()
    else:
        draw_posed(ctx, "boy_stand", BHUMI, bx, QG, 125, t, 0.0)
        d = prog(t, T_DROPSTONE, T_DROPSTONE + 0.35)
        ctx.set_source_rgb(*hexc("#8a7256"))
        rock_poly(ctx, bx + 60, lerp(QG - 120, QG - 22, ease_in(d)), 70, 50, 77, d * 1.5)
        ctx.fill()
        for dx, dy, sz in DUST[:30]:
            dd = (t - T_DROPSTONE - 0.35) * 160
            if dd > 0:
                ctx.set_source_rgba(0.85, 0.75, 0.55, max(0, 0.7 - dd / 200))
                ctx.arc(bx + 60 + dx * (30 + dd), QG - 10 - dy * 20 - dd * 0.1, sz, 0, TAU)
                ctx.fill()
    ctx.restore()
    for t0, t1, ls in ((4.0, 6.4, ["...was once called", "USELESS."]),
                       (6.7, 8.9, ["Too weak to lift", "even a small stone."])):
        a = ease_io(prog(t, t0, t0 + 0.4)) * (1 - ease_io(prog(t, t1 - 0.4, t1)))
        for j, ln in enumerate(ls):
            text(ctx, ln, W / 2, 380 + j * 90, 66, (0.12, 0.08, 0.04), a, FONT_BLACK if "USELESS" in ln else FONT, 2)


CAVE_X = 760


def quake_layers(ctx, t, boy_fn):
    dusk = ease_io(prog(t, T_QUAKE, T_QUAKE + 1.0))
    quarry_bg(ctx, t, dusk)
    ctx.push_group()
    draw_villain(ctx, W / 2, -60, 0.85, t, ease_out(prog(t, 10.0, 10.4)), 0.8)
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(0.5 * dusk)
    # cave in the cliff
    ctx.set_source_rgb(0.03, 0.015, 0.015)
    ctx.move_to(CAVE_X - 230, QG)
    ctx.line_to(CAVE_X - 260, 1060)
    ctx.line_to(CAVE_X + 260, 1040)
    ctx.line_to(CAVE_X + 280, QG)
    ctx.close_path()
    ctx.fill()
    ctx.move_to(CAVE_X - 150, QG)
    ctx.curve_to(CAVE_X - 150, 1190, CAVE_X + 150, 1190, CAVE_X + 150, QG)
    ctx.close_path()
    ctx.set_source_rgb(0, 0, 0)
    ctx.fill()
    glow(ctx, CAVE_X, QG - 80, 160, hexc("#ff9a40"), 0.5)
    # ground
    ctx.set_source_rgb(*tuple(lerp(a, b, dusk) for a, b in zip(hexc("#5a4428"), hexc("#1a0c08"))))
    ctx.rectangle(-300, QG, W + 600, 900)
    ctx.fill()
    if t > 9.5:
        cracks(ctx, 380, QG + 10, 520 * ease_out(prog(t, 9.6, 12.0)), (1, 0.25, 0.15), 0.8, 11, 7, 4)
    boy_fn()
    for x0, ph, sp, sz, spin, seed in FALLING:
        if t < 9.8:
            break
        y = ((ph + (t - 9.8) * sp / 1600) % 1.0) * 1700 - 100
        ctx.set_source_rgb(0.18, 0.12, 0.08)
        rock_poly(ctx, x0, y, sz, sz * 0.8, seed, spin * t)
        ctx.fill()


def kids_in_cave(ctx, t, out=0.0):
    for k in range(3):
        if out <= 0:
            x = CAVE_X - 60 + k * 60
            draw_posed(ctx, "boy_stand", BHUMI, x, QG, 55, t, 0.0)
        else:
            x = lerp(CAVE_X - 60 + k * 60, -200, ease_in(prog(out, k * 0.12, 0.7 + k * 0.12)))
            draw_posed(ctx, run_pose(x * 0.08 + k, 0.25), BHUMI, x, QG, 55, t, 0.0, key=f"kid{k}")


def boy_world_x(t):
    return lerp(300, CAVE_X, ease_io(prog(t, T_RUN, T_RUN + 1.5)))


def scene_quake(ctx, t):
    z = 1.3 + 0.2 * ease_io(prog(t, 15.5, T_CATCH))
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.scale(z, z)
    ctx.translate(-lerp(520, CAVE_X - 40, ease_io(prog(t, T_RUN, T_CATCH))), -1220)

    def boy():
        kids_in_cave(ctx, t)
        if t < T_RUN:
            draw_posed(ctx, "boy_stand", BHUMI, 300 + 3 * math.sin(t * 25), QG, 125, t, 0.0)
        elif t < T_RUN + 1.5:
            x = boy_world_x(t)
            draw_posed(ctx, run_pose(x * 0.03, 0.3), BHUMI, x, QG, 125, t, 0.0, key="boyrun")
        else:
            draw_posed(ctx, "strain", BHUMI, CAVE_X, QG, 125, t, 0.0)
        # ceiling slab coming down
        if t > 16.2:
            fall = ease_in(prog(t, 16.2, T_CATCH))
            slab(ctx, CAVE_X, lerp(1000, QG - (pose_bottom("strain") + 1.6) * 125 + 18, fall), t)
    quake_layers(ctx, t, boy)
    ctx.restore()
    for t0, t1, ls, acc in ((9.4, 12.0, ["Then the darkness", "shook the earth."], False),
                            (12.3, 14.8, ["The children were", "trapped in the cave..."], False),
                            (15.0, 17.4, ["Everyone ran away.", "He ran IN."], True)):
        a = ease_io(prog(t, t0, t0 + 0.4)) * (1 - ease_io(prog(t, t1 - 0.4, t1)))
        for j, ln in enumerate(ls):
            hi = acc and j == 1
            text(ctx, ln, W / 2, 380 + j * 90, 66, GOLD if hi else (1, 1, 1), a, FONT_BLACK if hi else FONT, 2,
                 glow_col=GREEN if hi else None)


def scene_hold(ctx, t):
    z = 1.5 + 0.3 * ease_io(prog(t, T_CATCH, T_DROP))
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.scale(z, z)
    ctx.translate(-CAVE_X + 20, -1260)
    power = ease_out(prog(t, T_GLOW, T_GLOW + 0.5))
    surge = ease_out(prog(t, T_DROP, T_DROP + 0.3))

    def boy():
        kids_in_cave(ctx, t, max(0.0, (t - T_DROP - 0.1) / 1.6))
        squash = 0.92 + 0.03 * math.sin(t * 30) * (1 - surge) + 0.08 * surge
        u = 125 * squash
        hands = draw_posed(ctx, "strain", BHUMI, CAVE_X, QG, u, t, power)
        fist_y = min(h[1] for h in hands)
        slab(ctx, CAVE_X, fist_y - 0.09 * u - 60 * surge, t, power)
        if power > 0:
            cracks(ctx, CAVE_X, QG + 5, 420 * power + 200 * surge, GOLD, power, 21)
            for hx, hy in hands:
                glow(ctx, hx, hy, 120, GREEN, power)
    quake_layers(ctx, t, boy)
    ctx.restore()
    if T_DROP <= t < T_DROP + 0.1:
        ctx.set_source_rgba(0.9, 1, 0.75, 0.9)
        ctx.paint()
    elif t >= T_DROP:
        ctx.set_source_rgba(*GREEN, 0.3 * math.exp(-(t - T_DROP) * 3))
        ctx.paint()


def scene_rise(ctx, t):
    s = t - T_RISE
    ctx.set_source_rgb(*hexc("#100c06"))
    ctx.paint()
    glow(ctx, W / 2, 1000, 1100, GREEN, 0.45)
    speed_lines(ctx, W / 2, 1000, t, 0.2, GOLD)
    ctx.set_source_rgb(0.03, 0.025, 0.02)
    ctx.rectangle(-200, 1400, W + 400, 800)
    ctx.fill()
    grow = ease_io(prog(t, T_RISE + 0.3, T_RISE + 2.2))
    u = lerp(140, 290, grow)
    cracks(ctx, W / 2, 1405, 600, GOLD, 0.9, 31)
    # orbiting rocks rushing in
    for ang, rad, sz, sp, seed in ORBIT:
        a = ang + t * sp * 2
        rr = rad * (1.2 - 0.5 * grow)
        px, py = W / 2 + math.cos(a) * rr, 1400 - 0.9 * u + math.sin(a) * rr * 0.4
        if math.sin(a) < 0:
            ctx.set_source_rgb(0.2, 0.15, 0.1)
            rock_poly(ctx, px, py, sz, sz * 0.8, seed, a)
            ctx.fill()
    def hero(name, h):
        y = 1400 - pose_bottom(name) * u
        return draw_hero(ctx, dict(h, pose=name), W / 2, y, u, t, 1.0)
    ctx.push_group()
    hero("strain", BHUMI)
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(1 - grow)
    if grow > 0:
        ctx.push_group()
        hands = hero("bhumi", BHUMI)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(grow)
    for ang, rad, sz, sp, seed in ORBIT:
        a = ang + t * sp * 2
        rr = rad * (1.2 - 0.5 * grow)
        px, py = W / 2 + math.cos(a) * rr, 1400 - 0.9 * u + math.sin(a) * rr * 0.4
        if math.sin(a) >= 0:
            ctx.set_source_rgb(0.22, 0.17, 0.11)
            rock_poly(ctx, px, py, sz, sz * 0.8, seed, a)
            ctx.fill_preserve()
            ctx.set_source_rgba(*GOLD, 0.7)
            ctx.set_line_width(2)
            ctx.stroke()
    a = ease_io(prog(t, T_RISE + 0.6, T_RISE + 1.0)) * (1 - ease_io(prog(t, T_HERO - 0.5, T_HERO)))
    text(ctx, "They called him weak...", W / 2, 380, 62, (1, 1, 1), a, FONT, 1)
    b = ease_io(prog(t, T_RISE + 1.7, T_RISE + 2.1)) * (1 - ease_io(prog(t, T_HERO - 0.5, T_HERO)))
    text(ctx, "He held up a MOUNTAIN.", W / 2, 470, 70, GOLD, b, FONT_BLACK, 2, glow_col=GREEN)


def scene_hero(ctx, t):
    s = t - T_HERO
    ctx.set_source_rgb(*BHUMI["bg"])
    ctx.paint()
    glow(ctx, W / 2, 900, 1000, GREEN, 0.5)
    speed_lines(ctx, W / 2, 900, t, 0.2, GOLD)
    z = 1.0 + 0.06 * prog(t, T_HERO, T_END)
    ctx.save()
    ctx.translate(W / 2, 1300)
    ctx.scale(z, z)
    ctx.translate(-W / 2, -1300)
    ctx.set_source_rgb(0.02, 0.02, 0.01)
    ctx.move_to(-200, 1400)
    ctx.curve_to(300, 1360, 780, 1360, W + 200, 1400)
    ctx.line_to(W + 200, H + 200)
    ctx.line_to(-200, H + 200)
    ctx.close_path()
    ctx.fill()
    u = 290
    y = 1400 - pose_bottom("bhumi") * u
    kit.hero_fx_back(ctx, BHUMI, t, s + 0.4, W / 2, y, u, 1.0)
    hands = draw_hero(ctx, BHUMI, W / 2, y, u, t, 1.0)
    kit.hero_fx_front(ctx, BHUMI, t, s + 0.4, W / 2, y, u, 1.0, hands)
    ctx.restore()
    if s < 0.1:
        ctx.set_source_rgba(1, 0.95, 0.8, 1 - s / 0.1)
        ctx.paint()
    if t >= T_SLAM:
        p = ease_out(prog(t, T_SLAM, T_SLAM + 0.15))
        a = 1 - ease_io(prog(t, T_END - 0.4, T_END))
        ctx.save()
        ctx.translate(W / 2, 1660)
        ctx.scale(lerp(1.8, 1.0, p), lerp(1.8, 1.0, p))
        text(ctx, "BHUMI", 0, 0, 160, (1, 1, 1), p * a, FONT_BLACK, 16, glow_col=GREEN)
        ctx.restore()
        text(ctx, "THE UNBREAKABLE", W / 2, 1745, 44, GOLD, ease_io(prog(t, T_SLAM + 0.3, T_SLAM + 0.7)) * a, FONT, 12)
        text(ctx, "GUARDIAN  #4", W / 2, 1815, 30, (0.95, 1, 0.85), ease_io(prog(t, T_SLAM + 1.2, T_SLAM + 1.7)) * a,
             FONT, 8)
        if t < T_SLAM + 0.08:
            ctx.set_source_rgba(1, 1, 1, 0.7)
            ctx.paint()


def scene_end(ctx, t):
    s = t - T_END
    ctx.set_source_rgb(*hexc("#06050a"))
    ctx.paint()
    a = ease_io(prog(s, 0.1, 0.5))
    text(ctx, "FOUR GUARDIANS", W / 2, 560, 84, (1, 1, 1), a, FONT_BLACK, 6)
    text(ctx, "ARE READY...", W / 2, 650, 60, (0.9, 0.9, 0.95), a, FONT, 6)
    cols = [h["col"] for h in kit.HEROES]
    for k, c in enumerate(cols):
        on = ease_out(prog(s, 0.4 + k * 0.15, 0.6 + k * 0.15))
        x = W / 2 + (k - 1.5) * 140
        glow(ctx, x, 820, 70 * on, c, 0.9)
        ctx.set_source_rgba(*c, on)
        ctx.arc(x, 820, 12 * on, 0, TAU)
        ctx.fill()
    if s > 1.4:
        p = ease_out(prog(s, 1.4, 1.6))
        b = hexc("#ffd166")
        glow(ctx, W / 2, 1080, 260 * p * (1 + 0.08 * math.sin(t * 6)), b, 0.9)
        ctx.set_source_rgba(1, 0.97, 0.85, p)
        ctx.arc(W / 2, 1080, 16 * p, 0, TAU)
        ctx.fill()
        text(ctx, "NEXT:", W / 2, 1260, 46, (1, 0.95, 0.8), p, FONT, 10)
        text(ctx, "THE LAST LIGHT", W / 2, 1360, 96, (1, 1, 1), p, FONT_BLACK, 8, glow_col=b)
    text(ctx, "Subscribe so you don't miss it", W / 2, 1560, 46, (1, 1, 1), ease_io(prog(s, 2.2, 2.7)), FONT, 1)


def draw_frame(i):
    t = i / FPS
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    dx, dy = shake(t)
    ctx.translate(dx, dy)
    ctx.translate(W / 2, H / 2)
    ctx.scale(1.04, 1.04)
    ctx.translate(-W / 2, -H / 2)
    if t < T_REWIND:
        scene_hook(ctx, t)
    elif t < T_QUARRY:
        scene_rewind(ctx, t)
    elif t < T_QUAKE:
        scene_quarry(ctx, t)
    elif t < T_CATCH:
        scene_quake(ctx, t)
    elif t < T_RISE:
        scene_hold(ctx, t)
    elif t < T_HERO:
        scene_rise(ctx, t)
    elif t < T_END:
        scene_hero(ctx, t)
    else:
        scene_end(ctx, t)
    ctx.identity_matrix()
    v = cairo.RadialGradient(W / 2, H / 2, H * 0.3, W / 2, H / 2, H * 0.72)
    v.add_color_stop_rgba(0, 0, 0, 0, 0)
    v.add_color_stop_rgba(1, 0, 0, 0, 0.55)
    ctx.set_source(v)
    ctx.paint()
    if T_QUARRY <= t < T_DROP:
        ctx.set_source_rgba(0.35, 0.2, 0.08, 0.1)
        ctx.paint()
    if t > DUR - 0.6:
        ctx.set_source_rgba(0, 0, 0, prog(t, DUR - 0.6, DUR))
        ctx.paint()
    surf.flush()
    post(surf, t, 0)
    surf.mark_dirty()
    surf.write_to_png(os.path.join(FRAMES, f"f{i:04d}.png"))


# ------------------------------------------------------------------ original score
def make_audio(path):
    import mass_kit as m
    mx = m.Mix(DUR)
    # hook: rumble, catch impact with chant
    mx.add(m.lowpass(m.noise(T_CATCH0), 120) * np.linspace(0, 1, int(T_CATCH0 * m.SR)) ** 2 * 3, 0, 0.8)
    mx.add(m.braam([38, 45, 50]), T_CATCH0, 0.9)
    mx.add(m.taiko(0.8), T_CATCH0, 1.0)
    mx.add(m.chant_hey(48), T_CATCH0, 0.7, 0, 0.4)
    mx.add(m.cymbal(), T_CATCH0, 0.5, 0.3)
    mx.add(m.choir([50, 57, 62], 2.2, "oh"), T_CATCH0 + 0.1, 0.5)
    # rewind
    tt = m.tl(0.8)
    mx.add(np.sin(m.TAU * np.cumsum(np.linspace(600, 40, len(tt))) / m.SR) * np.exp(-tt * 2), T_REWIND, 0.3)
    mx.add((m.lowpass(m.noise(0.8), 1200) * np.exp(-tt * 4))[::-1], T_REWIND, 0.6)
    # quarry: tanpura + bansuri (D, raga-ish minor colour), sad drop
    mx.add(m.tanpura(62, T_QUAKE - T_QUARRY + 1.0), T_QUARRY, 0.35, 0, 0.3)
    melody = [(69, 0.5), (70, 0.25), (69, 0.25), (67, 0.5), (65, 0.5), (64, 0.75), (62, 1.25),
              (65, 0.5), (67, 0.25), (65, 0.25), (64, 0.5), (62, 0.9)]
    mx.add(m.bansuri(melody), T_QUARRY + 0.3, 0.32, -0.2, 0.4)
    mx.add(m.dhol_bass(0.8), T_DROPSTONE + 0.35, 0.5)
    # quake: Varanasi-style slow build in D minor (strings ostinato, choir swell, dhol builds)
    tq = T_QUAKE
    mx.add(m.braam([38, 45, 50]), 10.0, 0.9)
    mx.add(m.taiko(0.7), 10.0, 0.9)
    patt = [50, 50, 62, 50, 53, 50, 62, 50, 52, 50, 60, 50, 53, 50, 57, 50]
    j, t0 = 0, tq + 0.5
    s16 = BEAT / 4
    while t0 < T_CATCH:
        g = 0.12 + 0.2 * prog(t0, tq, T_CATCH)
        mx.add(m.strings_stacc(patt[j % 16]), t0, g, 0.25 if j % 2 else -0.25, 0.2)
        j += 1
        t0 += s16
    mx.add(m.choir([38, 45, 50, 53], 4.5, "ah"), 12.3, 0.45)
    mx.add(m.choir([41, 48, 53, 57], 3.2, "ah"), 14.8, 0.55)
    for b in (12.3, 14.8):
        mx.add(m.braam([38, 45, 50, 53]), b, 0.7)
    k, t0 = 0, tq + 1.0
    while t0 < T_CATCH - 0.2:                      # dhol pattern gets denser
        mx.add(m.dhol_bass(), t0, 0.35 + 0.25 * prog(t0, tq, T_CATCH))
        if t0 > 12.0:
            mx.add(m.dhol_slap(), t0 + BEAT / 2, 0.3, 0.3)
        if t0 > 14.8:
            mx.add(m.dhol_slap(), t0 + BEAT * 0.75, 0.22, -0.3)
        t0 += BEAT
    mx.add(m.riser(T_CATCH - 15.0), 15.0, 0.25)
    # catch: impact, then the strain (held choir + heartbeat), riser into the drop
    mx.add(m.taiko(0.6), T_CATCH, 1.0)
    mx.add(m.braam([36, 43, 48]), T_CATCH, 1.0)
    mx.add(m.cymbal(), T_CATCH, 0.4)
    mx.add(m.choir([50, 57, 62, 65], T_DROP - T_CATCH + 0.3, "oh", 4, 0.3), T_CATCH, 0.5)
    for hb in (17.9, 18.6, 19.2):
        mx.add(m.heartbeat(), hb, 0.7, 0, 0.1)
    mx.add(m.riser(T_DROP - T_GLOW, 300, 3000), T_GLOW, 0.4)
    for k2, n in enumerate((81, 86, 88, 93)):
        mx.add(m.bell(float(m.note(n)), 1.5), T_GLOW + k2 * 0.08, 0.06, 0.2 * (k2 - 1.5))
    # DROP: D major half-time hero groove (Raaka-style weight), original brass melody
    mx.add(m.braam([38, 45, 50, 54, 57], 3.5), T_DROP, 1.1)
    mx.add(m.taiko(0.6), T_DROP, 1.1)
    mx.add(m.cymbal(4), T_DROP, 0.6)
    mx.add(m.chant_hey(50), T_DROP, 0.8, 0, 0.4)
    chords = {"D": [50, 54, 57, 62], "G": [55, 59, 62, 67], "A": [57, 61, 64, 69], "Bm": [59, 62, 66, 71]}
    prog_ = ["D", "G", "Bm", "A", "D", "G", "A"]
    roots = {"D": 38, "G": 43, "A": 45, "Bm": 47}
    for b in range(7):
        bs = T_DROP + b * BAR
        c = prog_[b]
        mx.add(m.choir(chords[c], BAR + 0.4, "ah", 3, 0.2), bs, 0.42)
        nxt = roots[prog_[(b + 1) % 7]]
        mx.add(m.sub808(roots[c] - 12, BAR * 0.7), bs, 0.55, 0, 0.05)
        mx.add(m.sub808(roots[c] - 12, BAR * 0.3, glide_to=nxt - 12), bs + BAR * 0.7, 0.5, 0, 0.05)
        for beat in (0, 1.5, 2.75):
            mx.add(m.kick(), bs + beat * BEAT, 0.75, 0, 0.05)
        for beat in (0, 2.5):
            mx.add(m.dhol_bass(0.9), bs + beat * BEAT, 0.5)
        mx.add(m.clap(), bs + 2 * BEAT, 0.6, 0, 0.35)
        mx.add(m.taiko(1.1), bs + 2 * BEAT, 0.35)
        for e in range(8):
            mx.add(m.dhol_slap(), bs + e * BEAT / 2, 0.16 + 0.12 * (e % 4 == 3), 0.35 * (1 if e % 2 else -1), 0.1)
        if b in (1, 3, 5):
            mx.add(m.chant_hey(50), bs + 2 * BEAT, 0.6, 0, 0.4)
        if b == 3:
            for f in range(6):                     # tom fill into the slam
                mx.add(m.taiko(1.3 + 0.1 * f), bs + 2.5 * BEAT + f * BEAT / 4, 0.4)
    theme = [(62, 1), (69, 1), (66, 0.5), (67, 0.5), (69, 1),
             (71, 1.5), (69, 0.5), (67, 1), (66, 1),
             (64, 1), (66, 0.5), (67, 0.5), (69, 1), (74, 1),
             (73, 1.5), (71, 0.5), (69, 2),
             (74, 1), (81, 1), (78, 0.5), (79, 0.5), (81, 1),
             (83, 1.5), (81, 0.5), (79, 1), (78, 1),
             (76, 1), (78, 1), (81, 2)]
    tm = T_DROP
    for n, d in theme:
        if tm > T_END - 0.2:
            break
        mx.add(m.brass(n, d * BEAT * 0.95), tm, 0.5, 0.1, 0.35)
        mx.add(m.brass(n - 12, d * BEAT * 0.95, 0.7), tm, 0.25, -0.1, 0.35)
        tm += d * BEAT
    mx.add(m.braam([38, 45, 50, 54]), T_SLAM, 1.1)
    mx.add(m.taiko(0.7), T_SLAM, 1.1)
    mx.add(m.cymbal(4), T_SLAM, 0.6)
    mx.add(m.chant_hey(46), T_SLAM, 0.9, 0, 0.5)
    # end card: Bindu's light - soft bell + choir
    mx.add(m.choir([62, 66, 69, 74], 3.5, "oh", 3, 0.8), T_END + 0.2, 0.45)
    for k2, n in enumerate((86, 90, 93, 98)):
        mx.add(m.bell(float(m.note(n)), 2.5), T_END + 1.4 + k2 * 0.12, 0.08, 0.2 * (k2 - 1.5))
    mx.add(m.taiko(0.8), T_END + 1.4, 0.7)
    out = mx.render()
    st = (out.T * 32767).astype(np.int16)
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
    mp4 = os.path.join(HERE, "bhumi_origin.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
                    "-i", os.path.join(FRAMES, "f%04d.png"), "-i", wav,
                    "-c:v", "libx264", "-preset", "slow", "-crf", "27", "-tune", "grain",
                    "-maxrate", "6M", "-bufsize", "12M", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", mp4],
                   check=True)
    print("wrote", mp4)
