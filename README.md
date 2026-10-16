# 林晓煊 · 个人网站

定位：求职向个人展示页。风格参考 [careers.kimi.com](https://careers.kimi.com/)（黑白像素 / 高对比黑白摄影）。

**当前版本：v1.5.1（深浅双主题 + 中文）**。英文版架构已预留，尚未开放。

> **发布上线 + 上线后怎么改内容 → 见 [DEPLOY.md](DEPLOY.md)**（含临时预览链接、GitHub Pages 步骤、自定义域名、日常更新流程）。

## v1.5.1：发布准备（分享卡片 + 一处显示 bug）

- **修 reveal 底部盲区**：入场判据原是 `rect.top < innerHeight * 0.92`，等于要求元素顶部比视口底边再往上 8%，于是**停在视口最底部那 8% 里的元素永不显示** —— 矮窗口下首屏末尾一行字不出现，像是内容缺失。改为 `rect.top < innerHeight`（进入视口即显示）。
- **社交分享卡片**：新增 `og:` / `twitter:` 系列 meta + `Person` 结构化数据，配 `assets/img/og-cover.png`（1200×630 像素风封面，由 `tools/gen_og.py` 生成）。链接发到微信 / 领英时显示卡片而不是裸链接。
  ⚠️ 上线拿到正式域名后，把 `og:image` / `twitter:image` 改成**绝对地址**（见 DEPLOY.md 第四节）。
- **发布工具**：`tools/build_dist.py` 生成优化发布包（只打包真正引用的文件、照片压缩约 40%，PSNR 35~48 dB）；`DEPLOY.md` 是发布与维护手册；`.gitignore` 排除 `.workbuddy/`、`dist/`、`.venv/`；已初始化 git 仓库。

## v1.5：摄影区统一为「高对比黑白 + 网点」一种形态

此前摄影区有**两条并行渲染路径**，观感不同（预览面板里是黑白照片、系统浏览器里是 1-bit 抖动）。现在**合并为一条**，两边完全一致：

- 静止态：**高对比黑白照片 + 淡网点**；hover 解出彩色原图。**纯 CSS，零 JS、零 canvas。**
- 深色 `--photo-filter: grayscale(1) contrast(1.5) brightness(1.04)` / `--photo-dots: .22`
- 浅色 `--photo-filter: grayscale(1) contrast(1.28) brightness(0.92)` / `--photo-dots: .3`

**删掉的**：`main.js` 里整个 1-bit Bayer 抖动模块（`BAYER` / `ditherImage` / `useFallback` / `initDither`）、CSS 的 `.dither-wrap canvas` 与 `.dither-wrap.fallback` 两套规则、HTML 上的 `class="dither-img"` 与 `data-scale`、以及 `file://` 的降级提示 toast。

**保留但已弃用**（当前无任何引用，可直接删）：`assets/img/dither/*.png`、`tools/gen_dither.py`。

**为什么删抖动**：抖动位图按 `naturalWidth / data-scale` 生成（故宫 900/4 = 225px），再放大到 335px 显示（1.49× 非整数倍），颗粒落到 **≈1.5 CSS px 的细网眼**——暗调照片（睡莲、灯会、打铁花）整片糊平，观感不如高对比黑白。详见 v1.4.2。

**顺带的好处**：不再有任何 `getImageData`，所以 `file://` 直接打开也能正常显示照片；两条路径不一致的问题从根上消失。

**验证**（无头 CDP，1440×900，模拟了「正常环境」与「受限沙箱」两种）：两环境下截图**逐像素完全相同（maxdiff = 0）**；页面中 canvas 数量为 0；深/浅两主题静止态滤镜与网点浓度正确、hover 后 `filter: none` 且网点归 0；全页 214 个文字元素对比度扫描无低对比项；断点 390 / 600 / 860 / 1024 / 1440 无横向溢出；0 条 console 错误。

## v1.4.2：摄影区静止态回到「高对比黑白」

反馈是「抖动版比之前糊、深色也没原来好看」。先量化定位：**canvas 抖动与静态抖动层渲染逐像素相同**（差异 < 0.02），所以问题不在降级路径，而在**抖动颗粒本身**——位图按 `naturalWidth / data-scale` 生成（故宫 900/4 = 225px），再放大到 335px 显示（非整数倍 1.49×），颗粒最终落在 **≈1.5 CSS px 的细网眼**；暗调照片（睡莲、灯会、打铁花）被这层细网糊成一片。

改法：**降级路径不再叠加任何抖动**，直接显示原图的「高对比黑白 + 淡网点」——细节保留、锐利清晰，hover 解出彩色原图：

| | 深色 | 浅色 |
|---|---|---|
| 滤镜 | `grayscale(1) contrast(1.5) brightness(1.04)` | `grayscale(1) contrast(1.28) brightness(0.92)` |
| 网点 `--photo-dots` | `.22` | `.3` |

- 移除 HTML 的 `data-dither`、CSS 的 `.dither-static` / `.has-static` 规则，以及 `useFallback()` 里创建静态层的那段。
- `assets/img/dither/*.png` 与 `tools/gen_dither.py` **保留但当前未启用**。
- ⚠️ 当时**两条路径观感不同**（受限沙箱 / `file://` = 高对比黑白；canvas 可用的系统浏览器 = 1-bit 抖动）。
  **v1.5 已把两条路径合并**，统一为高对比黑白，该差异不存在了。

## v1.4.1 修复速览

- **浅色下摄影区 hover 解不开原图（一直是黑白灰）**。
  `html[data-theme="light"] .dither-wrap.fallback img{…}` 权重是 (0,3,2)，高于
  `.dither-wrap.fallback:hover img` 的 (0,3,1)，而它又写在 hover **之后** → hover 的
  `filter:none` 被永久盖掉。修法：主题差异改用自定义属性（当时叫 `--fb-img` / `--fb-dots`，
  v1.5 起更名为 `--photo-filter` / `--photo-dots`）挂在 `html[data-theme="light"]` 上，
  不再直接命中元素，从根上不参与这两个选择器的权重比较。
  **教训：凡是「主题 A 与主题 B 的差异」，一律用自定义属性承载，不要写带属性选择器的规则去覆盖元素属性。**
- **（v1.4.2 已撤销）降级路径曾一度叠加静态 1-bit 抖动层。**
  抖动层渲染与 canvas 逐像素一致，但颗粒只有 ≈1.5px，观感比高对比黑白更糊，故回退。
  `assets/img/dither/*.png` 与 `tools/gen_dither.py` 保留备用，当前未启用。
- **为什么预览面板会降级**（实测复现）：面板把页面放进 `sandbox="allow-scripts"`（**不带**
  `allow-same-origin`）的 iframe → 页面 origin 变成 opaque → **同源图片也被当作跨源** →
  `getImageData()` 抛 `SecurityError`。对照组 `sandbox="allow-scripts allow-same-origin"` 则正常。
  所以在受限面板里预览看到的一直是降级路径；用系统浏览器打开 `http://localhost:8642/` 才走 canvas 抖动。

## v1.4 变更速览：一键切换浅色主题

右上角第一个图标（深色下显示太阳、浅色下显示月亮）即可切换，选择写入 `localStorage`，刷新/下次访问保持。

- **配色全部走 CSS 变量**（`html[data-theme="dark|light"]`）。本轮把原本写死的两处颜色也抽成了变量：`--dot`（首屏网点底纹）、`--shadow`（姓名像素投影）。**新增样式时不要再写死白/黑**，否则浅色主题必漏改。
- **防闪烁**：`<head>` 内联脚本在样式生效前读 `localStorage` 并设好 `data-theme`，避免刷新时先深后浅闪一下；无存储权限（无痕模式）时静默降级为深色。
- **`<head>` 与 `main.js` 分工**：head 负责「尽早定色」，`initTheme()` 负责切换交互，并同步 `meta[theme-color]`、favicon、按钮的 `title/aria-label/aria-pressed`。`initTheme()` 在脚本解析时立刻执行（不放进 `DOMContentLoaded`），否则标签页图标会闪一下。
- **（v1.5 已删除）1-bit 抖动图在浅色下必须反相**：`html[data-theme="light"] .dither-wrap canvas { filter: invert(1) }`。黑底上本来就是「白点成画」（亮部成画，观感轻）；原样搬到白底会变成「暗部成画」，夜景/深调照片直接糊成一块黑砖。现在没有抖动图了，浮动滤镜改成写在高对比黑白上的 `--photo-filter`。
- **默认主题为深色**（作品集第一印象按深色设计）。若要改为「跟随系统」，在 head 内联脚本里把兜底分支换成 `matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark'` 即可。
- 多标签页之间通过 `storage` 事件同步主题。
- 浅色下 `--dim` 压深到 `#6f6f6f`（白底需 ≥4.5:1）；摄影区的黑白照片在浅色下额外压暗一档（`--photo-filter`），避免「发飘」。

**验证**（无头 CDP，1440×900）：切换后 `data-theme / localStorage / body 背景色 / meta / favicon / 图标 / aria` 全部同步、刷新后保持浅色；全页 **214 个文本元素在两个主题下都做了前景×背景对比度扫描，均无 < 2.4 的低对比元素**（即没有「白字白底」这类漏改）；展开态标题 hover 仍为整行反色；断点 390 / 560 / 860 / 1024 / 1440 无横向溢出，0 条 console 错误。

## v1.3.1 修复速览

- **实习手风琴：展开态 hover 变「隐形」**。`.acc-item[open] > summary` 与 `.acc-item summary:hover` 选择器权重相同（都是 0-2-1），原来把展开态底色写在 hover 之后 → hover 时底色被浅灰 `rgba(255,255,255,.08)` 盖掉、hover 的黑字照旧生效 = 黑字压深底，整行标题看不见。现把 `[open]` 底色规则挪到 hover 之前，展开态 hover 与收起态完全一致（整行反色高亮）。
- **收起第一段（默认展开）后第 3、4 段「消失」**。手风琴收起只改变页面高度，**不会派发 scroll 事件**，而滚动入场只监听 scroll（兜底轮询 12s 后也会停），折叠线以下的 `.reveal` 就永远停在 `opacity: 0`。现在 `initReveal` 里补了两条复查机制：**`details` 的 `toggle` 事件**（toggle 不冒泡，需逐个绑定）+ **`ResizeObserver(document.body)`** 兜底。

## v1.3 变更速览

- **导航 Logo**：中英文对调 → `■ 林晓煊`（白、16px）在前，`SHARON LIN`（灰、11px）退为副标签；≤860px 隐藏英文标签。
- **首屏**：删去 `// PORTFOLIO · 2026 · HANGZHOU` 那一行（`.eyebrow` 样式一并移除）。
- **首屏文案**：「AI 在定义新的产品。」→「**我们存在于一生仅一次的当下。**」（`Stay hungry, stay foolish.` 保留）。
- **首屏版式重排**（结构：左「文」右「图」＋底部通栏要点）：
  - 第一行：中文名（底端）＋ 证件照（底端），两者同时压在 `hero-rest` 的同一条分隔线上（实测差值 0px）；照片放大到 `clamp(132px, 14vw, 168px)`。
  - 第二行：`SHARON LIN_` / 身份 / 一句话 / 两个按钮（英文名从姓名组挪到分隔线下方，姓名才天然与照片同底）。
  - 第三行：三行亮点改为**通栏 `repeat(3, 1fr)`**，铺满整幅宽度，首屏下半部不再有中部留白。
  - ≤860px 退化为单列竖排（中文名 → 头像 → 英文名/身份/一句话/按钮 → 要点条）。

## v1.2 变更速览

- **首屏**：改为两列网格 `.hero-inner`（左 1.32fr / 右 0.68fr）。
  - 左栏：`// PORTFOLIO` + 姓名 + SHARON LIN + 身份 + 一句话 + 两个按钮；右栏：**彩色头像 + 三行亮点**（亮点从左侧移过来，解决「左密右疏」）。
  - 头像缩到 `clamp(108px, 11vw, 138px)`；**底端与「林晓煊」底端对齐**由 `align-items/align-self: end` 实现（实测差值 0px，不靠 JS）。
  - 亮点块 `justify-self: end`，右边缘与头像右边缘对齐。
  - ≤860px 退化为单列竖排（姓名 → 头像 → 简介 → 亮点）。

## v1.1 变更速览

- **滚动方式**：整屏吸附分页（`html { scroll-snap-type: y proximity }` + 每个板块 `min-height: calc(100svh - var(--nav-h))`）。
  - `--nav-h`（顶栏高度，桌面 62px / 小屏 92px）同时用于 `scroll-padding-top` 和板块算高，改顶栏高度时记得同步。
  - ⚠️ 不要给板块加 `scroll-snap-stop: always`：它会阻断导航锚点跳转和大跨度程序化滚动（实测会让懒加载图片永不加载）。
  - 个别超过一屏的板块（如「工作之外」）在板块内正常滚动，这是预期行为。
- **实习经历**：删去开源证券、浙大经院两段，现为 01-04。
- **联系**：文案去掉「数据产品」。

## 目录结构

```
├── index.html              # 全部页面内容（单页）
├── preview.sh              # 一键本地预览（起 http 服务 + 打开浏览器）
├── assets/
│   ├── css/style.css       # 全部样式（主题变量在文件开头）
│   ├── js/main.js          # 交互：主题切换 / 入场动画 / 导航高亮 / toast（无像素处理）
│   ├── fonts/cubic/        # Cubic 11 像素中文字体（开源可商用，勿删 result.css）
│   └── img/
│       ├── *.jpg           # 原始照片
│       └── dither/*.png    # ⚠️ 已废弃（v1.5 起无任何引用，可直接删）
├── tools/gen_dither.py     # ⚠️ 已废弃（v1.5 起无任何引用，可直接删）
└── README.md
```

## 内容维护

所有文案直接改 `index.html`，按 section 注释定位（导航 / HERO / 关于我 / 教育 / 经历 / 项目 / 技能 / 生活 / 联系）。

- **图片**：放进 `assets/img/`，套一层 `<div class="dither-wrap" style="aspect-ratio: …">` 即可自动获得「静止态高对比黑白 + 淡网点，hover 解出彩色原图」的效果（**纯 CSS，无需任何 JS/class 钩子**）。
  - 效果强度用主题变量调：`--photo-filter`（滤镜）、`--photo-dots`（网点浓度），定义在 `style.css` 顶部的 `html[data-theme]` 里。
  - `aspect-ratio` 想裁切就写成想要的比；**想保留原图完整比例，就把 `aspect-ratio` 写成和原图一致**（摄影区现在就是这么做的，所以不裁切、高度自然错落）。
  - 摄影区用 `columns: 3` 做错落（masonry），每张的 `aspect-ratio` 直接写在 `index.html` 的 `.dither-wrap` 上；换图时记得同步改这个值（否则会被 `object-fit: cover` 裁切）。列数断点：≤860px 两列、≤560px 一列。
  - 首屏头像是**彩色原图**，不套 `.dither-wrap`（所以不受滤镜影响）。
- **联系信息**：在 `#contact` 区块；微信号在 `index.html`（LOXOXOLO）和 `main.js` 的 `initCopy` 里各有一处。
- **内容来源**：飞书文档《小炫的自我介绍》`https://my.feishu.cn/docx/VnXUdajwtoYSTlx1nDJc1wvqnDf`（更新经历后同步过来即可）。

## 后续路线（已预留的扩展点）

- **跟随系统深浅色**：默认固定深色；若要跟随系统，把 `<head>` 内联脚本里的兜底分支换成
  `matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark'`（用户手动选过仍以选择为准）。
- **英文版**：HTML 已埋 `data-i18n` 属性；在 main.js 加一个 zh/en 字典 + `applyLang()` 即可。
- 部署：纯静态站，任意静态托管（GitHub Pages / Vercel / EdgeOne Pages）直接上传整个目录。

## 本地预览

**推荐**：双击 `preview.sh`，或在终端执行

```bash
sh preview.sh          # 默认 8642 端口，会自动打开浏览器
sh preview.sh 8080     # 也可指定端口
```

> ℹ️ **关于 `file://` 直接双击打开**：v1.5 起页面已不再读 canvas 像素，`file://` 下照片也能正常显示（黑白 + hover 彩图）。
> 个别浏览器可能拦截 `file://` 下的网页字体加载，所以仍**推荐**用 `preview.sh`（http://localhost）。
> 部署到静态托管后是 http(s) 协议，无任何限制。

## 素材版权备注

- 字体：Cubic 11（自由软件，可自由使用/修改/商用，见 `assets/fonts/cubic/result.css` 头部声明）
- 图片与文案：林晓煊本人（来自其飞书个人文档）
