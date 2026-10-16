#!/usr/bin/env python3
"""构建发布包 dist/ —— 干净、体积小、可直接上传或部署。

做了三件事：
  1. 只复制站点真正用到的文件（跳过未引用的旧图、.workbuddy、tools、README 等）
  2. 压缩在用的 JPEG（质量 82 + 渐进式；尺寸不动，观感无损）
  3. 生成 .nojekyll（GitHub Pages 默认会跑 Jekyll，会忽略下划线开头的文件）

用法（依赖 Pillow）：
    python3 -m venv .venv && .venv/bin/pip install pillow
    .venv/bin/python tools/build_dist.py          # 输出到 dist/
    .venv/bin/python tools/build_dist.py --out 目录名

⚠️ 只写 dist/，不改动任何源文件。原始图片保持原样，随时可重建。
"""

import argparse
import os
import re
import shutil
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("需要 Pillow：python3 -m venv .venv && .venv/bin/pip install pillow")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUALITY = 82          # 82 是画质/体积的甜点；想更省改 78，想更保真改 88
MAX_EDGE = 1200       # 超过则等比缩到这个边长（现有图片都 ≤1200，实际不触发）

def read_used_assets():
    """从 index.html 里扫出真实引用的资源，避免误把旧素材打进包。

    同时匹配 src / href / content（后者用于 og:image、twitter:image 这类 meta）。
    """
    html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    return set(re.findall(r'(?:src|href|content)="((?:assets|fonts)/[^"]+)"', html))


def copy_dir(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def optimize_jpeg(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im = Image.open(src)
    im = im.convert("RGB")
    if max(im.size) > MAX_EDGE:
        r = MAX_EDGE / max(im.size)
        im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    im.save(dst, "JPEG", quality=QUALITY, optimize=True, progressive=True)
    return os.path.getsize(src), os.path.getsize(dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="dist")
    args = ap.parse_args()

    out = os.path.abspath(os.path.join(ROOT, args.out))
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out)

    # 1) HTML
    shutil.copy2(os.path.join(ROOT, "index.html"), os.path.join(out, "index.html"))

    # 2) 字体 / CSS / JS 整目录复制（字体是分片 woff2，浏览器按需下载，不做处理）
    for d in ("assets/fonts", "assets/css", "assets/js"):
        copy_dir(os.path.join(ROOT, d), os.path.join(out, d))

    # 3) 图片：只打进被引用的，并压缩
    img_out = os.path.join(out, "assets", "img")
    os.makedirs(img_out, exist_ok=True)
    used = read_used_assets()
    total_before = total_after = 0

    for name in sorted(os.listdir(os.path.join(ROOT, "assets", "img"))):
        src = os.path.join(ROOT, "assets", "img", name)
        if not os.path.isfile(src):
            continue                                   # 跳过 dither/ 等子目录
        if not any(f"assets/img/{name}" in u for u in used):
            print(f"  跳过未引用：{name}")
            continue
        dst = os.path.join(img_out, name)
        before = os.path.getsize(src)
        if name.lower().endswith((".jpg", ".jpeg")):
            _, after = optimize_jpeg(src, dst)         # 照片压一压
        else:
            shutil.copy2(src, dst)                     # png 等原样复制
            after = before
        total_before += before
        total_after += after
        if before != after:
            print(f"  {name:<16} {before/1024:7.1f} KB → {after/1024:7.1f} KB "
                  f"({(1 - after/before)*100:.0f}% ↓)")
        else:
            print(f"  {name:<16} {before/1024:7.1f} KB（原样）")

    # 4) GitHub Pages 需要：禁用 Jekyll，否则下划线开头的文件会被吞
    with open(os.path.join(out, ".nojekyll"), "w") as f:
        f.write("")

    # 5) 体积汇总
    def size(p):
        t = 0
        for r, _, fs in os.walk(p):
            for x in fs:
                t += os.path.getsize(os.path.join(r, x))
        return t

    print(f"\n图片合计 {total_before/1024:.0f} KB → {total_after/1024:.0f} KB")
    print(f"发布包总计 {size(out)/1024/1024:.2f} MB  →  {out}")
    print("（字体看着大，但它是分片子集，浏览器只下载页面实际用到的几片）")


if __name__ == "__main__":
    main()
