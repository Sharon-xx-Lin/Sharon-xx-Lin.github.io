#!/usr/bin/env python3
"""生成社交分享封面 assets/img/og-cover.png（1200×630）。

链接发到微信 / 领英 / Twitter 时会显示这张卡片，而不是一条裸链接。
风格跟站点一致：黑底、白字、像素切角边框 + 淡网点。

用法（依赖 Pillow）：
    .venv/bin/python tools/gen_og.py
改文案就改下面的 TEXT，重新跑一次即可。
"""

import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "img", "og-cover.png")

W, H = 1200, 630
BG = (0, 0, 0)
FG = (255, 255, 255)
DIM = (150, 150, 150)

TEXT = {
    "eyebrow": "PORTFOLIO · 2026 · HANGZHOU",
    "name": "林晓煊",
    "en": "SHARON LIN",
    "role": "AI 产品 × 商业化产品",
    "edu": "浙江大学金融硕士在读",
}

# 候选中文字体，取第一个存在的
CJK_CANDIDATES = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
]
LATIN_CANDIDATES = [
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/Avenir Next.ttc",
    "/Library/Fonts/Arial.ttf",
]


def font(paths, size):
    for p in paths:
        if os.path.exists(p):
            for idx in (0, 1, 2):
                try:
                    return ImageFont.truetype(p, size, index=idx)
                except Exception:
                    continue
    return ImageFont.load_default()


def main():
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)

    f_eyebrow = font(LATIN_CANDIDATES, 26)
    f_name = font(CJK_CANDIDATES, 112)
    f_en = font(LATIN_CANDIDATES, 40)
    f_role = font(CJK_CANDIDATES, 38)
    f_edu = font(CJK_CANDIDATES, 30)

    # 淡网点底纹（与站点首屏同款）
    for y in range(0, H, 8):
        for x in range(0, W, 8):
            d.point((x, y), fill=(14, 14, 14))

    # 像素切角边框：先画满框，再切掉四角
    t, c = 4, 30
    d.rectangle([0, 0, W - 1, H - 1], outline=FG, width=t)
    for (cx, cy) in ((0, 0), (W, 0), (0, H), (W, H)):
        d.rectangle([min(cx, cx - c) if cx else 0,
                     min(cy, cy - c) if cy else 0,
                     max(cx, cx + c - 1) if cx else c - 1,
                     max(cy, cy + c - 1) if cy else c - 1], fill=BG)
    # 补上切角斜边
    d.polygon([(0, c), (c, 0), (0, 0)], fill=BG)
    d.polygon([(W - c, 0), (W - 1, c), (W - 1, 0)], fill=BG)
    d.polygon([(0, H - c), (c, H - 1), (0, H - 1)], fill=BG)
    d.polygon([(W - c, H - 1), (W - 1, H - c), (W - 1, H - 1)], fill=BG)

    x = 96
    d.text((x, 120), TEXT["eyebrow"], font=f_eyebrow, fill=DIM)
    d.text((x, 186), TEXT["name"], font=f_name, fill=FG)
    d.text((x + 4, 330), TEXT["en"], font=f_en, fill=FG, spacing=8)
    d.text((x, 412), TEXT["role"], font=f_role, fill=DIM)
    d.text((x, 468), TEXT["edu"], font=f_edu, fill=DIM)

    # 右下角像素方块装饰（呼应站点 logo 的 ■）：实心、由小到大
    for i, s in enumerate((10, 16, 24)):
        px = W - 96 - (2 - i) * 34 - s
        py = H - 92 - s
        d.rectangle([px, py, px + s - 1, py + s - 1], fill=FG)

    im.save(OUT, "PNG", optimize=True)
    print(f"已生成 {OUT}  ({os.path.getsize(OUT)/1024:.1f} KB)")


if __name__ == "__main__":
    main()
