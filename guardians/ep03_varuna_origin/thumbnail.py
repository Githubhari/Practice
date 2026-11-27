"""Thumbnails for VARUNA origin: vertical (1080x1920) and 16:9 (1280x720).
Usage: python thumbnail.py
"""
import math
import os
import random

import cairo

import render as r

HERE = os.path.dirname(os.path.abspath(__file__))
TEAL, AQUA, VARUNA = r.TEAL, r.AQUA, r.VARUNA


def backdrop(ctx, w, h, cx, ground, scale):
    ctx.set_source_rgb(*r.hexc("#021820"))
    ctx.paint()
    r.glow(ctx, cx, ground - 520 * scale, 1300 * scale, TEAL, 0.6)
    r.speed_lines(ctx, cx, ground - 500 * scale, 3.3, 0.18, AQUA)
    # towering wave behind her
    ctx.save()
    ctx.translate(cx - 540 * scale, ground - 1400 * scale)
    ctx.scale(scale, scale)
    r.big_wave(ctx, -150, 260, 1300, 1.0, r.hexc("#0e6b74"), AQUA)
    ctx.restore()
    # suspended droplets
    rng = random.Random(5)
    for _ in range(140):
        px = cx + rng.uniform(-1, 1) * 620 * scale
        py = ground - rng.uniform(250, 1250) * scale
        sz = rng.uniform(2, 8) * scale
        r.glow(ctx, px, py, sz * 3.5, TEAL, 0.5)
        ctx.set_source_rgba(*AQUA, 0.9)
        ctx.arc(px, py, sz * 0.6, 0, r.TAU)
        ctx.fill()
    # rock
    ctx.set_source_rgb(0.01, 0.03, 0.04)
    ctx.move_to(cx - 360 * scale, ground + 80 * scale)
    ctx.curve_to(cx - 240 * scale, ground - 30 * scale, cx + 240 * scale, ground - 30 * scale,
                 cx + 360 * scale, ground + 80 * scale)
    ctx.line_to(cx + 600 * scale, h + 100)
    ctx.line_to(cx - 600 * scale, h + 100)
    ctx.close_path()
    ctx.fill()


def hero(ctx, x, ground, u):
    y = ground - r.pose_bottom("varuna") * u
    r.kit.hero_fx_back(ctx, VARUNA, 1.0, 1.0, x, y, u, 1.0)
    hands = r.draw_hero(ctx, VARUNA, x, y, u, 1.0, 1.0)
    r.kit.hero_fx_front(ctx, VARUNA, 1.0, 1.0, x, y, u, 1.0, hands)
    for hx, hy in hands:
        r.glow(ctx, hx, hy, 0.6 * u, TEAL, 0.9)


def outlined(ctx, txt, x, y, size, fill, spacing=4, stroke=10):
    """Bold text with a dark outline so it reads on a phone at thumbnail size."""
    ctx.select_font_face(r.FONT_BLACK, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    widths = [ctx.text_extents(ch).x_advance for ch in txt]
    total = sum(widths) + spacing * (len(txt) - 1)
    cx = x - total / 2
    ctx.new_path()
    for ch, w in zip(txt, widths):
        ctx.move_to(cx, y)
        ctx.text_path(ch)
        cx += w + spacing
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_source_rgba(0, 0.05, 0.08, 0.95)
    ctx.set_line_width(stroke)
    ctx.stroke_preserve()
    ctx.set_source_rgb(*fill)
    ctx.fill()


def badge(ctx, x, y, txt, size):
    ctx.select_font_face(r.FONT_BLACK, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    ext = ctx.text_extents(txt)
    pw, ph = ext.x_advance + size * 1.2, size * 1.7
    rr = ph / 2
    ctx.new_sub_path()
    ctx.arc(x - pw / 2 + rr, y, rr, math.pi / 2, 3 * math.pi / 2)
    ctx.arc(x + pw / 2 - rr, y, rr, -math.pi / 2, math.pi / 2)
    ctx.close_path()
    ctx.set_source_rgb(*TEAL)
    ctx.fill()
    ctx.set_source_rgb(0.0, 0.1, 0.12)
    ctx.move_to(x - ext.x_advance / 2, y + size * 0.36)
    ctx.show_text(txt)


def vertical(path):
    w, h = 1080, 1920
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
    ctx = cairo.Context(s)
    backdrop(ctx, w, h, w / 2, 1500, 1.0)
    hero(ctx, w / 2, 1500, 400)
    r.glow(ctx, w / 2, 330, 520, (0, 0, 0), 0.55)
    outlined(ctx, "SHE BECAME", w / 2, 300, 118, (1, 1, 1))
    r.text(ctx, "THE STORM", w / 2, 450, 150, AQUA, 1.0, r.FONT_BLACK, 6, glow_col=TEAL)
    outlined(ctx, "THE STORM", w / 2, 450, 150, AQUA, 6, 8)
    badge(ctx, w / 2, 1690, "GUARDIAN #3  ·  VARUNA", 44)
    v = cairo.RadialGradient(w / 2, h / 2, h * 0.35, w / 2, h / 2, h * 0.75)
    v.add_color_stop_rgba(0, 0, 0, 0, 0)
    v.add_color_stop_rgba(1, 0, 0, 0, 0.55)
    ctx.set_source(v)
    ctx.paint()
    s.write_to_png(path)


def wide(path):
    w, h = 1280, 720
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
    ctx = cairo.Context(s)
    backdrop(ctx, w, h, 900, 640, 0.48)
    hero(ctx, 900, 640, 230)
    g = cairo.LinearGradient(0, 0, 700, 0)
    g.add_color_stop_rgba(0, 0, 0.04, 0.06, 0.85)
    g.add_color_stop_rgba(1, 0, 0.04, 0.06, 0)
    ctx.set_source(g)
    ctx.paint()
    outlined(ctx, "AFRAID OF", 330, 220, 78, (1, 1, 1), 3, 8)
    outlined(ctx, "THE SEA...", 330, 310, 78, (1, 1, 1), 3, 8)
    r.text(ctx, "BECAME", 330, 440, 108, AQUA, 1.0, r.FONT_BLACK, 4, glow_col=TEAL)
    outlined(ctx, "BECAME", 330, 440, 108, AQUA, 4, 8)
    r.text(ctx, "THE STORM", 330, 550, 96, AQUA, 1.0, r.FONT_BLACK, 4, glow_col=TEAL)
    outlined(ctx, "THE STORM", 330, 550, 96, AQUA, 4, 8)
    badge(ctx, 330, 640, "VARUNA · GUARDIAN #3", 26)
    s.write_to_png(path)


if __name__ == "__main__":
    vertical(os.path.join(HERE, "thumbnail_vertical.png"))
    wide(os.path.join(HERE, "thumbnail_16x9.png"))
    print("done")
