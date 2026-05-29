# Windows 本地试用说明

这份说明用于在 Windows 电脑上本地运行“公众号招募工作台”。

## 1. 需要准备

- Windows 电脑
- Python 3.11 或 3.12
- 可以访问外网安装依赖
- 项目压缩包
- `.env` 配置文件

## 2. 解压项目

请保持目录结构如下：

```text
公众号招募/
  poster-generator/
    player-recruitment-poster-standalone.html
  ux-recruitment-bot/
    app/
    start.ps1
    run.py
```

不要只复制 `ux-recruitment-bot`，因为它需要使用旁边的 `poster-generator` 海报 HTML。

## 3. 配置 .env

进入：

```text
公众号招募/ux-recruitment-bot
```

复制：

```text
.env.example
```

重命名为：

```text
.env
```

然后填写真实配置：

```text
OPENAI_API_KEY=
OPENAI_BASE_URL=
MODEL_NAME=
WECHAT_APP_ID=
WECHAT_APP_SECRET=
WECHAT_AUTHOR=
```

说明：

- 如果只是生成文案、海报、二维码，公众号配置可以暂时不测
- 如果要测试“推送草稿箱”，公众号配置必须正确
- 当前默认不调用 LLM，只有勾选“使用 LLM 润色文案”才需要 LLM 可用

## 4. 启动工具

在 `ux-recruitment-bot` 文件夹中，右键空白处，选择：

```text
在终端中打开
```

执行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\start.ps1
```

第一次启动会安装依赖和浏览器内核，可能需要几分钟。

看到类似以下内容表示启动成功：

```text
Uvicorn running on http://0.0.0.0:8000
Application startup complete.
```

## 5. 打开工作台

在浏览器打开：

```text
http://127.0.0.1:8000/workbench
```

## 6. 使用顺序

1. 填写活动基本信息
2. 填写玩家要求
3. 粘贴报名链接和社群链接
4. 填写封面标题和截止日期
5. 点击“生成预览”
6. 检查公众号文案、长海报、封面图
7. 下载图片或复制文案
8. 如需测试公众号，点击“推送草稿箱”

## 7. 关闭工具

回到启动工具的终端窗口，按：

```text
Ctrl + C
```

关闭终端即可。

## 8. 常见问题

### 无法运行 start.ps1

先执行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

然后再执行：

```powershell
.\start.ps1
```

### 提示 python 不是内部或外部命令

说明电脑没有安装 Python，或安装时没有勾选 `Add Python to PATH`。

处理方式：

- 安装 Python 3.11 或 3.12
- 安装时勾选 `Add Python to PATH`

### 推送草稿箱失败，提示 invalid ip not in whitelist

这是公众号后台 IP 白名单问题，不是工具问题。

需要公众号负责人把当前电脑访问微信 API 的出口 IP 加到公众号后台白名单。

### 生成很慢

第一次启动会安装依赖和 Chromium，比较慢。后续启动会快很多。

### 只想生成海报，不想调用 LLM

默认不会调用 LLM。不要勾选：

```text
使用 LLM 润色文案
```

