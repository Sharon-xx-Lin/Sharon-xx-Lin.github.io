#!/usr/bin/env python3
"""【已弃用 · v1.5 起页面不再引用】预生成静态 1-bit 抖动图（assets/img/dither/*.png）。

背景：v1.4.1 曾用它做「canvas 读不到像素时的保真降级」（当时的调用方是
     assets/js/main.js 的 useFallback()）。v1.4.2 发现抖动颗粒过细（位图 225px
     放大到 335px 显示 → ≈1.5 CSS px 网眼）观感反而更糊，于是撤销；
     v1.5 把摄影区统一为「高对比黑白 + 网点」（纯 CSS），本脚本与其产物已无人引用。

留作参考：若将来想重新试 1-bit 抖动（比如把 SCALE 调小、让位图尺寸接近显示宽，
     颗粒就会粗而锐利），这套 Bayer 算法可直接复用。

⚠️ 若要重新启用，需要自己把结果接回页面（页面侧已无任何 dither 逻辑）。

算法：
     w = floor(naturalWidth / scale), h = floor(naturalHeight / scale)
     gray = 0.299R + 0.587G + 0.114B
     gray = gray * 0.92 + 6
     on   = gray > (BAYER[y & 7][x & 7] + 0.5) / 64 * 255

用法（依赖 Pillow）：
     python3 -m venv .venv && .venv/bin/pip install pillow
     .venv/bin/python tools/gen_dither.py
"""
import os
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("需要 Pillow：python3 -m venv .venv && .venv/bin/pip install pillow")

BAYER = [
    [0, 32, 8, 40, 2, 34, 10, 42],
    [48, 16, 56, 24, 50, 18, 58, 26],
    [12, 44, 4, 36, 14, 46, 6, 38],
    [60, 28, 52, 20, 62, 30, 54, 22],
    [3, 35, 11, 43, 1, 33, 9, 41],
    [51, 19, 59, 27, 49, 17, 57, 25],
    [15, 47, 7, 39, 13, 45, 5, 37],
    [63, 31, 55, 23, 61, 29, 53, 21],
]

# 需要生成抖动图的照片
NAMES = ["gugong", "datong", "haining", "tulip", "lily", "lantern"]
SCALE = 4   # 除的基数：值越小位图越大、颗粒越细（v1.4.2 的教训：位图应≈显示宽度/期望颗粒px）

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "img")
DST = os.path.join(SRC, "dither")


def dither(path_in: str, path_out: str) -> tuple:
    im = Image.open(path_in).convert("RGB")
    w = max(1, im.width // SCALE)
    h = max(1, im.height // SCALE)
    small = im.resize((w, h), Image.LANCZOS)
    px = small.load()
    out = Image.new("1", (w, h), 0)
    o = out.load()
    for y in range(h):
        row = BAYER[y & 7]
        for x in range(w):
            r, g, b = px[x, y]
            gray = 0.299 * r + 0.587 * g + 0.114 * b
            gray = gray * 0.92 + 6.0
            if gray > (row[x & 7] + 0.5) / 64 * 255:
                o[x, y] = 255
    out.save(path_out, optimize=True)
    return (im.width, im.height, w, h)


def main() -> None:
    os.makedirs(DST, exist_ok=True)
    for name in NAMES:
        src = os.path.join(SRC, name + ".jpg")
        dst = os.path.join(DST, name + ".png")
        if not os.path.exists(src):
            print("跳过（找不到源图）: " + src)
            continue
        sw, sh, w, h = dither(src, dst)
        print("%-9s %4dx%-5d -> %3dx%-5d  %6.1f KB" % (name, sw, sh, w, h, os.path.getsize(dst) / 1024))
    print("完成 → " + DST)


if __name__ == "__main__":
    main()
