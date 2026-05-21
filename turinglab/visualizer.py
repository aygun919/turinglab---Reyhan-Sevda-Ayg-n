"""
TuringLab - Turing Makinesi Görselleştirici
Bonus D: Her adım için PNG üretir, GIF oluşturur
"""

from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from turinglab.tm_engine import RunResult, Configuration


# Renkler
BG_COLOR      = (245, 245, 245)
CELL_COLOR    = (255, 255, 255)
HEAD_COLOR    = (255, 80, 80)
BORDER_COLOR  = (100, 100, 100)
TEXT_COLOR    = (30, 30, 30)
STATE_COLOR   = (80, 130, 255)
ACCEPT_COLOR  = (60, 200, 100)
LABEL_COLOR   = (120, 120, 120)


def _draw_frame(config: Configuration, step: int,
                total_steps: int, accept_states: set[str]) -> Image.Image:
    """
    Tek bir konfigürasyon için PNG karesi üretir.

    Args:
        config: O adımdaki TM konfigürasyonu
        step: Adım numarası
        total_steps: Toplam adım sayısı
        accept_states: Kabul durumları kümesi

    Returns:
        PIL Image nesnesi
    """
    width, height = 800, 200
    img = Image.new("RGB", (width, height), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Başlık
    draw.text((10, 10), f"TuringLab — Adım {step}/{total_steps}",
              fill=LABEL_COLOR)

    # Durum kutusu
    state_color = ACCEPT_COLOR if config.state in accept_states else STATE_COLOR
    draw.rounded_rectangle([10, 35, 160, 80], radius=8, fill=state_color)
    draw.text((20, 50), f"Durum: {config.state}", fill=(255, 255, 255))

    # Şerit hücreleri
    tape = config.tape
    head = config.head_position

    # Şeridi parse et
    cells = []
    i = 0
    raw = tape
    # Köşeli parantezleri kaldırarak hücreleri ayıkla
    import re
    parts = re.findall(r'\[(.)\]|(.)', raw)
    pos = 0
    head_idx = 0
    parsed = []
    for bracket, plain in parts:
        if bracket:
            parsed.append((bracket, True))
            head_idx = pos
        elif plain and plain not in '[]':
            parsed.append((plain, False))
        pos += 1

    # Hücreleri çiz
    cell_size = 45
    start_x = 180
    start_y = 40
    max_cells = 12

    # Görüntülenecek hücre aralığı
    visible_start = max(0, head_idx - max_cells // 2)
    visible_end = min(len(parsed), visible_start + max_cells)
    visible = parsed[visible_start:visible_end]

    for idx, (char, is_head) in enumerate(visible):
        x = start_x + idx * cell_size
        y = start_y
        color = HEAD_COLOR if is_head else CELL_COLOR
        draw.rectangle([x, y, x + cell_size - 2, y + cell_size - 2],
                       fill=color, outline=BORDER_COLOR, width=2)
        draw.text((x + 14, y + 12), char, fill=TEXT_COLOR)

    # Kafa oku
    if visible:
        arrow_x = start_x + min(head_idx - visible_start,
                                 len(visible) - 1) * cell_size + 20
        draw.text((arrow_x - 5, start_y + cell_size + 5), "▲",
                  fill=HEAD_COLOR)

    # Alt bilgi
    draw.text((10, 160),
              f"Şerit: {tape}",
              fill=LABEL_COLOR)
    draw.text((10, 180),
              f"Kafa pozisyonu: {head}",
              fill=LABEL_COLOR)

    return img


def visualize(
    result: RunResult,
    output_dir: str | Path = "docs/images",
    accept_states: set[str] | None = None,
    max_frames: int = 20,
    make_gif: bool = True,
) -> list[Path]:
    """
    TM çalışmasını görselleştirir, PNG kareleri ve GIF üretir.

    Args:
        result: SingleTapeTM.run() sonucu
        output_dir: PNG dosyalarının kaydedileceği klasör
        accept_states: Kabul durumları (yeşil renk için)
        max_frames: Maksimum kare sayısı
        make_gif: True ise GIF de üretir

    Returns:
        Oluşturulan dosyaların yolları
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if accept_states is None:
        accept_states = set()

    history = result.history[:max_frames]
    total = len(history) - 1
    frames = []
    paths = []

    for step, config in enumerate(history):
        img = _draw_frame(config, step, total, accept_states)
        path = output_dir / f"step_{step:03d}.png"
        img.save(path)
        paths.append(path)
        frames.append(img)
        print(f"  PNG kaydedildi: {path}")

    # GIF üret
    if make_gif and frames:
        gif_path = output_dir / "simulation.gif"
        frames[0].save(
            gif_path,
            save_all=True,
            append_images=frames[1:],
            duration=600,
            loop=0,
        )
        paths.append(gif_path)
        print(f"  GIF kaydedildi: {gif_path}")

    return paths


__all__ = ["visualize"]