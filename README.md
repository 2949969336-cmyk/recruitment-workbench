# 公众号招募工作台

一个用于游戏玩家招募活动的本地/内网工作台。

## 核心能力

- 填写活动需求单
- 支持多类玩家要求
- 报名链接/社群链接自动生成二维码
- 自动生成长版招募海报
- 自动生成横版公众号封面图
- 推送到公众号草稿箱
- 公众号封面使用横版封面图
- 公众号正文只插入长版招募海报图片

## 项目结构

```text
poster-generator/
  player-recruitment-poster-standalone.html

ux-recruitment-bot/
  app/
  run.py
  start.ps1
  requirements.deploy.txt
```

## Windows 本地试用

进入：

```text
ux-recruitment-bot/
```

复制 `.env.example` 为 `.env`，填写配置。

启动：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\start.ps1
```

打开：

```text
http://127.0.0.1:8000/workbench
```

详细说明见：

```text
ux-recruitment-bot/MENTOR_WINDOWS_TRIAL.md
```

## 安全说明

不要提交：

- `.env`
- API Key
- AppSecret
- 生成的二维码/海报图片
- `.venv`

已通过 `.gitignore` 默认排除这些内容。
