# 发布与更新指南

面向长期维护。所有命令都在项目目录下执行：

```bash
cd "/Users/linxiaoxuan/Downloads/xx personal site"
```

---

## 当前状态（2026-10-17 已正式上线）

| 项目 | 状态 |
|---|---|
| **正式网址** | **https://sharon-xx-lin.github.io/** |
| 托管 | GitHub Pages（源：`Sharon-xx-Lin/Sharon-xx-Lin.github.io` 仓库 `main` 分支根目录） |
| 远端 | `origin` = https://github.com/Sharon-xx-Lin/Sharon-xx-Lin.github.io.git<br>`backup` = https://github.com/Sharon-xx-Lin/linxiaoxuan.github.io.git（代码备份，Pages 已关） |
| 发布包构建 | `tools/build_dist.py`（可选，见第三节） |

> 仓库名与 GitHub 账号名**完全同名**（`Sharon-xx-Lin.github.io`）才会得到不带路径的
> `https://sharon-xx-lin.github.io/`。早期那个 `linxiaoxuan.github.io` 仓库名字和账号名不一致，
> 网址会多一级 `/linxiaoxuan.github.io/` 路径，已弃用（只留作备份仓库）。

---

## 一、正式发布（推荐：GitHub Pages）

免费、永久、改完自动更新。**本步骤已完成**（2026-10-17），下面是重建流程，留作备忘／换电脑时参考。

> ⚠️ 命名规则：仓库名取成 `你的用户名.github.io` 时，网址是 `https://你的用户名.github.io/`；
> 取其他名字（如 `portfolio`）时，网址会多一级路径 `https://你的用户名.github.io/portfolio/`。
> 想要最干净的网址，仓库名必须与 GitHub 账号名一致。

### 第 1 步：在 GitHub 建一个空仓库

1. 登录 [github.com](https://github.com)，右上角 `+` → **New repository**
2. Repository name 建议 `portfolio`
3. 选 **Public**（Private 仓库用 Pages 需要付费版）
4. **不要**勾选 "Add a README file" / ".gitignore" / "license"（保持空仓库，否则第一次推送会冲突）
5. 点 Create repository

### 第 2 步：把本地代码推上去

推荐先装 GitHub CLI，登录一次以后都不用再管密码：

```bash
brew install gh && gh auth login
```

然后：

```bash
cd "/Users/linxiaoxuan/Downloads/xx personal site"
git remote add origin https://github.com/你的用户名/portfolio.git
git branch -M main
git push -u origin main
```

> 不用 `gh` 的话，推送时会要求输入用户名和密码 —— 密码处要填 **Personal Access Token**
> （GitHub 早已不支持账号密码。生成：GitHub → 头像 → Settings → Developer settings →
> Personal access tokens → Tokens (classic) → Generate new token，勾选 `repo`，生成后立刻复制保存）。

### 第 3 步：开启 Pages

仓库页面 → **Settings** → 左侧 **Pages** → Source 选 `Deploy from a branch`
→ Branch 选 `main`、目录选 `/ (root)` → **Save**

### 第 4 步：等待 1~2 分钟

访问 `https://你的用户名.github.io/portfolio/` 就是正式网站了。

> 小技巧：如果仓库名取成 `你的用户名.github.io`，网址会变成更简洁的 `https://你的用户名.github.io/`

---

## 二、发布之后还能改吗？

**能，随时改，而且改完 1~2 分钟自动生效。** 不需要重新发布，也不需要碰任何设置。

### 日常更新流程

```bash
cd "/Users/linxiaoxuan/Downloads/xx personal site"

# 1. 改内容（文案改 index.html，照片替换 assets/img/ 下的文件）
# 2. 提交并推送
git add -A
git commit -m "更新：新增 XX 实习经历"
git push
```

推送后 GitHub Pages 会自动重新构建，大约 1~2 分钟后线上就是新的了。

### 改哪里

| 想改什么 | 改哪个文件 |
|---|---|
| 文案、板块内容 | `index.html`（按 `<!-- ======= 关于我 ======= -->` 这类注释定位） |
| 照片 | 替换 `assets/img/` 下的同名文件 |
| 微信号 / 联系方式 | `index.html` 和 `assets/js/main.js` **各有一处**，都要改 |
| 配色、字号、间距 | `assets/css/style.css`（开头是深浅两套颜色变量） |
| 分享卡片封面 | `assets/img/og-cover.png`（想换文案就改 `tools/gen_og.py` 再跑） |

### 换照片的注意点

- 摄影区的每张图都写着 `aspect-ratio`（在 `index.html` 的 `.dither-wrap` 上），**新图比例要和它对得上**，否则会被裁切。
- 首屏头像 `portrait.jpg` 是彩色原图，不做黑白处理。
- 一张图建议控制在 500 KB 以内。

---

## 三、可选：让页面更小、加载更快

`tools/build_dist.py` 会生成一份优化后的发布包：只打包真正用到的文件，并把照片压缩约 40%（画质实测 PSNR 35~48 dB，且照片实际显示宽度只有约 335px，肉眼无差别）。

```bash
# 需要 Pillow（只需装一次）
python3 -m venv .venv && .venv/bin/pip install pillow

# 生成 dist/
.venv/bin/python tools/build_dist.py
```

两种用法：

- **拖拽类平台**（Vercel、EdgeOne Pages 等）：直接把 `dist/` 文件夹拖上去。
- **GitHub Pages**：如果你也想让线上用压缩图，改成
  `.venv/bin/python tools/build_dist.py --out docs`，
  提交 `docs/` 目录，并把 Pages 的发布目录从 `/ (root)` 改成 `/docs`。
  （默认走仓库根目录发布，用的是未压缩原图，总量 1.8 MB，也完全够用。）

---

## 四、拿到正式域名后，必做一件事

否则链接发到微信 / 领英时可能没有封面图。把 `index.html` 里这两行的值改成绝对地址：

```html
<meta property="og:image" content="https://你的域名/assets/img/og-cover.png" />
<meta name="twitter:image" content="https://你的域名/assets/img/og-cover.png" />
```

（微信、领英对相对路径不友好，必须绝对地址。）

---

## 五、其他发布平台（备选）

| 平台 | 操作 | 特点 |
|---|---|---|
| **Vercel** | [vercel.com](https://vercel.com) → New Project → 把 `dist/` 拖进去 | 最快，1 分钟出链接；`*.vercel.app` 国内访问不稳 |
| **腾讯云 EdgeOne Pages** | 控制台新建项目 → 上传 `dist/` | 国内访问快，适合简历给国内 HR 看 |
| **Cloudflare Pages** | 连接 GitHub 仓库 | 全球 CDN，免费额度大 |

---

## 六、绑定自己的域名（可选，稍后再做也行）

1. 买域名（阿里云 / 腾讯云 / Namecheap，`.com` 约 60~80 元/年，`.cn` 更便宜）
2. 域名商后台加一条 DNS 解析：类型 `CNAME`、主机记录填 `www` 或 `@`、值填你的站点地址
   （GitHub Pages 需填 `你的用户名.github.io`）
3. 回到仓库 Settings → Pages → Custom domain 填上域名 → Save，勾选 Enforce HTTPS
4. 等待几分钟到几小时生效
5. 生效后记得回到第四节，把 og:image 换成新域名

> ⚠️ 如果之后把网站托管在国内服务器（如腾讯云服务器、需备案的对象存储），域名要先做 ICP 备案。
> GitHub Pages / Vercel / EdgeOne 这类则不需要备案。

---

## 七、常见问题

**推送时报 403 / 认证失败？**
密码处不能用 GitHub 账号密码，要用 Personal Access Token，或改用 `gh auth login`。

**改了东西，线上没变？**
先等 2 分钟（构建有延迟）；再强制刷新浏览器：`Cmd + Shift + R`。也可以到仓库的 Actions 标签看构建状态。

**换电脑了怎么继续维护？**
```bash
git clone https://github.com/Sharon-xx-Lin/Sharon-xx-Lin.github.io.git
cd Sharon-xx-Lin.github.io
```
然后照第二节的流程改就行了。

**`git remote add origin` 报 `error: remote origin already exists`？**
说明已经加过（或之前填的是占位地址）。不要删了再加，直接覆盖：
```bash
git remote set-url origin https://github.com/你的用户名/你的仓库.git
```
确认地址：`git remote -v`

**原始照片被覆盖了想找回？**
首次提交包含所有原图，可以随时取回：
```bash
git show 首次提交的版本号:assets/img/gugong.jpg > 恢复的图.jpg
```
（`git log --oneline` 可以看到提交版本号。）
