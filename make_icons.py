"""
EDB 通告智能分析系統 — PWA App Icon Generator
Generates premium app icons at 192x192, 512x512 (standard + maskable)
and 180x180 (Apple Touch Icon)
Design: dark navy background · gradient blue arc ring · centered EDB mark · glow
"""
import math, os
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(__file__), "icons")
os.makedirs(OUT, exist_ok=True)

# ── colour palette (matches the system's CSS vars) ──────────────────────────
BG_DARK   = (11,  18,  33)     # #0b1221
BG_MID    = (15,  26,  48)     # slightly lighter navy
BLUE      = (59, 130, 246)     # #3b82f6
CYAN      = ( 6, 182, 212)     # #06b6d4
WHITE     = (255, 255, 255)
GLOW      = (59, 130, 246, 60) # translucent glow

# ── helper: lerp colour ──────────────────────────────────────────────────────
def lerp_colour(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

# ── draw one icon ────────────────────────────────────────────────────────────
def make_icon(size: int, maskable: bool = False) -> Image.Image:
    S = size
    PAD = int(S * (0.12 if maskable else 0.0))   # maskable: 12% safe-zone padding
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # ── background shape ────────────────────────────────────────────────────
    r_bg = S * (0.18 if not maskable else 0.0)   # standard: rounded square
    # for maskable we do full bleed (iOS clips to circle itself)
    draw.rounded_rectangle([0, 0, S-1, S-1],
                            radius=int(r_bg),
                            fill=BG_DARK)

    # ── radial background gradient (subtle) ─────────────────────────────────
    CX, CY = S // 2, S // 2
    # draw concentric circles with very low alpha for depth
    for step in range(20, 0, -1):
        r = int(CX * step / 20)
        alpha = int(18 * (1 - step / 20))
        col = lerp_colour(BG_MID, BG_DARK, step / 20) + (alpha,)
        draw.ellipse([CX-r, CY-r, CX+r, CY+r], fill=col)

    # ── outer glow ring (soft, large) ───────────────────────────────────────
    glow_r = int(S * 0.36)
    for g in range(8, 0, -1):
        gr = glow_r + g * 3
        alpha = int(8 * (1 - g / 8))
        draw.ellipse([CX-gr, CY-gr, CX+gr, CY+gr],
                     outline=(59, 130, 246, alpha), width=2)

    # ── gradient arc ring (main element) ────────────────────────────────────
    arc_outer = int(S * 0.35)
    arc_inner = int(S * 0.27)
    N_SEGMENTS = 180   # smoothness
    ARC_SWEEP  = 300   # degrees of visible arc (leaves a 60° gap at bottom-left)
    START_DEG  = 120   # gap sits at lower-left

    # layer 1: soft outer glow for the arc
    for step in range(N_SEGMENTS):
        t = step / (N_SEGMENTS - 1)
        angle_deg = START_DEG + t * ARC_SWEEP
        angle_rad = math.radians(angle_deg)
        colour = lerp_colour(BLUE, CYAN, t)
        r_mid = (arc_outer + arc_inner) // 2

        # glow dots (slightly outside)
        gx = int(CX + (r_mid + 6) * math.cos(angle_rad))
        gy = int(CY + (r_mid + 6) * math.sin(angle_rad))
        gw = max(1, S // 64)
        draw.ellipse([gx-gw*2, gy-gw*2, gx+gw*2, gy+gw*2],
                     fill=colour + (30,))

    # layer 2: thick arc (fill between outer and inner radius)
    for step in range(N_SEGMENTS):
        t = step / (N_SEGMENTS - 1)
        angle_deg = START_DEG + t * ARC_SWEEP
        angle_rad = math.radians(angle_deg)
        colour = lerp_colour(BLUE, CYAN, t)
        # rasterize as a small filled circle at the arc midpoint
        r_mid = (arc_outer + arc_inner) // 2
        dot_r = max(2, (arc_outer - arc_inner) // 2)
        px = int(CX + r_mid * math.cos(angle_rad))
        py = int(CY + r_mid * math.sin(angle_rad))
        draw.ellipse([px-dot_r, py-dot_r, px+dot_r, py+dot_r],
                     fill=colour + (255,))

    # ── arc end-cap dots (tech feel) ────────────────────────────────────────
    for end_t in [0.0, 1.0]:
        end_angle = math.radians(START_DEG + end_t * ARC_SWEEP)
        r_mid = (arc_outer + arc_inner) // 2
        ex = int(CX + r_mid * math.cos(end_angle))
        ey = int(CY + r_mid * math.sin(end_angle))
        cap_r = max(3, (arc_outer - arc_inner) // 2 + 1)
        c = CYAN if end_t == 1.0 else BLUE
        draw.ellipse([ex-cap_r, ey-cap_r, ex+cap_r, ey+cap_r], fill=c + (255,))

    # ── small orbital dots (AI / network motif) ─────────────────────────────
    for i, (angle, radius_frac, alpha) in enumerate([
        (  30, 0.46, 200),
        ( 210, 0.44, 160),
        ( 155, 0.48, 180),
    ]):
        a = math.radians(angle)
        r = int(S * radius_frac)
        px = int(CX + r * math.cos(a))
        py = int(CY + r * math.sin(a))
        dot_r = max(2, S // 48)
        col = lerp_colour(BLUE, CYAN, i / 3)
        draw.ellipse([px-dot_r, py-dot_r, px+dot_r, py+dot_r],
                     fill=col + (alpha,))

    # ── centre mark: "E" shape (minimal, geometric) ─────────────────────────
    # Draw a clean geometric "E" using rectangles — no font dependency
    em_w  = int(S * 0.20)   # E total width
    em_h  = int(S * 0.24)   # E total height
    bar_h = max(2, int(S * 0.045))
    ex0   = CX - em_w // 2
    ey0   = CY - em_h // 2

    # vertical stroke
    v_w = max(2, int(S * 0.04))
    draw.rectangle([ex0, ey0, ex0 + v_w, ey0 + em_h], fill=WHITE)

    # top bar
    draw.rectangle([ex0, ey0, ex0 + em_w, ey0 + bar_h], fill=WHITE)
    # mid bar (shorter — classic E)
    mid_y = ey0 + em_h // 2 - bar_h // 2
    draw.rectangle([ex0, mid_y, ex0 + int(em_w * 0.82), mid_y + bar_h], fill=WHITE)
    # bottom bar
    draw.rectangle([ex0, ey0 + em_h - bar_h, ex0 + em_w, ey0 + em_h], fill=WHITE)

    # ── apply Gaussian blur to glow layer (composite trick) ─────────────────
    # Blur a copy and composite at low alpha for the glow
    glow_layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)
    r_mid = (arc_outer + arc_inner) // 2
    for step in range(0, N_SEGMENTS, 3):
        t = step / (N_SEGMENTS - 1)
        angle_rad = math.radians(START_DEG + t * ARC_SWEEP)
        colour = lerp_colour(BLUE, CYAN, t)
        px = int(CX + r_mid * math.cos(angle_rad))
        py = int(CY + r_mid * math.sin(angle_rad))
        dot_r = max(3, S // 24)
        gd.ellipse([px-dot_r, py-dot_r, px+dot_r, py+dot_r],
                   fill=colour + (120,))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=S // 20))
    img = Image.alpha_composite(img, glow_layer)

    # ── maskable: ensure rounded corners are visible ─────────────────────────
    if maskable:
        # Add very slight gradient vignette at corners
        mask = Image.new("L", (S, S), 0)
        md = ImageDraw.Draw(mask)
        md.rounded_rectangle([0, 0, S-1, S-1], radius=int(S * 0.22), fill=255)
        img.putalpha(mask)

    return img.convert("RGBA")


# ── generate all sizes ───────────────────────────────────────────────────────
sizes_configs = [
    ("icon-192.png",           192, False),
    ("icon-512.png",           512, False),
    ("icon-192-maskable.png",  192, True),
    ("icon-512-maskable.png",  512, True),
    ("apple-touch-icon.png",   180, False),
    ("favicon-32.png",          32, False),
]

for filename, size, maskable in sizes_configs:
    icon = make_icon(size, maskable)
    path = os.path.join(OUT, filename)
    icon.save(path, "PNG", optimize=True)
    print(f"✓  {filename:35s}  {size}×{size}  maskable={maskable}")

print("\nAll icons generated in ./icons/")
