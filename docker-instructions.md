# Streamlit 應用程序 Docker 容器化指南

## 概述

本文檔說明如何使用 Docker 容器運行此 Streamlit 待辦事項管理系統。Docker 容器可以提供一致的運行環境，使應用程序在不同平台上的部署和運行更加可靠。

## 先決條件

- 安裝 [Docker](https://docs.docker.com/get-docker/)
- 安裝 [Docker Compose](https://docs.docker.com/compose/install/) (推薦但非必需)

## 使用 Docker Compose（推薦方法）

1. 在項目根目錄中，運行以下命令啟動應用程序：

   ```bash
   docker-compose up
   ```

2. 在瀏覽器中訪問：`http://localhost:5000`

3. 要在後台運行服務：

   ```bash
   docker-compose up -d
   ```

4. 要停止服務：

   ```bash
   docker-compose down
   ```

## 使用 Docker 命令（替代方法）

1. 構建 Docker 映像：

   ```bash
   docker build -t streamlit-todo-app .
   ```

2. 運行容器：

   ```bash
   docker run -p 5000:5000 streamlit-todo-app
   ```

3. 要使用卷掛載以便立即反映代碼更改（開發模式）：

   ```bash
   docker run -p 5000:5000 -v $(pwd):/app streamlit-todo-app
   ```

## 數據持久性

應用程序使用本地 JSON 文件存儲任務和系統參數。在 Docker 容器中，這些文件將保存在容器的文件系統中。

- 如果您希望數據在容器重啟後依然保留，請使用卷掛載（如 docker-compose.yml 中所配置）。
- 對於生產環境，建議考慮使用數據庫作為後端存儲。

## 自定義配置

您可以通過修改 `.streamlit/config.toml` 文件或在運行容器時傳遞環境變量來更改 Streamlit 的配置設置。

## 故障排除

- 如果您看到端口衝突錯誤，可以在 docker-compose.yml 中更改映射的主機端口（例如，將 "5000:5000" 更改為 "8501:5000"）。
- 確保您的防火牆允許指定端口的流量。