"""Series poster for the playlist announcement: 1080x1080 (YouTube post) and 1080x1350 (Instagram).
Usage: python poster.py
"""
import importlib.util
import math
import os

import cairo

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("trailer_kit", os.path.join(HERE, "..", "trailer", "render.py"))
kit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(kit)
_bspec = importlib.util.spec_from_file_location("bindu_ep", os.path.join(HERE, "..", "ep05_bindu_origin", "render.py"))
bep = importlib.util.module_from_spec(_bspec)
_bspec.loader.exec_module(bep)
glow, hexc, text, TAU = kit.glow, kit.hexc, kit.text, kit.TAU
GOLD = hexc("#ffd166")


def outlined(ctx, txt, x, y, size, fill, spacing=4, stroke=8, font=kit.FONT_BLACK):
    ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    widths = [ctx.text_extents(ch).x_advance for ch in txt]
    cx = x - (sum(widths) + spacing * (len(txt) - 1)) / 2
    ctx.new_path()
    for ch, w in zip(txt, widths):
        ctx.move_to(cx, y)
        ctx.text_path(ch)
        cx += w + spacing
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_source_rgba(0.02, 0.0, 0.03, 0.95)
    ctx.set_line_width(stroke)
    ctx.stroke_preserve()
    if isinstance(fill, cairo.Pattern):
        ctx.set_source(fill)
    else:
        ctx.set_source_rgb(*fill)
    ctx.fill()


def poster(path, w, h):
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
    ctx = cairo.Context(s)
    ground = h - 190
    ctx.set_source_rgb(*hexc("#07040c"))
    ctx.paint()
    g = cairo.LinearGradient(0, 0, 0, h)
    g.add_color_stop_rgb(0, *hexc("#0a0310"))
    g.add_color_stop_rgb(0.55, *hexc("#2a0818"))
    g.add_color_stop_rgb(1, *hexc("#06040a"))
    ctx.set_source(g)
    ctx.paint()
    # Andhakaar looming behind
    ctx.save()
    sc = w / 1080
    kit.draw_villain(ctx, w / 2, 40 * sc + (h - w) * 0.25, 0.95 * sc, 2.0, 1.0, 0.9)
    ctx.restore()
    ctx.set_source_rgba(0.03, 0.0, 0.04, 0.35)
    ctx.paint()
    # golden light rising from the heroes
    lg = cairo.RadialGradient(w / 2, ground, 20, w / 2, ground, w * 0.9)
    lg.add_color_stop_rgba(0, 1, 0.8, 0.4, 0.55)
    lg.add_color_stop_rgba(1, 0.3, 0.05, 0.1, 0)
    ctx.set_source(lg)
    ctx.paint()
    for k in range(18):
        ang = -math.pi / 2 + (k - 8.5) * 0.14
        ctx.move_to(w / 2, ground)
        ctx.line_to(w / 2 + math.cos(ang - 0.02) * 1800, ground + math.sin(ang - 0.02) * 1800)
        ctx.line_to(w / 2 + math.cos(ang + 0.02) * 1800, ground + math.sin(ang + 0.02) * 1800)
        ctx.close_path()
        ctx.set_source_rgba(1, 0.85, 0.5, 0.05)
        ctx.fill()
    ctx.set_source_rgb(0.015, 0.01, 0.02)
    ctx.rectangle(0, ground, w, h)
    ctx.fill()
    # heroes
    u = 150 * sc
    for hero, hx in zip(kit.HEROES, (0.15, 0.33, 0.67, 0.85)):
        x = hx * w
        glow(ctx, x, ground - 0.9 * u, 200 * sc, hero["col"], 0.45)
        bottom = max(l[-1][1] for l in kit.POSES[hero["pose"]]["legs"])
        hands = kit.draw_hero(ctx, hero, x, ground - bottom * u, u, 1.0, 1.0)
        kit.hero_fx_front(ctx, hero, 1.0, 1.4, x, ground - bottom * u, u, 0.6, hands)
    bep.bindu(ctx, w / 2, ground + 4, 70 * sc, 1.0, 1.0, (0, -0.1), "smile", 1.6, 1.0, 0.6)
    # title block
    top = 120 * sc
    gold = cairo.LinearGradient(0, top - 90 * sc, 0, top + 20 * sc)
    gold.add_color_stop_rgb(0, *hexc("#fff4cf"))
    gold.add_color_stop_rgb(0.5, *hexc("#ffc94a"))
    gold.add_color_stop_rgb(0.6, *hexc("#c07a12"))
    gold.add_color_stop_rgb(1, *hexc("#ffe08a"))
    text(ctx, "GUARDIANS", w / 2, top, 128 * sc, gold, 1.0, kit.FONT_BLACK, 6, glow_col=hexc("#ff9a00"))
    outlined(ctx, "GUARDIANS", w / 2, top, 128 * sc, gold, 6, 6 * sc)
    outlined(ctx, "OF THE LAST LIGHT", w / 2, top + 72 * sc, 56 * sc, hexc("#ffe7b0"), 8, 6 * sc)
    # badges
    outlined(ctx, "5 HEROES  .  1 DARKNESS", w / 2, h - 105 * sc, 40 * sc, (1, 1, 1), 4, 6 * sc)
    btxt = "FULL STORY  -  WATCH IN ORDER"
    ctx.select_font_face(kit.FONT_BLACK, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(34 * sc)
    ext = ctx.text_extents(btxt)
    pw, ph = ext.x_advance + 120 * sc, 66 * sc
    bx, by = w / 2, h - 45 * sc
    ctx.new_sub_path()
    ctx.arc(bx - pw / 2 + ph / 2, by - ph / 2 + 12 * sc, ph / 2, math.pi / 2, 3 * math.pi / 2)
    ctx.arc(bx + pw / 2 - ph / 2, by - ph / 2 + 12 * sc, ph / 2, -math.pi / 2, math.pi / 2)
    ctx.close_path()
    ctx.set_source_rgb(*GOLD)
    ctx.fill()
    # play triangle
    tx, ty = bx - pw / 2 + 38 * sc, by - ph / 2 + 12 * sc
    ctx.move_to(tx - 9 * sc, ty - 13 * sc)
    ctx.line_to(tx + 14 * sc, ty)
    ctx.line_to(tx - 9 * sc, ty + 13 * sc)
    ctx.close_path()
    ctx.set_source_rgb(0.1, 0.05, 0.02)
    ctx.fill()
    ctx.move_to(bx - ext.x_advance / 2 + 18 * sc, ty + 12 * sc)
    ctx.show_text(btxt)
    v = cairo.RadialGradient(w / 2, h / 2, h * 0.4, w / 2, h / 2, h * 0.8)
    v.add_color_stop_rgba(0, 0, 0, 0, 0)
    v.add_color_stop_rgba(1, 0, 0, 0, 0.5)
    ctx.set_source(v)
    ctx.paint()
    s.write_to_png(path)


if __name__ == "__main__":
    poster(os.path.join(HERE, "guardians_poster_square.png"), 1080, 1080)
    poster(os.path.join(HERE, "guardians_poster_4x5.png"), 1080, 1350)
    print("done")
