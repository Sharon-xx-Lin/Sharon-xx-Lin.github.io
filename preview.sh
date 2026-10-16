#!/bin/sh
# 本地预览个人网站：启动静态服务器并自动打开浏览器
# 用法：双击本文件，或在终端执行  sh preview.sh
cd "$(dirname "$0")" || exit 1

PORT="${1:-8642}"
URL="http://localhost:$PORT/"

echo "→ 网站目录：$(pwd)"
echo "→ 预览地址：$URL"
echo "→ 按 Ctrl+C 停止"

python3 -m http.server "$PORT" >/dev/null 2>&1 &
SERVER_PID=$!
trap 'kill $SERVER_PID 2>/dev/null' INT TERM EXIT

sleep 1
if command -v open >/dev/null 2>&1; then open "$URL"; fi
wait "$SERVER_PID"
