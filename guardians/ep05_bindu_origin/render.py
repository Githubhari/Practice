"""GUARDIANS OF THE LAST LIGHT - Origin #5: BINDU, The Last Light  (1080x1920, 35 s)

The last star escaped the darkness, fell to Earth and woke up as Bindu.
Every Guardian's power began with one spark of its light.
Visuals reuse ../trailer/render.py; the score uses ../../music/mass_kit.py.
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
GOLD = hexc("#ffd166")
WARM = hexc("#fff3c4")
HEROES = kit.HEROES

BEAT = 60 / 144
BAR = 4 * BEAT
# ------------------------------------------------------------------ timeline
T_CARD, T_STARS, T_ESCAPE = 2.8, 3.6, 7.0
T_FALL, T_LAND, T_SPROUT, T_EYES = 9.0, 9.6, 12.0, 12.6
T_HEAL, T_BRAVE, T_SHINE = 15.0, 17.3, 17.8
T_MONTAGE = 21.0
T_SLAM = T_MONTAGE + 4 * BAR
T_END = T_SLAM + 2.5 * BAR
SHAKES = [(1.6, 25), (T_CARD, 8), (T_ESCAPE, 18), (T_LAND, 35), (T_SHINE, 20),
          (T_SLAM, 35), (T_END + 0.6, 10)]
SHAKES += [(T_MONTAGE + k * BAR + 0.35, 22) for k in range(4)]


def shake(t):
    amp = sum(s * math.exp(-(t - ts) * 5) for ts, s in SHAKES if t >= ts)
    r = random.Random(int(t * FPS))
    return r.uniform(-amp, amp), r.uniform(-amp, amp)


def pose_bottom(name):
    return max(l[-1][1] for l in kit.POSES[name]["legs"])


# ------------------------------------------------------------------ Bindu
def bindu(ctx, x, y, R, t, eyes=1.0, look=(0.0, 0.0), mood="smile", glow_a=0.8, sprout=1.0, brave=0.0):
    """Cute Bindu (y = ground contact)."""
    cy = y - R
    glow(ctx, x, cy, R * 4.5, GOLD, 0.7 * glow_a)
    ctx.set_source_rgba(0, 0, 0, 0.25)
    ctx.save()
    ctx.translate(x, y + 3)
    ctx.scale(R, R * 0.18)
    ctx.arc(0, 0, 1, 0, TAU)
    ctx.restore()
    ctx.fill()
    g = cairo.RadialGradient(x - R * 0.33, cy - R * 0.45, R * 0.1, x, cy, R * 1.3)
    g.add_color_stop_rgb(0, *hexc("#fff0c2"))
    g.add_color_stop_rgb(0.6, *hexc("#ffb347"))
    g.add_color_stop_rgb(1, *hexc("#e0662a"))
    ctx.set_source(g)
    ctx.arc(x, cy, R, 0, TAU)
    ctx.fill()
    if sprout > 0:
        s = sprout
        ctx.set_source_rgb(*hexc("#5cc46a"))
        ctx.set_line_width(R * 0.08)
        top = cy - R
        ctx.move_to(x, top + 2)
        ctx.curve_to(x + 2, top - R * 0.22 * s, x + R * 0.14 * s, top - R * 0.32 * s, x + R * 0.27 * s, top - R * 0.36 * s)
        ctx.stroke()
        ctx.save()
        ctx.translate(x + R * 0.32 * s, top - R * 0.38 * s)
        ctx.rotate(-0.5 + 0.15 * math.sin(t * 3))
        ctx.scale(R * 0.2 * s, R * 0.1 * s)
        ctx.arc(0, 0, 1, 0, TAU)
        ctx.restore()
        ctx.fill()
    lx, ly = look
    for side in (-1, 1):
        ex, ey = x + side * 0.34 * R, cy - 0.18 * R
        if eyes < 0.12:
            ctx.set_source_rgb(*hexc("#5a2330"))
            ctx.set_line_width(R * 0.06)
            ctx.arc(ex, ey, R * 0.15, 0.25, math.pi - 0.25)
            ctx.stroke()
            continue
        ctx.save()
        ctx.translate(ex, ey)
        ctx.scale(1, eyes)
        ctx.set_source_rgb(1, 1, 1)
        ctx.arc(0, 0, 0.24 * R, 0, TAU)
        ctx.fill()
        ctx.set_source_rgb(*hexc("#2a1b3d"))
        ctx.arc(lx * 0.09 * R, ly * 0.09 * R, 0.135 * R, 0, TAU)
        ctx.fill()
        ctx.set_source_rgb(1, 1, 1)
        ctx.arc(lx * 0.09 * R + 0.05 * R, ly * 0.09 * R - 0.06 * R, 0.045 * R, 0, TAU)
        ctx.fill()
        ctx.restore()
    if brave > 0:
        ctx.set_source_rgba(*hexc("#7a2f12"), brave)
        ctx.set_line_width(R * 0.06)
        for side in (-1, 1):
            ctx.move_to(x + side * 0.52 * R, cy - 0.5 * R)
            ctx.line_to(x + side * 0.18 * R, cy - 0.42 * R)
        ctx.stroke()
    ctx.set_source_rgba(1, 0.45, 0.55, 0.6)
    for side in (-1, 1):
        ctx.save()
        ctx.translate(x + side * 0.64 * R, cy + 0.2 * R)
        ctx.scale(0.19 * R, 0.11 * R)
        ctx.arc(0, 0, 1, 0, TAU)
        ctx.restore()
        ctx.fill()
    ctx.set_source_rgb(*hexc("#5a2330"))
    my = cy + 0.18 * R
    if mood == "smile":
        ctx.set_line_width(R * 0.055)
        ctx.arc(x, my - R * 0.06, 0.17 * R, 0.35, math.pi - 0.35)
        ctx.stroke()
    elif mood == "o":
        ctx.save()
        ctx.translate(x, my + 2)
        ctx.scale(0.09 * R, 0.12 * R)
        ctx.arc(0, 0, 1, 0, TAU)
        ctx.restore()
        ctx.fill()
    elif mood == "open":
        ctx.arc(x, my, 0.19 * R, 0, math.pi)
        ctx.close_path()
        ctx.fill()


# ------------------------------------------------------------------ static data
R0 = random.Random(77)
STARS = [(R0.uniform(0, W), R0.uniform(0, 1500), R0.uniform(0.8, 3.0), R0.uniform(0, TAU)) for _ in range(300)]
SPARKS = [(R0.uniform(0, TAU), R0.uniform(120, 520), R0.uniform(2, 6)) for _ in range(90)]
GRASS = [(x, R0.uniform(20, 50), R0.uniform(-6, 6)) for x in range(-40, W + 60, 11)]
FLOWERS = [(x, R0.uniform(-30, 30), R0.choice(["#ff6b9a", "#ffd166", "#7fd4ff", "#b48cff", "#ff8c5a"]))
           for x in (120, 250, 380, 700, 830, 960)]
LAST_STAR = (540, 760)
GROUND = 1420


def star_shape(ctx, x, y, ro, ri, n=4, rot=0.0):
    for k in range(2 * n):
        r = ro if k % 2 == 0 else ri
        a = rot + k * math.pi / n
        (ctx.line_to if k else ctx.move_to)(x + r * math.cos(a), y + r * math.sin(a))
    ctx.close_path()


# ------------------------------------------------------------------ scenes
def scene_hook(ctx, t):
    ctx.set_source_rgb(0, 0, 0.01)
    ctx.paint()
    eyes = ease_out(prog(t, 0.1, 0.5))
    ctx.push_group()
    draw_villain(ctx, W / 2, -120, 1.0, t, eyes, 0.6)
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(0.75)
    flare = ease_out(prog(t, 1.6, 1.9))
    # tendrils reaching for the tiny light, recoiling on the flare
    reach = ease_io(prog(t, 0.3, 1.6)) * (1 - flare)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(6):
        side = -1 if k % 2 else 1
        sx = W / 2 + side * (180 + 60 * k)
        ex, ey = lerp(sx, W / 2 + side * 40, reach), lerp(700, 1330, reach)
        ctx.set_source_rgba(0.03, 0.0, 0.05, 0.95)
        ctx.set_line_width(26 - 2 * k)
        ctx.move_to(sx, 650)
        ctx.curve_to(sx + side * 60, 900 + 30 * math.sin(t * 3 + k), ex - side * 120, ey - 200, ex, ey)
        ctx.stroke()
        ctx.set_source_rgba(1, 0.15, 0.25, 0.4)
        ctx.set_line_width(2)
        ctx.move_to(sx, 650)
        ctx.curve_to(sx + side * 60, 900 + 30 * math.sin(t * 3 + k), ex - side * 120, ey - 200, ex, ey)
        ctx.stroke()
    pulse = 1 + 0.15 * math.sin(t * 8)
    glow(ctx, W / 2, 1360, (60 + 500 * flare) * pulse, GOLD, 0.9)
    ctx.set_source_rgb(1, 0.98, 0.88)
    ctx.arc(W / 2, 1360, 7 + 10 * flare, 0, TAU)
    ctx.fill()
    if 1.6 <= t < 1.68:
        ctx.set_source_rgba(1, 0.95, 0.8, 0.85)
        ctx.paint()
    a = ease_io(prog(t, 0.6, 0.9))
    text(ctx, "The darkness feared", W / 2, 1600, 66, (1, 1, 1), a, FONT, 2)
    text(ctx, "only ONE thing...", W / 2, 1690, 76, GOLD, a, FONT_BLACK, 3, glow_col=hexc("#ffb000"))


def scene_card(ctx, t):
    ctx.set_source_rgb(0, 0, 0)
    ctx.paint()
    a = ease_io(prog(t, T_CARD + 0.05, T_CARD + 0.3)) * (1 - ease_io(prog(t, T_STARS - 0.15, T_STARS)))
    text(ctx, "BEFORE THE GUARDIANS...", W / 2, 980, 62, (1, 1, 1), a, FONT_BLACK, 8)


def scene_stars(ctx, t):
    s = t - T_STARS
    ctx.set_source_rgb(*hexc("#050b1f"))
    ctx.paint()
    g = cairo.RadialGradient(*LAST_STAR, 50, *LAST_STAR, 1300)
    g.add_color_stop_rgba(0, 0.25, 0.3, 0.6, 0.5)
    g.add_color_stop_rgba(1, 0.05, 0.05, 0.15, 0)
    ctx.set_source(g)
    ctx.paint()
    lx, ly = LAST_STAR
    close = ease_io(prog(t, T_STARS, T_ESCAPE))     # darkness ring radius closing in on the last star
    radius = lerp(1500, 120, close)
    for sx, sy, r, ph in STARS:
        d = math.hypot(sx - lx, sy - ly)
        if d < radius:
            a = 0.6 + 0.4 * math.sin(t * 3 + ph)
            ctx.set_source_rgba(1, 1, 0.95, a)
            ctx.arc(sx, sy, r, 0, TAU)
            ctx.fill()
        elif d < radius + 60:
            glow(ctx, sx, sy, r * 8, (1, 0.5, 0.6), 0.6 * (1 - (d - radius) / 60))
    # darkness mass with wavy inner edge
    ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    ctx.rectangle(-300, -300, W + 600, H + 600)
    for k in range(60):
        a = k * TAU / 60
        rr = radius + 25 * math.sin(a * 7 + t * 4) + 15 * math.sin(a * 13 - t * 5)
        (ctx.line_to if k else ctx.move_to)(lx + math.cos(a) * rr, ly + math.sin(a) * rr)
    ctx.close_path()
    ctx.set_source_rgb(0.01, 0.0, 0.02)
    ctx.fill()
    ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
    for k in range(60):
        a = k * TAU / 60
        rr = radius + 25 * math.sin(a * 7 + t * 4) + 15 * math.sin(a * 13 - t * 5)
        (ctx.line_to if k else ctx.move_to)(lx + math.cos(a) * rr, ly + math.sin(a) * rr)
    ctx.close_path()
    ctx.set_source_rgba(1, 0.15, 0.25, 0.5)
    ctx.set_line_width(6)
    ctx.stroke()
    # the last star: shrinks, then escapes downward
    if t < T_ESCAPE:
        p = 1 + 0.15 * math.sin(t * 9)
        size = lerp(46, 30, close)
        glow(ctx, lx, ly, size * 5 * p, WARM, 0.9)
        star_shape(ctx, lx, ly, size * p, size * 0.35 * p, 4, t * 0.6)
        ctx.set_source_rgb(1, 0.98, 0.9)
        ctx.fill()
    else:
        q = ease_in(prog(t, T_ESCAPE, T_ESCAPE + 1.2))
        x, y = lerp(lx, 820, q), lerp(ly, 2100, q)
        for k in range(18):
            qq = max(0, q - k * 0.02)
            px, py = lerp(lx, 820, qq), lerp(ly, 2100, qq)
            glow(ctx, px, py, 40 * (1 - k / 18), WARM, 0.7 * (1 - k / 18))
        glow(ctx, x, y, 160, WARM, 0.9)
        ring = ease_out(prog(t, T_ESCAPE, T_ESCAPE + 0.5))
        if ring < 1:
            ctx.set_source_rgba(1, 0.95, 0.8, 0.8 * (1 - ring))
            ctx.set_line_width(10 * (1 - ring) + 1)
            ctx.arc(lx, ly, 40 + 500 * ring, 0, TAU)
            ctx.stroke()
    for t0, t1, ls, acc in ((3.9, 6.6, ["When Andhakaar", "swallowed the stars..."], False),
                            (7.0, 8.9, ["...ONE star", "escaped."], True)):
        a = ease_io(prog(t, t0, t0 + 0.4)) * (1 - ease_io(prog(t, t1 - 0.4, t1)))
        for j, ln in enumerate(ls):
            hi = acc
            text(ctx, ln, W / 2, 1500 + j * 90, 70, GOLD if hi else (1, 1, 1), a, FONT_BLACK if hi else FONT, 2,
                 glow_col=hexc("#ffb000") if hi else None)


def meadow(ctx, t, bloom=0.0):
    g = cairo.LinearGradient(0, 0, 0, GROUND)
    g.add_color_stop_rgb(0, *hexc("#050a1c"))
    g.add_color_stop_rgb(1, *tuple(lerp(a, b, bloom) for a, b in zip(hexc("#14214a"), hexc("#3a3060"))))
    ctx.set_source(g)
    ctx.paint()
    r = random.Random(3)
    for _ in range(140):
        sx, sy = r.uniform(0, W), r.uniform(0, 1100)
        ctx.set_source_rgba(1, 1, 1, (0.15 + 0.6 * bloom) * r.random())
        ctx.arc(sx, sy, r.uniform(0.8, 2), 0, TAU)
        ctx.fill()
    for base, amp, ph, col in ((1250, 50, 1.0, "#1a2550"), (1330, 35, 3.0, "#121a3a")):
        ctx.set_source_rgb(*hexc(col))
        ctx.move_to(-200, H + 200)
        for x in range(-200, W + 220, 20):
            ctx.line_to(x, base - amp * math.sin(x * 0.006 + ph))
        ctx.line_to(W + 220, H + 200)
        ctx.close_path()
        ctx.fill()
    ctx.set_source_rgb(*hexc("#0b1128"))
    ctx.rectangle(-200, GROUND, W + 400, 800)
    ctx.fill()


def grass(ctx, t):
    ctx.set_source_rgb(*hexc("#070c1c"))
    for gx, gh, lean in GRASS:
        sway = lean + 4 * math.sin(t * 1.5 + gx * 0.05)
        ctx.move_to(gx - 4, GROUND + 30)
        ctx.curve_to(gx - 2, GROUND + 30 - gh * 0.5, gx, GROUND + 30 - gh * 0.8, gx + sway, GROUND + 30 - gh)
        ctx.curve_to(gx + 1, GROUND + 30 - gh * 0.8, gx + 2, GROUND + 30 - gh * 0.5, gx + 4, GROUND + 30)
        ctx.close_path()
        ctx.fill()


def flower(ctx, x, y, col, bloom, t, wilt=0.0):
    stem_top = y - 90 + 30 * wilt
    ctx.set_source_rgb(*tuple(lerp(a, b, wilt) for a, b in zip(hexc("#4caf50"), hexc("#3a3a3a"))))
    ctx.set_line_width(5)
    ctx.move_to(x, y)
    ctx.curve_to(x - 5, y - 40, x + 20 * wilt, stem_top + 20, x + 30 * wilt, stem_top)
    ctx.stroke()
    fx, fy = x + 30 * wilt, stem_top
    c = tuple(lerp(a, b, wilt) for a, b in zip(hexc(col), (0.35, 0.35, 0.38)))
    pr = 8 + 16 * bloom
    if bloom > 0.5:
        glow(ctx, fx, fy, 70 * bloom, hexc(col), 0.35)
    for k in range(6):
        a = k * TAU / 6 + 0.3 * t * bloom
        ctx.save()
        ctx.translate(fx + math.cos(a) * pr * 0.8, fy + math.sin(a) * pr * 0.8)
        ctx.rotate(a)
        ctx.scale(pr * 0.7, pr * 0.4)
        ctx.arc(0, 0, 1, 0, TAU)
        ctx.restore()
        ctx.set_source_rgb(*c)
        ctx.fill()
    ctx.set_source_rgb(*tuple(lerp(a, b, wilt) for a, b in zip(hexc("#ffd166"), (0.3, 0.3, 0.3))))
    ctx.arc(fx, fy, pr * 0.35, 0, TAU)
    ctx.fill()


def wisp(ctx, x, y, t, a=1.0, s=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(-40, 30)
    for k in range(9):
        ang = math.pi + k * math.pi / 8
        rr = 45 + 8 * math.sin(t * 6 + k)
        ctx.line_to(math.cos(ang) * rr, math.sin(ang) * rr * 1.3)
    ctx.line_to(40, 30)
    for k in range(5):
        ctx.line_to(40 - k * 20, 30 + (14 if k % 2 == 0 else 0) + 6 * math.sin(t * 8 + k))
    ctx.close_path()
    ctx.set_source_rgba(0.03, 0.0, 0.05, 0.95 * a)
    ctx.fill_preserve()
    ctx.set_source_rgba(1, 0.15, 0.25, 0.6 * a)
    ctx.set_line_width(2)
    ctx.stroke()
    for side in (-1, 1):
        glow(ctx, side * 14, -12, 18, (1, 0.1, 0.2), 0.8 * a)
        ctx.set_source_rgba(1, 0.6, 0.6, a)
        ctx.arc(side * 14, -12, 4, 0, TAU)
        ctx.fill()
    ctx.restore()


def scene_meadow(ctx, t):
    bloom_all = ease_io(prog(t, 19.0, 20.6))
    z = 1.45 + 0.35 * ease_io(prog(t, T_LAND + 1.0, T_EYES)) - 0.3 * ease_io(prog(t, T_HEAL, T_HEAL + 1.0))
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.scale(z, z)
    ctx.translate(-W / 2, -1300)
    meadow(ctx, t, bloom_all)
    bx = 540
    # falling star
    if t < T_LAND:
        q = ease_in(prog(t, T_FALL, T_LAND))
        x, y = lerp(-100, bx, q), lerp(-200, GROUND - 20, q)
        for k in range(16):
            qq = max(0, q - k * 0.03)
            glow(ctx, lerp(-100, bx, qq), lerp(-200, GROUND - 20, qq), 50 * (1 - k / 16), WARM, 0.8 * (1 - k / 16))
        glow(ctx, x, y, 140, WARM, 1.0)
    else:
        dt = t - T_LAND
        crater = 1 - 0.5 * prog(t, T_LAND, T_LAND + 2)
        ctx.set_source_rgba(0.02, 0.02, 0.05, 0.9)
        ctx.save()
        ctx.translate(bx, GROUND + 6)
        ctx.scale(150, 22)
        ctx.arc(0, 0, 1, 0, TAU)
        ctx.restore()
        ctx.fill()
        if dt < 1.5:
            for ang, sp, sz in SPARKS[:50]:
                d = sp * ease_out(dt / 1.5) * 0.6
                ctx.set_source_rgba(1, 0.9, 0.6, 1 - dt / 1.5)
                ctx.arc(bx + math.cos(ang) * d, GROUND - abs(math.sin(ang)) * d * 0.8, sz * 0.6, 0, TAU)
                ctx.fill()
        # flowers around: wilted until Bindu shines
        for k, (fx, fo, col) in enumerate(FLOWERS):
            fb = ease_out(prog(t, 19.0 + 0.2 * abs(k - 2.5), 19.6 + 0.2 * abs(k - 2.5)))
            flower(ctx, fx, GROUND + 25, col, fb, t, wilt=1 - fb)
        # the spark becomes Bindu
        form = ease_io(prog(t, T_LAND + 0.6, T_SPROUT))
        R = lerp(16, 62, form)
        if form < 0.02:
            glow(ctx, bx, GROUND - 25, 100, WARM, 1.0)
            ctx.set_source_rgb(1, 0.98, 0.9)
            ctx.arc(bx, GROUND - 20, 14, 0, TAU)
            ctx.fill()
        else:
            eyes = ease_out(prog(t, T_EYES, T_EYES + 0.2))
            for bt in (13.6, 16.0, 20.4):
                if abs(t - bt) < 0.08:
                    eyes = 0.1
            look = (0.0, 0.0)
            mood = "smile"
            brave = 0.0
            if 13.0 < t < 14.8:
                look = (math.sin((t - 13.0) * 3.2), -0.3)
            if T_HEAL < t < T_SHINE:
                look = (1.0, 0.1)
                mood = "o"
            if t >= T_BRAVE:
                brave = ease_out(prog(t, T_BRAVE, T_BRAVE + 0.3)) * (1 - prog(t, 19.8, 20.3))
                mood = "smile" if t < T_SHINE else "open"
            if t > 20.0:
                mood = "smile"
                look = (0.0, -0.2)
            hop = 0.0
            if 14.0 < t < 14.5:
                hop = 50 * math.sin(math.pi * prog(t, 14.0, 14.5))
            shine = ease_out(prog(t, T_SHINE, T_SHINE + 0.3)) * (1 - 0.6 * prog(t, 19.2, 20.5))
            bindu(ctx, bx, GROUND - hop, R, t, eyes if t >= T_EYES else 0.0, look, mood,
                  0.6 + 2.0 * shine, ease_back(prog(t, T_SPROUT, T_SPROUT + 0.4)) if t >= T_SPROUT else 0.0, brave)
            if shine > 0:
                ring = ease_out(prog(t, T_SHINE, T_SHINE + 1.0))
                ctx.set_source_rgba(1, 0.9, 0.6, 0.8 * (1 - ring))
                ctx.set_line_width(14 * (1 - ring) + 2)
                ctx.arc(bx, GROUND - R, 80 + 700 * ring, 0, TAU)
                ctx.stroke()
        # the shadow wisp attacking the nearest flower
        if T_HEAL - 0.5 < t < T_SHINE + 0.6:
            come = ease_out(prog(t, T_HEAL - 0.5, 16.5))
            dissolve = prog(t, T_SHINE + 0.1, T_SHINE + 0.6)
            wisp(ctx, lerp(1200, 760, come), GROUND - 140, t, 1 - dissolve, 1 + 0.5 * dissolve)
    grass(ctx, t)
    ctx.restore()
    if T_LAND <= t < T_LAND + 0.1:
        ctx.set_source_rgba(1, 0.95, 0.8, 0.9)
        ctx.paint()
    if T_SHINE <= t < T_SHINE + 0.6:
        ctx.set_source_rgba(1, 0.92, 0.7, 0.5 * (1 - prog(t, T_SHINE, T_SHINE + 0.6)))
        ctx.paint()
    for t0, t1, ls, acc in ((9.8, 12.2, ["It fell to Earth..."], False),
                            (12.6, 14.9, ["...and woke up as", "BINDU."], True),
                            (15.2, 17.6, ["So small...", "the darkness laughed."], False),
                            (18.3, 20.9, ["But its light could", "HEAL what darkness broke."], True)):
        a = ease_io(prog(t, t0, t0 + 0.4)) * (1 - ease_io(prog(t, t1 - 0.4, t1)))
        for j, ln in enumerate(ls):
            hi = acc and j == len(ls) - 1
            text(ctx, ln, W / 2, 380 + j * (130 if ln == "BINDU." else 90), 68 if not (hi and ln == "BINDU.") else 110,
                 GOLD if hi else (1, 1, 1), a, FONT_BLACK if hi else FONT, 2,
                 glow_col=hexc("#ffb000") if hi else None)


def ease_back(x):
    c = 1.9
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def scene_montage(ctx, t):
    k = min(3, int((t - T_MONTAGE) / BAR))
    s = t - (T_MONTAGE + k * BAR)
    h = HEROES[k]
    arrive = ease_in(prog(s, 0.0, 0.35))
    power = ease_out(prog(s, 0.35, 0.6))
    ctx.set_source_rgb(*h["bg"])
    ctx.paint()
    glow(ctx, W / 2, 950, 1000, h["col"], 0.2 + 0.5 * power)
    speed_lines(ctx, W / 2, 950, t, 0.1 + 0.25 * power, h["col2"])
    ctx.set_source_rgb(0.02, 0.02, 0.03)
    ctx.rectangle(-200, 1400, W + 400, 800)
    ctx.fill()
    u = 260
    y = 1400 - pose_bottom(h["pose"]) * u
    kit.hero_fx_back(ctx, h, t, s + 0.4, W / 2, y, u, power)
    hands = draw_hero(ctx, h, W / 2, y, u, t, power)
    kit.hero_fx_front(ctx, h, t, s + 0.4, W / 2, y, u, power, hands)
    # Bindu at the bottom sending the spark
    bindu(ctx, W / 2, 1830, 46, t, 1.0, (0, -1), "open", 1.2, 1.0, 0.8)
    sy = lerp(1740, y - 0.6 * u, arrive)
    if s < 0.4:
        for j in range(12):
            yy = lerp(1740, y - 0.6 * u, max(0, arrive - j * 0.04))
            glow(ctx, W / 2, yy, 34 * (1 - j / 12), h["col"], 0.8 * (1 - j / 12))
        glow(ctx, W / 2, sy, 90, WARM, 1.0)
    if 0.35 <= s < 0.43:
        ctx.set_source_rgba(*h["col2"], 0.7)
        ctx.paint()
    a = ease_io(prog(t, T_MONTAGE + 0.2, T_MONTAGE + 0.6)) * (1 - ease_io(prog(t, T_SLAM - 0.35, T_SLAM)))
    text(ctx, "Every Guardian's power...", W / 2, 360, 62, (1, 1, 1), a, FONT, 1)
    b = ease_io(prog(t, T_MONTAGE + 1.2, T_MONTAGE + 1.6)) * (1 - ease_io(prog(t, T_SLAM - 0.35, T_SLAM)))
    text(ctx, "began with ONE spark.", W / 2, 450, 72, GOLD, b, FONT_BLACK, 2, glow_col=hexc("#ffb000"))
    nm = ease_out(prog(s, 0.35, 0.5))
    text(ctx, h["name"], W / 2, 1600, 110, (1, 1, 1), nm * 0.9, FONT_BLACK, 12, glow_col=h["col"])


def scene_slam(ctx, t):
    s = t - T_SLAM
    ctx.set_source_rgb(*hexc("#0a0712"))
    ctx.paint()
    g = cairo.RadialGradient(W / 2, 1250, 50, W / 2, 1250, 1300)
    g.add_color_stop_rgba(0, 1, 0.8, 0.4, 0.5)
    g.add_color_stop_rgba(1, 0.2, 0.05, 0.2, 0)
    ctx.set_source(g)
    ctx.paint()
    for k in range(22):
        ang = -math.pi / 2 + (k - 10.5) * 0.13 + 0.02 * math.sin(t + k)
        ctx.move_to(W / 2, 1300)
        ctx.line_to(W / 2 + math.cos(ang - 0.025) * 2000, 1300 + math.sin(ang - 0.025) * 2000)
        ctx.line_to(W / 2 + math.cos(ang + 0.025) * 2000, 1300 + math.sin(ang + 0.025) * 2000)
        ctx.close_path()
        ctx.set_source_rgba(1, 0.85, 0.5, 0.06)
        ctx.fill()
    ctx.set_source_rgb(0.02, 0.015, 0.03)
    ctx.rectangle(-200, 1380, W + 400, 800)
    ctx.fill()
    for k, (h, hx) in enumerate(zip(HEROES, (170, 360, 720, 910))):
        u = 170
        glow(ctx, hx, 1380 - 0.9 * u, 220, h["col"], 0.4)
        draw_hero(ctx, h, hx, 1380 - pose_bottom(h["pose"]) * u, u, t, 1.0)
    pop = ease_out(prog(s, 0.0, 0.2))
    bindu(ctx, W / 2, 1390, 95 * (0.6 + 0.4 * pop), t, 1.0, (0, -0.1), "open", 1.8, 1.0, 0.0)
    if s < 0.1:
        ctx.set_source_rgba(1, 0.97, 0.85, 1 - s / 0.1)
        ctx.paint()
    p = ease_out(prog(s, 0.0, 0.15))
    a = 1 - ease_io(prog(t, T_END - 0.4, T_END))
    ctx.save()
    ctx.translate(W / 2, 1660)
    ctx.scale(lerp(1.8, 1.0, p), lerp(1.8, 1.0, p))
    text(ctx, "BINDU", 0, 0, 160, (1, 1, 1), p * a, FONT_BLACK, 16, glow_col=GOLD)
    ctx.restore()
    text(ctx, "THE LAST LIGHT", W / 2, 1745, 46, GOLD, ease_io(prog(s, 0.3, 0.7)) * a, FONT, 12)
    text(ctx, "GUARDIAN  #5", W / 2, 1815, 30, (1, 0.95, 0.85), ease_io(prog(s, 1.2, 1.7)) * a, FONT, 8)


def scene_end(ctx, t):
    s = t - T_END
    ctx.set_source_rgb(*hexc("#06050a"))
    ctx.paint()
    a = ease_io(prog(s, 0.1, 0.5))
    text(ctx, "THE GUARDIANS", W / 2, 560, 92, (1, 1, 1), a, FONT_BLACK, 6)
    text(ctx, "WILL UNITE.", W / 2, 670, 92, GOLD, a, FONT_BLACK, 6, glow_col=hexc("#ffb000"))
    cols = [h["col"] for h in HEROES] + [GOLD]
    for k, c in enumerate(cols):
        on = ease_out(prog(s, 0.5 + k * 0.12, 0.7 + k * 0.12))
        x = W / 2 + (k - 2) * 130
        glow(ctx, x, 860, 70 * on, c, 0.9)
        ctx.set_source_rgba(*c, on)
        ctx.arc(x, 860, (12 if k < 4 else 16) * on, 0, TAU)
        ctx.fill()
    b = ease_io(prog(s, 1.3, 1.7))
    text(ctx, "EPISODE 1", W / 2, 1100, 70, (1, 1, 1), b, FONT_BLACK, 10)
    text(ctx, "C O M I N G   S O O N", W / 2, 1180, 40, (0.9, 0.9, 0.95), b, FONT, 4)
    text(ctx, "Subscribe so you don't miss it", W / 2, 1480, 46, (1, 1, 1), ease_io(prog(s, 2.0, 2.5)), FONT, 1)


def draw_frame(i):
    t = i / FPS
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    dx, dy = shake(t)
    ctx.translate(dx, dy)
    ctx.translate(W / 2, H / 2)
    ctx.scale(1.04, 1.04)
    ctx.translate(-W / 2, -H / 2)
    if t < T_CARD:
        scene_hook(ctx, t)
    elif t < T_STARS:
        scene_card(ctx, t)
    elif t < T_FALL:
        scene_stars(ctx, t)
    elif t < T_MONTAGE:
        scene_meadow(ctx, t)
    elif t < T_SLAM:
        scene_montage(ctx, t)
    elif t < T_END:
        scene_slam(ctx, t)
    else:
        scene_end(ctx, t)
    ctx.identity_matrix()
    v = cairo.RadialGradient(W / 2, H / 2, H * 0.3, W / 2, H / 2, H * 0.72)
    v.add_color_stop_rgba(0, 0, 0, 0, 0)
    v.add_color_stop_rgba(1, 0, 0, 0, 0.55)
    ctx.set_source(v)
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
    # hook: dread drone, heartbeat, a single bell; flare at 1.6
    tt = m.tl(T_CARD)
    mx.add(m.lowpass(m.saw(36.7, tt) + m.saw(36.9, tt), 200) * np.minimum(1, tt / 0.4), 0, 0.5, 0, 0.2)
    mx.add(m.braam([37, 44, 49], 2.0), 0.1, 0.6)
    mx.add(m.heartbeat(), 0.6, 0.8, 0, 0.1)
    mx.add(m.riser(1.0, 300, 2500), 0.6, 0.3)
    mx.add(m.bell(float(m.note(86)), 2.5), 1.6, 0.18)
    mx.add(m.taiko(0.8), 1.6, 0.8)
    mx.add(m.choir([62, 66, 69], 1.3, "oh", 3, 0.05), 1.6, 0.5)
    # card + stars: cosmic choir, tremolo strings, the star's motif on bells
    mx.add(m.choir([50, 57, 62, 65], T_ESCAPE - T_STARS + 0.5, "oh", 3, 1.5), T_STARS, 0.45)
    j, t0 = 0, T_STARS
    while t0 < T_ESCAPE:
        n = [62, 65, 69, 65][j % 4]
        mx.add(m.strings_stacc(n, 0.1), t0, 0.08 + 0.1 * prog(t0, T_STARS, T_ESCAPE), 0.3 * (1 if j % 2 else -1), 0.3)
        j += 1
        t0 += BEAT / 4
    for k2, n in enumerate((74, 78, 81, 86)):
        mx.add(m.bell(float(m.note(n)), 2.0), 4.2 + k2 * 0.5, 0.08, 0.2 * (k2 - 1.5))
    mx.add(m.riser(T_ESCAPE - 5.5, 200, 2000), 5.5, 0.3)
    mx.add(m.braam([38, 45, 50, 54], 2.5), T_ESCAPE, 0.9)
    mx.add(m.cymbal(), T_ESCAPE, 0.4)
    tt = m.tl(1.8)
    mx.add(m.highpass(m.noise(1.8), 800) * np.sin(np.linspace(0, np.pi, len(tt))) ** 2, T_ESCAPE, 0.35)
    # fall + landing
    mx.add(m.riser(T_LAND - T_FALL, 1500, 300), T_FALL, 0.3)
    mx.add(m.taiko(0.6), T_LAND, 1.0)
    mx.add(m.braam([38, 45, 50]), T_LAND, 0.7)
    mx.add(m.cymbal(2.5), T_LAND, 0.35)
    # awakening: tanpura + music-box Bindu theme (D major)
    mx.add(m.tanpura(62, T_HEAL - T_LAND + 0.5, 1.4), T_LAND + 0.3, 0.25, 0, 0.3)
    theme = [(69, 0.5), (74, 0.5), (78, 0.5), (76, 0.5), (74, 1.0), (69, 0.5), (71, 0.5), (74, 1.0),
             (76, 0.5), (78, 0.5), (81, 1.0), (78, 0.5), (76, 0.5), (74, 1.5)]
    tm = T_SPROUT - 0.3
    for n, d in theme:
        mx.add(m.bell(float(m.note(n)), 1.6), tm, 0.12, 0.15, 0.4)
        tm += d * 0.38
    mx.add(m.bell(float(m.note(93)), 1.2), T_EYES, 0.08)           # eyes open twinkle
    mx.add(m.choir([62, 66, 69], 3.0, "oh", 3, 1.0), T_EYES, 0.3)
    # wisp threat -> bravery -> shine (heal)
    tt = m.tl(T_SHINE - T_HEAL)
    mx.add(m.lowpass(m.saw(46, tt) * (0.6 + 0.4 * np.sin(m.TAU * 6 * tt)), 400) * np.minimum(1, tt / 1), T_HEAL, 0.35)
    mx.add(m.braam([37, 44, 49], 2.0), T_HEAL + 0.3, 0.6)
    for hb in (15.8, 16.5, 17.1):
        mx.add(m.heartbeat(), hb, 0.6, 0, 0.1)
    mx.add(m.riser(T_SHINE - T_BRAVE, 400, 3000), T_BRAVE, 0.35)
    mx.add(m.choir([62, 66, 69, 74], 3.2, "ah", 4, 0.1), T_SHINE, 0.6)
    mx.add(m.taiko(0.8), T_SHINE, 0.9)
    mx.add(m.cymbal(3), T_SHINE, 0.4)
    for k2, n in enumerate((81, 86, 88, 90, 93, 98)):              # flowers blooming
        mx.add(m.bell(float(m.note(n)), 1.5), 19.0 + k2 * 0.2, 0.07, 0.3 * (k2 % 2 * 2 - 1))
    # montage: 4 bars, each spark lands on beat 1 + 0.35 s; rising choir progression
    mx.add(m.riser(T_MONTAGE - 19.8, 200, 1800), 19.8, 0.25)
    chords = [[50, 54, 57, 62], [55, 59, 62, 67], [59, 62, 66, 71], [57, 61, 64, 69]]
    for k2 in range(4):
        bs = T_MONTAGE + k2 * BAR
        mx.add(m.choir(chords[k2], BAR + 0.3, "ah", 3, 0.15), bs, 0.4)
        mx.add(m.braam([chords[k2][0] - 12, chords[k2][0] - 5, chords[k2][0]], 1.8), bs + 0.35, 0.7)
        mx.add(m.taiko(0.8), bs + 0.35, 0.9)
        mx.add(m.chant_hey(50 + k2), bs + 0.35, 0.5, 0, 0.4)
        mx.add(m.highpass(m.noise(0.35), 1500) * np.linspace(0, 1, int(0.35 * m.SR)) ** 2, bs, 0.3)   # spark whoosh
        # element sounds
        if k2 == 0:
            tt = m.tl(1.2)
            fire = m.lowpass(m.noise(1.2), 900) * (0.6 + 0.4 * np.abs(np.sin(m.TAU * 7 * tt))) * np.exp(-tt * 1.5)
            mx.add(fire, bs + 0.35, 0.6)
        elif k2 == 1:
            for c in range(4):
                n = m.noise(0.25)
                mx.add(m.highpass(n, 2500) * np.exp(-m.tl(0.25) * 16), bs + 0.35 + c * 0.25, 0.6, 0.3 * (c - 1.5))
        elif k2 == 2:
            tt = m.tl(1.4)
            mx.add(m.lowpass(m.noise(1.4), 600) * (1 + np.sin(m.TAU * 1.5 * tt)) * np.exp(-tt * 1.2), bs + 0.35, 0.8)
        else:
            mx.add(m.lowpass(m.noise(1.5), 150) * np.exp(-m.tl(1.5) * 1.2) * 3, bs + 0.35, 0.9)
        for e in range(8):
            mx.add(m.dhol_slap(), bs + e * BEAT / 2, 0.12 + 0.1 * (k2 / 3), 0.3 * (1 if e % 2 else -1), 0.1)
        for beat in (0, 2.5):
            mx.add(m.dhol_bass(), bs + beat * BEAT, 0.45)
        mx.add(m.sub808(chords[k2][0] - 24, BAR * 0.95), bs, 0.4, 0, 0.05)
    for f in range(6):
        mx.add(m.taiko(1.3 + 0.1 * f), T_SLAM - 1.5 * BEAT + f * BEAT / 4, 0.4)
    # slam: heroic Bindu theme in full
    mx.add(m.braam([38, 45, 50, 54, 57], 3.5), T_SLAM, 1.1)
    mx.add(m.taiko(0.6), T_SLAM, 1.1)
    mx.add(m.cymbal(4), T_SLAM, 0.6)
    mx.add(m.chant_hey(48), T_SLAM, 0.8, 0, 0.5)
    prog_ = [[50, 54, 57, 62], [55, 59, 62, 67], [57, 61, 64, 69]]
    for b in range(3):
        bs = T_SLAM + b * BAR
        if bs > T_END:
            break
        mx.add(m.choir(prog_[b], BAR + 0.4, "ah", 3, 0.2), bs, 0.45)
        mx.add(m.sub808(prog_[b][0] - 24, BAR * 0.95), bs, 0.5, 0, 0.05)
        for beat in (0, 1.5, 2.75):
            mx.add(m.kick(), bs + beat * BEAT, 0.7, 0, 0.05)
        mx.add(m.clap(), bs + 2 * BEAT, 0.55, 0, 0.35)
        for e in range(8):
            mx.add(m.dhol_slap(), bs + e * BEAT / 2, 0.15, 0.3 * (1 if e % 2 else -1), 0.1)
    tm = T_SLAM
    for n, d in theme:
        if tm > T_END - 0.2:
            break
        mx.add(m.brass(n - 12, d * BEAT * 1.9), tm, 0.45, 0.1, 0.35)
        mx.add(m.bell(float(m.note(n)), 1.2), tm, 0.07, -0.2, 0.4)
        tm += d * BEAT * 2
    # end card
    mx.add(m.choir([62, 66, 69, 74], 3.5, "oh", 3, 0.6), T_END + 0.1, 0.45)
    mx.add(m.taiko(0.8), T_END + 1.3, 0.7)
    for k2, n in enumerate((74, 78, 81, 86, 90)):
        mx.add(m.bell(float(m.note(n)), 2.0), T_END + 0.5 + k2 * 0.12, 0.07, 0.25 * (k2 - 2))
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
    mp4 = os.path.join(HERE, "bindu_origin.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
                    "-i", os.path.join(FRAMES, "f%04d.png"), "-i", wav,
                    "-c:v", "libx264", "-preset", "slow", "-crf", "27", "-tune", "grain",
                    "-maxrate", "6M", "-bufsize", "12M", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", mp4],
                   check=True)
    print("wrote", mp4)
