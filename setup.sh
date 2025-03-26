#!/bin/bash

# 創建必要的目錄
mkdir -p ~/.streamlit

# 寫入 Streamlit 配置
echo "[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml