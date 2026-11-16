"""
Generator for photorealistic, high-resolution gadget studio renders for all 25 products.
Uses 2x supersampling (1200x1200 -> 600x600 LANCZOS) for buttery smooth anti-aliased curves.
"""
import os
import math
from PIL import Image, ImageDraw, ImageFont

MEDIA_DIR = os.path.join(os.path.dirname(__file__), 'media', 'products', 'main')
os.makedirs(MEDIA_DIR, exist_ok=True)

# High-resolution TrueType fonts for crisp rendering on 1200x1200 canvas
FONT_REGULAR_28 = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 28)
FONT_BOLD_28 = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 28)
FONT_BOLD_36 = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 36)
FONT_BOLD_48 = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 48)
FONT_BOLD_64 = ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf', 64)

W, H = 1200, 1200  # 2x supersampling canvas

def create_studio_canvas():
    canvas = Image.new('RGB', (W, H), '#F8FAFC')
    draw = ImageDraw.Draw(canvas)
    # Subtle soft radial gradient background
    for r in range(W, 300, -20):
        alpha = int(8 * (1 - r / W))
        # Subtle light tone
        draw.ellipse([W//2 - r, H//2 - r, W//2 + r, H//2 + r], fill='#F1F5F9')
    # Inner studio area
    draw.rounded_rectangle([60, 60, W - 60, H - 60], radius=48, fill='#FAFAFA', outline='#E2E8F0', width=4)
    return canvas, draw

def draw_shadow(draw, cx, cy, rx, ry, opacity=40):
    # Oval soft shadow underneath device
    for i in range(8):
        factor = (8 - i) / 8.0
        cur_rx = int(rx + (8 - i) * 8)
        cur_ry = int(ry + (8 - i) * 4)
        draw.ellipse([cx - cur_rx, cy - cur_ry, cx + cur_rx, cy + cur_ry], fill='#E2E8F0')

def draw_clipped_screen(canvas, sx0, sy0, sw, sh, radius, bg_color, draw_fn):
    """Draws screen with perfect rounded-corner clipping so wallpaper never spills over bezels"""
    screen = Image.new('RGBA', (sw, sh), bg_color)
    sdraw = ImageDraw.Draw(screen)
    draw_fn(sdraw, sw, sh)
    
    mask = Image.new('L', (sw, sh), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.rounded_rectangle([0, 0, sw, sh], radius=radius, fill=255)
    
    canvas.paste(screen, (sx0, sy0), mask)

# ================= SMARTPHONES =================

def render_iphone(slug):
    img, draw = create_studio_canvas()
    cx, cy = W // 2, H // 2 - 20
    draw_shadow(draw, cx, cy + 420, 260, 40)
    
    # Phone Body (Natural Titanium)
    pw, ph = 460, 840
    x0, y0 = cx - pw // 2, cy - ph // 2
    draw.rounded_rectangle([x0, y0, x0 + pw, y0 + ph], radius=72, fill='#9CA3AF', outline='#6B7280', width=6)
    draw.rounded_rectangle([x0 + 6, y0 + 6, x0 + pw - 6, y0 + ph - 6], radius=68, fill='#1F2937')
    
    # OLED Screen
    sw, sh = pw - 28, ph - 28
    sx0, sy0 = cx - sw // 2, cy - sh // 2
    
    def iphone_wallpaper(sdraw, w, h):
        sdraw.ellipse([40, 100, w - 40, h // 2 + 100], fill='#3B82F6')
        sdraw.ellipse([80, 260, w - 40, h // 2 + 260], fill='#EC4899')
        sdraw.ellipse([60, 440, w - 60, h - 120], fill='#F59E0B')
        # Dynamic Island inside screen
        di_w, di_h = 160, 48
        sdraw.rounded_rectangle([w // 2 - di_w // 2, 28, w // 2 + di_w // 2, 28 + di_h], radius=24, fill='#000000')
        sdraw.ellipse([w // 2 + 36, 44, w // 2 + 52, 60], fill='#1E293B')
        # Clock
        sdraw.text((w // 2, 160), "09:41", font=FONT_BOLD_48, fill='#FFFFFF', anchor="mm")
        # Home bar
        sdraw.rounded_rectangle([w // 2 - 90, h - 28, w // 2 + 90, h - 20], radius=4, fill='#FFFFFF')

    draw_clipped_screen(img, sx0, sy0, sw, sh, radius=56, bg_color='#0B0F19', draw_fn=iphone_wallpaper)
    return img

def render_nothing_phone(slug):
    img, draw = create_studio_canvas()
    cx, cy = W // 2, H // 2 - 20
    draw_shadow(draw, cx, cy + 420, 260, 40)

    # Phone Body (Dark Smoke Glass)
    pw, ph = 460, 840
    x0, y0 = cx - pw // 2, cy - ph // 2
    draw.rounded_rectangle([x0, y0, x0 + pw, y0 + ph], radius=68, fill='#111827', outline='#374151', width=8)
    
    # Inner transparent glass texture
    draw.rounded_rectangle([x0 + 16, y0 + 16, x0 + pw - 16, y0 + ph - 16], radius=56, fill='#1F2937')
    draw.rounded_rectangle([x0 + 28, y0 + 28, x0 + pw - 28, y0 + ph - 28], radius=48, fill='#0F172A')

    # Dual Camera module at top left
    cam_x = x0 + 100
    draw.ellipse([cam_x - 44, y0 + 90, cam_x + 44, y0 + 178], fill='#111827', outline='#4B5563', width=4)
    draw.ellipse([cam_x - 26, y0 + 108, cam_x + 26, y0 + 160], fill='#000000')
    draw.ellipse([cam_x - 12, y0 + 122, cam_x + 12, y0 + 146], fill='#1E3A8A')
    
    draw.ellipse([cam_x - 44, y0 + 196, cam_x + 44, y0 + 284], fill='#111827', outline='#4B5563', width=4)
    draw.ellipse([cam_x - 26, y0 + 214, cam_x + 26, y0 + 266], fill='#000000')
    draw.ellipse([cam_x - 12, y0 + 228, cam_x + 12, y0 + 252], fill='#1E3A8A')

    # Glowing White LED Glyph Interface Elements!
    glyph_color = '#F8FAFC'
    glyph_w = 12
    # C-shaped arc around cameras
    draw.arc([cam_x - 64, y0 + 70, cam_x + 64, y0 + 304], start=90, end=270, fill=glyph_color, width=glyph_w)
    
    # Wireless charging coil center circle
    coil_r = 140
    draw.ellipse([cx - coil_r, cy - 20 - coil_r, cx + coil_r, cy - 20 + coil_r], outline='#374151', width=8)
    # Glyph strips around coil
    draw.arc([cx - coil_r - 20, cy - 40 - coil_r, cx + coil_r + 20, cy - 40 + coil_r], start=210, end=330, fill=glyph_color, width=glyph_w)
    draw.arc([cx - coil_r - 20, cy - coil_r, cx + coil_r + 20, cy + coil_r], start=30, end=150, fill=glyph_color, width=glyph_w)

    # Diagonal slash glyph top right
    draw.line([x0 + pw - 120, y0 + 110, x0 + pw - 70, y0 + 160], fill=glyph_color, width=glyph_w)

    # Bottom straight glyph
    draw.line([cx - 4, y0 + ph - 140, cx - 4, y0 + ph - 80], fill=glyph_color, width=glyph_w)
    draw.ellipse([cx - 10, y0 + ph - 170, cx + 2, y0 + ph - 158], fill='#EF4444')  # Red recording LED!
    
    return img

def render_samsung(slug):
    img, draw = create_studio_canvas()
    cx, cy = W // 2 - 30, H // 2 - 20
    draw_shadow(draw, cx, cy + 430, 270, 40)

    # Phone Body (S24 Ultra - boxy sharp titanium corners)
    pw, ph = 460, 860
    x0, y0 = cx - pw // 2, cy - ph // 2
    draw.rounded_rectangle([x0, y0, x0 + pw, y0 + ph], radius=24, fill='#475569', outline='#334155', width=6)
    
    # Screen
    sw, sh = pw - 20, ph - 20
    sx0, sy0 = cx - sw // 2, cy - sh // 2
    draw.rounded_rectangle([sx0, sy0, sx0 + sw, sy0 + sh], radius=16, fill='#020617')
    
    # Samsung Crystal AI Wallpaper
    draw.polygon([(sx0 + 60, sy0 + 200), (sx0 + sw - 40, sy0 + 320), (sx0 + 120, sy0 + 600)], fill='#2563EB')
    draw.polygon([(sx0 + sw - 40, sy0 + 320), (sx0 + sw - 100, sy0 + 700), (sx0 + 120, sy0 + 600)], fill='#7C3AED')
    draw.polygon([(sx0 + 60, sy0 + 200), (sx0 + 180, sy0 + 100), (sx0 + sw - 40, sy0 + 320)], fill='#38BDF8')

    # Front punch-hole camera
    draw.ellipse([cx - 10, sy0 + 28, cx + 10, sy0 + 48], fill='#000000', outline='#1E293B', width=2)
    
    # S-Pen beside the phone
    pen_x = cx + pw // 2 + 50
    draw.rounded_rectangle([pen_x - 10, y0 + 100, pen_x + 10, y0 + ph - 100], radius=8, fill='#1E293B', outline='#475569', width=2)
    draw.polygon([(pen_x - 10, y0 + ph - 100), (pen_x + 10, y0 + ph - 100), (pen_x, y0 + ph - 60)], fill='#0F172A')
    draw.rounded_rectangle([pen_x - 10, y0 + 100, pen_x + 10, y0 + 140], radius=4, fill='#94A3B8')
    return img

def render_xiaomi(slug):
    img, draw = create_studio_canvas()
    cx, cy = W // 2, H // 2 - 20
    draw_shadow(draw, cx, cy + 420, 260, 40)
    
    # Phone Body (Glossy Ceramic Black)
    pw, ph = 460, 840
    x0, y0 = cx - pw // 2, cy - ph // 2
    draw.rounded_rectangle([x0, y0, x0 + pw, y0 + ph], radius=64, fill='#18181B', outline='#27272A', width=6)
    
    # Big Leica Camera Island
    island_w, island_h = 280, 280
    ix0, iy0 = cx - island_w // 2, y0 + 80
    draw.rounded_rectangle([ix0, iy0, ix0 + island_w, iy0 + island_h], radius=48, fill='#09090B', outline='#E11D48', width=3)
    
    # 4 Lens elements
    lens_r = 38
    centers = [
        (ix0 + 75, iy0 + 75),
        (ix0 + island_w - 75, iy0 + 75),
        (ix0 + 75, iy0 + island_h - 75),
        (ix0 + island_w - 75, iy0 + island_h - 75),
    ]
    for lx, ly in centers:
        draw.ellipse([lx - lens_r, ly - lens_r, lx + lens_r, ly + lens_r], fill='#18181B', outline='#3F3F46', width=3)
        draw.ellipse([lx - lens_r + 12, ly - lens_r + 12, lx + lens_r - 12, ly + lens_r - 12], fill='#000000')
        draw.ellipse([lx - 6, ly - 6, lx + 6, ly + 6], fill='#3B82F6')
    
    # Leica red badge
    draw.rounded_rectangle([cx - 50, iy0 + island_h // 2 - 20, cx + 50, iy0 + island_h // 2 + 20], radius=8, fill='#DC2626')
    draw.text((cx, iy0 + island_h // 2), "Leica", font=FONT_BOLD_28, fill='#FFFFFF', anchor="mm")
    
    # Xiaomi logo at bottom
    draw.text((cx, y0 + ph - 80), "X I A O M I", font=FONT_BOLD_28, fill='#71717A', anchor="mm")
    return img

def render_pixel(slug):
    img, draw = create_studio_canvas()
    cx, cy = W // 2, H // 2 - 20
    draw_shadow(draw, cx, cy + 420, 260, 40)
    
    # Phone Body (Bay Blue)
    pw, ph = 460, 840
    x0, y0 = cx - pw // 2, cy - ph // 2
    draw.rounded_rectangle([x0, y0, x0 + pw, y0 + ph], radius=70, fill='#93C5FD', outline='#60A5FA', width=6)
    
    # Iconic Pixel Camera Visor Bar
    bar_y0 = y0 + 140
    bar_h = 130
    draw.rounded_rectangle([x0 - 10, bar_y0, x0 + pw + 10, bar_y0 + bar_h], radius=24, fill='#CBD5E1', outline='#94A3B8', width=4)
    
    # Pill camera cutout inside visor
    draw.rounded_rectangle([x0 + 60, bar_y0 + 25, x0 + 260, bar_y0 + bar_h - 25], radius=40, fill='#000000')
    draw.ellipse([x0 + 90, bar_y0 + 38, x0 + 146, bar_y0 + bar_h - 38], fill='#1E3A8A')
    draw.ellipse([x0 + 174, bar_y0 + 38, x0 + 230, bar_y0 + bar_h - 38], fill='#1E3A8A')
    
    # Telephoto circle lens
    draw.ellipse([x0 + 285, bar_y0 + 32, x0 + 345, bar_y0 + bar_h - 32], fill='#000000')
    draw.ellipse([x0 + 295, bar_y0 + 42, x0 + 335, bar_y0 + bar_h - 42], fill='#1E3A8A')

    # Google 'G' logo
    draw.ellipse([cx - 24, y0 + ph // 2 + 80, cx + 24, y0 + ph // 2 + 128], outline='#3B82F6', width=8)
    return img

# ================= LAPTOPS =================

def render_macbook_pro(slug):
    img, draw = create_studio_canvas()
    cx, cy = W // 2, H // 2 - 20
    draw_shadow(draw, cx, cy + 320, 480, 50)
    
    # Open Display
    dw, dh = 760, 480
    dx0, dy0 = cx - dw // 2, cy - 240
    draw.rounded_rectangle([dx0, dy0, dx0 + dw, dy0 + dh], radius=28, fill='#18181B', outline='#27272A', width=4)
    
    # Screen bezel and display
    sw, sh = dw - 28, dh - 32
    sx0, sy0 = cx - sw // 2, dy0 + 14

    def macbook_wallpaper(sdraw, w, h):
        sdraw.ellipse([40, 40, w - 40, h + 80], fill='#4338CA')
        sdraw.ellipse([140, 80, w - 80, h], fill='#D946EF')
        sdraw.ellipse([80, 140, w - 180, h + 40], fill='#06B6D4')
        # Notch inside screen
        sdraw.rounded_rectangle([w // 2 - 40, 0, w // 2 + 40, 24], radius=6, fill='#18181B')

    draw_clipped_screen(img, sx0, sy0, sw, sh, radius=16, bg_color='#09090B', draw_fn=macbook_wallpaper)
    
    # Laptop Base / Keyboard deck (Space Black aluminum)
    bw, bh = 940, 80
    bx0, by0 = cx - bw // 2, dy0 + dh
    draw.polygon([
        (bx0 + 60, by0),
        (bx0 + bw - 60, by0),
        (bx0 + bw, by0 + bh),
        (bx0, by0 + bh)
    ], fill='#27272A', outline='#3F3F46')
    
    # Front lip notch
    draw.rounded_rectangle([cx - 60, by0 + bh - 8, cx + 60, by0 + bh], radius=4, fill='#52525B')
    
    # Keyboard well
    kw, kh = 620, 44
    draw.rounded_rectangle([cx - kw // 2, by0 + 8, cx + kw // 2, by0 + 8 + kh], radius=6, fill='#09090B')
    
    # Trackpad
    tw, th = 220, 22
    draw.rounded_rectangle([cx - tw // 2, by0 + 54, cx + tw // 2, by0 + 54 + th], radius=6, fill='#18181B', outline='#3F3F46', width=2)
    return img

def render_macbook_air(slug):
    img, draw = create_studio_canvas()
    cx, cy = W // 2, H // 2 - 20
    draw_shadow(draw, cx, cy + 320, 460, 45)
    
    # Display (Midnight color)
    dw, dh = 720, 450
    dx0, dy0 = cx - dw // 2, cy - 230
    draw.rounded_rectangle([dx0, dy0, dx0 + dw, dy0 + dh], radius=24, fill='#0F172A', outline='#1E293B', width=4)
    
    # Screen
    sw, sh = dw - 24, dh - 28
    sx0, sy0 = cx - sw // 2, dy0 + 12
    draw.rounded_rectangle([sx0, sy0, sx0 + sw, sy0 + sh], radius=14, fill='#020617')
    
    # Fluid golden-blue M2 wallpaper
    draw.ellipse([sx0 + 60, sy0 + 60, sx0 + sw - 60, sy0 + sh], fill='#1E3A8A')
    draw.ellipse([sx0 + 160, sy0 + 120, sx0 + sw - 140, sy0 + sh - 40], fill='#F59E0B')
    
    # Base
    bw, bh = 880, 70
    bx0, by0 = cx - bw // 2, dy0 + dh
    draw.polygon([
        (bx0 + 50, by0),
        (bx0 + bw - 50, by0),
        (bx0 + bw, by0 + bh),
        (bx0, by0 + bh)
    ], fill='#1E293B', outline='#334155')
    
    # Trackpad
    tw, th = 200, 20
    draw.rounded_rectangle([cx - tw // 2, by0 + 46, cx + tw // 2, by0 + 46 + th], radius=6, fill='#0F172A', outline='#334155', width=2)
    return img

def render_asus_rog(slug):
    img, draw = create_studio_canvas()
    cx, cy = W // 2, H // 2 - 20
    draw_shadow(draw, cx, cy + 320, 490, 50)
    
    dw, dh = 780, 490
    dx0, dy0 = cx - dw // 2, cy - 250
    draw.rounded_rectangle([dx0, dy0, dx0 + dw, dy0 + dh], radius=16, fill='#18181B', outline='#27272A', width=4)
    
    # Screen with ROG cyber eye
    sw, sh = dw - 24, dh - 28
    sx0, sy0 = cx - sw // 2, dy0 + 12
    draw.rounded_rectangle([sx0, sy0, sx0 + sw, sy0 + sh], radius=10, fill='#09090B')
    
    # Red & Cyan gaming graphics
    draw.polygon([(cx - 140, cy - 80), (cx + 140, cy - 80), (cx + 80, cy + 40), (cx - 80, cy + 40)], fill='#DC2626')
    draw.polygon([(cx - 100, cy + 60), (cx + 100, cy + 60), (cx, cy + 130)], fill='#06B6D4')
    
    # Base with RGB keyboard glow
    bw, bh = 940, 85
    bx0, by0 = cx - bw // 2, dy0 + dh
    draw.polygon([
        (bx0 + 40, by0),
        (bx0 + bw - 40, by0),
        (bx0 + bw, by0 + bh),
        (bx0, by0 + bh)
    ], fill='#18181B', outline='#3F3F46')
    
    # RGB keyboard strip
    kw, kh = 660, 46
    draw.rounded_rectangle([cx - kw // 2, by0 + 8, cx + kw // 2, by0 + 8 + kh], radius=6, fill='#09090B', outline='#06B6D4', width=2)
    return img

def render_thinkpad(slug):
    img, draw = create_studio_canvas()
    cx, cy = W // 2, H // 2 - 20
    draw_shadow(draw, cx, cy + 320, 480, 50)
    
    dw, dh = 760, 480
    dx0, dy0 = cx - dw // 2, cy - 240
    draw.rounded_rectangle([dx0, dy0, dx0 + dw, dy0 + dh], radius=12, fill='#18181B', outline='#27272A', width=4)
    
    # Screen
    sw, sh = dw - 28, dh - 32
    sx0, sy0 = cx - sw // 2, dy0 + 14
    draw.rounded_rectangle([sx0, sy0, sx0 + sw, sy0 + sh], radius=8, fill='#0A0A0A')
    draw.text((cx, cy - 40), "ThinkPad X1 Carbon", font=FONT_BOLD_36, fill='#71717A', anchor="mm")
    
    # Base
    bw, bh = 920, 80
    bx0, by0 = cx - bw // 2, dy0 + dh
    draw.polygon([
        (bx0 + 50, by0),
        (bx0 + bw - 50, by0),
        (bx0 + bw, by0 + bh),
        (bx0, by0 + bh)
    ], fill='#18181B', outline='#27272A')
    
    # Keyboard with signature RED TrackPoint!
    kw, kh = 640, 46
    draw.rounded_rectangle([cx - kw // 2, by0 + 6, cx + kw // 2, by0 + 6 + kh], radius=6, fill='#09090B')
    draw.ellipse([cx - 7, by0 + 26, cx + 7, by0 + 40], fill='#DC2626')  # Red TrackPoint dot!
    
    # Red stripe on trackpad
    draw.line([cx - 40, by0 + 56, cx + 40, by0 + 56], fill='#DC2626', width=3)
    return img

def render_framework(slug):
    img, draw = create_studio_canvas()
    cx, cy = W // 2, H // 2 - 20
    draw_shadow(draw, cx, cy + 320, 480, 50)
    
    # Silver aluminum finish
    dw, dh = 760, 480
    dx0, dy0 = cx - dw // 2, cy - 240
    draw.rounded_rectangle([dx0, dy0, dx0 + dw, dy0 + dh], radius=16, fill='#E2E8F0', outline='#CBD5E1', width=4)
    
    # Screen
    sw, sh = dw - 24, dh - 28
    sx0, sy0 = cx - sw // 2, dy0 + 12
    draw.rounded_rectangle([sx0, sy0, sx0 + sw, sy0 + sh], radius=10, fill='#0F172A')
    draw.text((cx, cy - 40), "Framework 16", font=FONT_BOLD_48, fill='#F97316', anchor="mm")
    
    # Base with visible modular expansion cards
    bw, bh = 920, 80
    bx0, by0 = cx - bw // 2, dy0 + dh
    draw.polygon([
        (bx0 + 50, by0),
        (bx0 + bw - 50, by0),
        (bx0 + bw, by0 + bh),
        (bx0, by0 + bh)
    ], fill='#CBD5E1', outline='#94A3B8')
    
    # Modular port color accents on sides
    draw.rectangle([bx0 + 8, by0 + 44, bx0 + 36, by0 + 64], fill='#F97316')
    draw.rectangle([bx0 + bw - 36, by0 + 44, bx0 + bw - 8, by0 + 64], fill='#3B82F6')
    return img

# ================= AUDIO =================

def render_sony_headphones(slug):
    img, draw = create_studio_canvas()
    cx, cy = W // 2, H // 2 - 20
    draw_shadow(draw, cx, cy + 340, 360, 45)
    
    # Arched Headband (Matte Black leatherette)
    hb_r = 280
    draw.arc([cx - hb_r, cy - 320, cx + hb_r, cy + 140], start=180, end=0, fill='#18181B', width=42)
    draw.arc([cx - hb_r, cy - 320, cx + hb_r, cy + 140], start=180, end=0, fill='#27272A', width=32)

    # Left & Right Earcups (Luxurious tilted ovals)
    for side, sign in [('left', -1), ('right', 1)]:
        ecx = cx + sign * 240
        ecy = cy + 60
        # Swivel stem
        draw.rounded_rectangle([ecx - 14, ecy - 160, ecx + 14, ecy - 70], radius=8, fill='#27272A')
        # Outer cup
        draw.ellipse([ecx - 90, ecy - 120, ecx + 90, ecy + 120], fill='#18181B', outline='#27272A', width=4)
        # Soft plush cushion
        draw.ellipse([ecx - 72, ecy - 96, ecx + 72, ecy + 96], fill='#09090B')
        # Gold accent
        draw.rectangle([ecx - 18, ecy - 130, ecx + 18, ecy - 124], fill='#EAB308')

    return img

def render_airpods(slug):
    img, draw = create_studio_canvas()
    cx, cy = W // 2, H // 2
    draw_shadow(draw, cx, cy + 280, 320, 45)
    
    # Open AirPods Pro Case (Glossy White)
    cw, ch = 380, 280
    cx0, cy0 = cx - cw // 2, cy - 40
    draw.rounded_rectangle([cx0, cy0, cx0 + cw, cy0 + ch], radius=84, fill='#FFFFFF', outline='#E2E8F0', width=4)
    
    # Status LED
    draw.ellipse([cx - 8, cy0 + 70, cx + 8, cy0 + 86], fill='#22C55E')  # Green LED
    
    # Left & Right AirPods Pro Earbuds popping out
    for side, sign in [('left', -1), ('right', 1)]:
        ebx = cx + sign * 100
        eby = cy0 - 80
        # Angled head
        draw.ellipse([ebx - 50, eby - 40, ebx + 50, eby + 40], fill='#FFFFFF', outline='#E2E8F0', width=4)
        # Black acoustic vent
        draw.ellipse([ebx - 20, eby - 14, ebx + 20, eby + 14], fill='#18181B')
        # Silicone tip
        tip_x1 = min(ebx + sign * 30, ebx + sign * 70)
        tip_x2 = max(ebx + sign * 30, ebx + sign * 70)
        draw.ellipse([tip_x1, eby - 20, tip_x2, eby + 20], fill='#F1F5F9')
        # Stem
        draw.rounded_rectangle([ebx - 14, eby + 20, ebx + 14, eby + 140], radius=10, fill='#FFFFFF', outline='#E2E8F0', width=2)
        # Silver charging contact
        draw.rounded_rectangle([ebx - 14, eby + 130, ebx + 14, eby + 140], radius=4, fill='#CBD5E1')

    return img

def render_marshall(slug):
    img, draw = create_studio_canvas()
    cx, cy = W // 2, H // 2 - 20
    draw_shadow(draw, cx, cy + 340, 360, 45)
    
    # Textured Headband
    hb_r = 280
    draw.arc([cx - hb_r, cy - 320, cx + hb_r, cy + 140], start=180, end=0, fill='#1C1917', width=54)
    
    # Vintage Square Earcups
    for side, sign in [('left', -1), ('right', 1)]:
        ecx = cx + sign * 240
        ecy = cy + 60
        # Hinges
        draw.rounded_rectangle([ecx - 16, ecy - 160, ecx + 16, ecy - 80], radius=8, fill='#44403C')
        # Vinyl textured square cup
        draw.rounded_rectangle([ecx - 90, ecy - 100, ecx + 90, ecy + 100], radius=32, fill='#1C1917', outline='#292524', width=6)
        # Cushion
        draw.rounded_rectangle([ecx - 70, ecy - 80, ecx + 70, ecy + 80], radius=24, fill='#0C0A09')
        # Gold knob on right
        if sign == 1:
            draw.ellipse([ecx + 60, ecy + 60, ecx + 94, ecy + 94], fill='#CA8A04', outline='#A16207', width=2)

    return img

def render_bose(slug):
    img, draw = create_studio_canvas()
    cx, cy = W // 2, H // 2 - 20
    draw_shadow(draw, cx, cy + 340, 360, 45)
    
    # White Smoke Headband
    hb_r = 280
    draw.arc([cx - hb_r, cy - 320, cx + hb_r, cy + 140], start=180, end=0, fill='#E2E8F0', width=44)
    
    for side, sign in [('left', -1), ('right', 1)]:
        ecx = cx + sign * 240
        ecy = cy + 60
        # Polished aluminum yoke
        draw.rounded_rectangle([ecx - 14, ecy - 170, ecx + 14, ecy - 70], radius=8, fill='#CBD5E1')
        # Soft luxury cup
        draw.ellipse([ecx - 88, ecy - 116, ecx + 88, ecy + 116], fill='#F1F5F9', outline='#E2E8F0', width=4)
        draw.ellipse([ecx - 70, ecy - 92, ecx + 70, ecy + 92], fill='#E2E8F0')

    return img

def render_sennheiser_orpheus(slug):
    img, draw = create_studio_canvas()
    cx, cy = W // 2, H // 2
    draw_shadow(draw, cx, cy + 340, 460, 50)
    
    # Carrara Marble Base
    mw, mh = 680, 180
    mx0, my0 = cx - mw // 2, cy + 120
    draw.rounded_rectangle([mx0, my0, mx0 + mw, my0 + mh], radius=16, fill='#F1F5F9', outline='#CBD5E1', width=4)
    # Marble veins
    draw.line([mx0 + 80, my0 + 20, mx0 + 260, my0 + 140], fill='#E2E8F0', width=4)
    draw.line([mx0 + 380, my0 + 30, mx0 + 580, my0 + 120], fill='#E2E8F0', width=4)

    # 4 Glowing Vacuum Glass Tubes!
    for i in range(4):
        tx = cx - 210 + i * 140
        ty = my0 - 110
        # Amber vacuum glow
        draw.ellipse([tx - 40, ty - 20, tx + 40, ty + 100], fill='#FDE68A')
        # Glass tube
        draw.rounded_rectangle([tx - 30, ty - 30, tx + 30, ty + 90], radius=24, outline='#D97706', width=3)
        # Glowing filament
        draw.line([tx, ty - 10, tx, ty + 70], fill='#EA580C', width=4)

    # Electrostatic Headphones Resting on Stand
    draw.arc([cx - 180, cy - 360, cx + 180, cy - 60], start=180, end=0, fill='#475569', width=28)
    draw.ellipse([cx - 200, cy - 140, cx - 110, cy + 20], fill='#0F172A', outline='#94A3B8', width=4)
    draw.ellipse([cx + 110, cy - 140, cx + 200, cy + 20], fill='#0F172A', outline='#94A3B8', width=4)
    return img

# ================= TABLETS =================

def render_ipad_pro(slug):
    img, draw = create_studio_canvas()
    cx, cy = W // 2, H // 2 - 20
    draw_shadow(draw, cx, cy + 420, 360, 45)
    
    # Ultra-thin Space Black body
    tw, th = 640, 840
    tx0, ty0 = cx - tw // 2, cy - th // 2
    draw.rounded_rectangle([tx0, ty0, tx0 + tw, ty0 + th], radius=44, fill='#18181B', outline='#27272A', width=4)
    
    # Tandem OLED screen
    sw, sh = tw - 24, th - 24
    sx0, sy0 = cx - sw // 2, cy - sh // 2
    draw.rounded_rectangle([sx0, sy0, sx0 + sw, sy0 + sh], radius=36, fill='#09090B')
    
    # Fluid Apple OLED wallpaper
    draw.ellipse([sx0 + 80, sy0 + 100, sx0 + sw - 60, sy0 + sh - 100], fill='#4F46E5')
    draw.ellipse([sx0 + 160, sy0 + 260, sx0 + sw + 40, sy0 + sh], fill='#EC4899')
    draw.ellipse([sx0 + 40, sy0 + 420, sx0 + sw - 140, sy0 + sh - 80], fill='#06B6D4')

    # Apple Pencil magnetically attached on top
    draw.rounded_rectangle([cx - 220, ty0 - 18, cx + 220, ty0 - 4], radius=6, fill='#FFFFFF', outline='#E2E8F0', width=2)
    draw.polygon([(cx + 220, ty0 - 18), (cx + 220, ty0 - 4), (cx + 236, ty0 - 11)], fill='#F1F5F9')
    return img

def render_ipad_air(slug):
    img, draw = create_studio_canvas()
    cx, cy = W // 2, H // 2 - 20
    draw_shadow(draw, cx, cy + 420, 350, 45)
    
    # Blue aluminum finish
    tw, th = 620, 820
    tx0, ty0 = cx - tw // 2, cy - th // 2
    draw.rounded_rectangle([tx0, ty0, tx0 + tw, ty0 + th], radius=40, fill='#93C5FD', outline='#60A5FA', width=4)
    
    # Screen
    sw, sh = tw - 24, th - 24
    sx0, sy0 = cx - sw // 2, cy - sh // 2
    draw.rounded_rectangle([sx0, sy0, sx0 + sw, sy0 + sh], radius=32, fill='#0F172A')
    draw.ellipse([sx0 + 60, sy0 + 80, sx0 + sw - 60, sy0 + sh - 80], fill='#2563EB')
    draw.ellipse([sx0 + 140, sy0 + 200, sx0 + sw - 40, sy0 + sh], fill='#38BDF8')
    return img

def render_samsung_tab(slug):
    img, draw = create_studio_canvas()
    cx, cy = W // 2, H // 2 - 20
    draw_shadow(draw, cx, cy + 340, 480, 45)
    
    # Widescreen 16:10 format
    tw, th = 860, 580
    tx0, ty0 = cx - tw // 2, cy - th // 2
    draw.rounded_rectangle([tx0, ty0, tx0 + tw, ty0 + th], radius=28, fill='#1E293B', outline='#334155', width=4)
    
    sw, sh = tw - 24, th - 24
    sx0, sy0 = cx - sw // 2, cy - sh // 2
    draw.rounded_rectangle([sx0, sy0, sx0 + sw, sy0 + sh], radius=20, fill='#020617')
    draw.ellipse([sx0 + 100, sy0 + 40, sx0 + sw - 100, sy0 + sh + 40], fill='#7C3AED')
    draw.ellipse([sx0 + 260, sy0 + 120, sx0 + sw - 60, sy0 + sh - 40], fill='#3B82F6')
    return img

def render_xiaomi_pad(slug):
    img, draw = create_studio_canvas()
    cx, cy = W // 2, H // 2 - 20
    draw_shadow(draw, cx, cy + 420, 350, 45)
    
    tw, th = 620, 820
    tx0, ty0 = cx - tw // 2, cy - th // 2
    draw.rounded_rectangle([tx0, ty0, tx0 + tw, ty0 + th], radius=36, fill='#CBD5E1', outline='#94A3B8', width=4)
    
    sw, sh = tw - 24, th - 24
    sx0, sy0 = cx - sw // 2, cy - sh // 2
    draw.rounded_rectangle([sx0, sy0, sx0 + sw, sy0 + sh], radius=28, fill='#09090B')
    draw.ellipse([sx0 + 80, sy0 + 80, sx0 + sw - 80, sy0 + sh - 80], fill='#059669')
    draw.ellipse([sx0 + 140, sy0 + 200, sx0 + sw - 40, sy0 + sh], fill='#10B981')
    return img

def render_remarkable(slug):
    img, draw = create_studio_canvas()
    cx, cy = W // 2, H // 2 - 20
    draw_shadow(draw, cx, cy + 420, 360, 45)
    
    # reMarkable 2 (Slate gray with wide left spine bezel)
    tw, th = 620, 840
    tx0, ty0 = cx - tw // 2, cy - th // 2
    draw.rounded_rectangle([tx0, ty0, tx0 + tw, ty0 + th], radius=16, fill='#334155', outline='#1E293B', width=4)
    
    # Left spine accent
    draw.rectangle([tx0, ty0, tx0 + 60, ty0 + th], fill='#1E293B')
    
    # CANVAS paper screen (Off-white paper look)
    sx0, sy0 = tx0 + 68, ty0 + 16
    sw, sh = tw - 84, th - 32
    draw.rectangle([sx0, sy0, sx0 + sw, sy0 + sh], fill='#F8FAFC')
    
    # Simulated handwritten sketch & notes on e-ink
    for y in range(sy0 + 80, sy0 + 400, 40):
        draw.line([sx0 + 40, y, sx0 + sw - 60, y], fill='#94A3B8', width=2)
    # Pencil sketch
    draw.ellipse([sx0 + 140, sy0 + 460, sx0 + 340, sy0 + 660], outline='#0F172A', width=4)
    draw.line([sx0 + 100, sy0 + 600, sx0 + 380, sy0 + 600], fill='#0F172A', width=4)
    return img

# ================= SMARTHOME =================

def render_yandex_station(slug):
    img, draw = create_studio_canvas()
    cx, cy = W // 2, H // 2
    draw_shadow(draw, cx, cy + 360, 360, 45)
    
    # Speaker cylindrical fabric base
    bw, bh = 320, 260
    bx0, by0 = cx - bw // 2, cy + 80
    draw.rounded_rectangle([bx0, by0, bx0 + bw, by0 + bh], radius=40, fill='#1F2937', outline='#111827', width=4)
    
    # Alice Purple glowing LED ring!
    draw.ellipse([cx - 120, by0 + 20, cx + 120, by0 + 60], fill='#9333EA', outline='#C084FC', width=4)
    
    # 10.5" Touchscreen mounted on swivel arm
    sw, sh = 600, 380
    sx0, sy0 = cx - sw // 2, cy - 220
    draw.rounded_rectangle([sx0, sy0, sx0 + sw, sy0 + sh], radius=24, fill='#111827', outline='#374151', width=6)
    draw.rounded_rectangle([sx0 + 12, sy0 + 12, sx0 + sw - 12, sy0 + sh - 12], radius=16, fill='#0F172A')
    
    # Display UI: Clock and Alice Voice Soundwave graphic
    draw.text((cx, sy0 + 110), "12:30", font=FONT_BOLD_64, fill='#FFFFFF', anchor="mm")
    
    # Alice audio wave bars (purple/cyan)
    wave_colors = ['#C084FC', '#9333EA', '#7C3AED', '#A855F7', '#C084FC', '#E879F9', '#38BDF8', '#818CF8']
    wave_heights = [30, 60, 90, 110, 80, 50, 40, 25]
    bar_w = 12
    start_x = cx - (len(wave_heights) * 22) // 2
    for idx, h_val in enumerate(wave_heights):
        bx = start_x + idx * 22
        by = sy0 + 230
        draw.rounded_rectangle([bx, by - h_val // 2, bx + bar_w, by + h_val // 2], radius=6, fill=wave_colors[idx % len(wave_colors)])
    
    return img

def render_roborock(slug):
    img, draw = create_studio_canvas()
    cx, cy = W // 2, H // 2
    draw_shadow(draw, cx, cy + 340, 380, 50)
    
    # White Docking Station in background
    dw, dh = 460, 340
    dx0, dy0 = cx - dw // 2, cy - 240
    draw.rounded_rectangle([dx0, dy0, dx0 + dw, dy0 + dh], radius=32, fill='#F8FAFC', outline='#CBD5E1', width=4)
    draw.rounded_rectangle([dx0 + 40, dy0 + 40, dx0 + 200, dy0 + 200], radius=16, fill='#E2E8F0')  # Clean water tank
    draw.rounded_rectangle([dx0 + dw - 200, dy0 + 40, dx0 + dw - 40, dy0 + 200], radius=16, fill='#64748B')  # Dirty water tank
    
    # White Circular Robot Vacuum disc
    rw = 480
    rx0, ry0 = cx - rw // 2, cy + 40
    draw.ellipse([rx0, ry0, rx0 + rw, ry0 + 320], fill='#FFFFFF', outline='#CBD5E1', width=6)
    
    # LiDAR spinning turret with orange accent
    draw.ellipse([cx - 50, ry0 + 80, cx + 50, ry0 + 180], fill='#FFFFFF', outline='#F97316', width=6)
    draw.ellipse([cx - 30, ry0 + 100, cx + 30, ry0 + 160], fill='#EA580C')
    return img

def render_apple_tv(slug):
    img, draw = create_studio_canvas()
    cx, cy = W // 2 - 80, H // 2
    draw_shadow(draw, cx, cy + 220, 280, 40)
    
    # Apple TV 4K puck (Matte Black square rounded block)
    pw, ph = 380, 340
    px0, py0 = cx - pw // 2, cy - ph // 2
    draw.rounded_rectangle([px0, py0, px0 + pw, py0 + ph], radius=56, fill='#18181B', outline='#27272A', width=6)
    draw.ellipse([cx - 40, cy - 30, cx + 40, cy + 30], fill='#27272A')
    draw.text((cx, cy + 30), "tv", font=FONT_BOLD_48, fill='#71717A', anchor="mm")
    
    # Siri Remote on the right side
    rcx = cx + 320
    draw_shadow(draw, rcx, cy + 260, 100, 30)
    rw, rh = 130, 480
    rx0, ry0 = rcx - rw // 2, cy - rh // 2
    draw.rounded_rectangle([rx0, ry0, rx0 + rw, ry0 + rh], radius=32, fill='#E2E8F0', outline='#CBD5E1', width=4)
    # Black clickpad
    draw.ellipse([rcx - 42, ry0 + 36, rcx + 42, ry0 + 120], fill='#18181B')
    draw.ellipse([rcx - 16, ry0 + 62, rcx + 16, ry0 + 94], fill='#3F3F46')
    return img

def render_smartmi(slug):
    img, draw = create_studio_canvas()
    cx, cy = W // 2, H // 2
    draw_shadow(draw, cx, cy + 360, 260, 40)
    
    # Minimalist White Tower
    tw, th = 340, 680
    tx0, ty0 = cx - tw // 2, cy - th // 2
    draw.rounded_rectangle([tx0, ty0, tx0 + tw, ty0 + th], radius=44, fill='#FFFFFF', outline='#E2E8F0', width=4)
    
    # Top air outlet grill
    draw.ellipse([cx - 130, ty0 + 20, cx + 130, ty0 + 80], outline='#CBD5E1', width=6)
    
    # LED Display showing humidity
    draw.ellipse([cx - 50, ty0 + 130, cx + 50, ty0 + 230], fill='#0F172A')
    draw.text((cx, ty0 + 180), "48%", font=FONT_BOLD_48, fill='#38BDF8', anchor="mm")
    
    # Water level window slit
    draw.rounded_rectangle([cx - 6, ty0 + 320, cx + 6, ty0 + 580], radius=4, fill='#93C5FD')
    return img

def render_cyberdog(slug):
    img, draw = create_studio_canvas()
    cx, cy = W // 2, H // 2 - 20
    draw_shadow(draw, cx, cy + 340, 400, 45)
    
    # Cybernetic Quadruped Body (Titanium & Carbon Black)
    bw, bh = 540, 260
    bx0, by0 = cx - bw // 2, cy - 80
    draw.rounded_rectangle([bx0, by0, bx0 + bw, by0 + bh], radius=40, fill='#18181B', outline='#3F3F46', width=6)
    
    # Head module with visor sensor
    hx0, hy0 = bx0 + bw - 120, by0 - 100
    draw.rounded_rectangle([hx0, hy0, hx0 + 180, hy0 + 140], radius=24, fill='#09090B', outline='#06B6D4', width=4)
    # Cyan LED Visor eyes
    draw.rounded_rectangle([hx0 + 30, hy0 + 40, hx0 + 150, hy0 + 70], radius=8, fill='#06B6D4')
    
    # 4 Articulated robotic legs
    leg_coords = [
        (bx0 + 60, by0 + bh),
        (bx0 + 140, by0 + bh),
        (bx0 + bw - 140, by0 + bh),
        (bx0 + bw - 60, by0 + bh),
    ]
    for lx, ly in leg_coords:
        draw.line([lx, ly, lx - 20, ly + 140], fill='#3F3F46', width=18)
        draw.line([lx - 20, ly + 140, lx + 10, ly + 280], fill='#18181B', width=14)
        draw.ellipse([lx - 4, ly + 270, lx + 24, ly + 296], fill='#E11D48')  # Silicone foot pad
    return img

# Dispatch mapping
RENDERERS = {
    'iphone-15-pro-max': render_iphone,
    'nothing-phone-2': render_nothing_phone,
    'samsung-s24-ultra': render_samsung,
    'xiaomi-14-pro': render_xiaomi,
    'google-pixel-8-pro': render_pixel,
    
    'macbook-pro-16-m3': render_macbook_pro,
    'macbook-air-m2': render_macbook_air,
    'asus-rog-zephyrus-g16': render_asus_rog,
    'lenovo-thinkpad-x1': render_thinkpad,
    'framework-laptop-16': render_framework,
    
    'sony-wh1000xm5': render_sony_headphones,
    'airpods-pro-2-usbc': render_airpods,
    'marshall-major-iv': render_marshall,
    'bose-qc-ultra': render_bose,
    'sennheiser-he-1': render_sennheiser_orpheus,
    
    'ipad-pro-13-m4': render_ipad_pro,
    'ipad-air-11-m2': render_ipad_air,
    'samsung-tab-s9-ultra': render_samsung_tab,
    'xiaomi-pad-6': render_xiaomi_pad,
    'remarkable-2': render_remarkable,
    
    'yandex-station-duo-max': render_yandex_station,
    'roborock-s8-pro-ultra': render_roborock,
    'apple-tv-4k-128gb': render_apple_tv,
    'smartmi-humidifier-3': render_smartmi,
    'xiaomi-cyberdog-2': render_cyberdog,
}

def main():
    print("Generating 25 studio renders with 2x supersampling...")
    for slug, render_fn in RENDERERS.items():
        img_1200 = render_fn(slug)
        # Downscale with high-quality anti-aliasing
        img_600 = img_1200.resize((600, 600), Image.Resampling.LANCZOS)
        out_path = os.path.join(MEDIA_DIR, f"{slug}.webp")
        img_600.save(out_path, format='WEBP', quality=92)
        print(f"Generated: {out_path}")
    print("All 25 renders successfully generated!")

if __name__ == '__main__':
    main()
