# 公众号招募工作台

这是一个用于生成公众号招募文案和招募海报的 FastAPI 工具。

当前能力：

- 工作台表单录入活动信息
- 稳定模板生成公众号正文
- 可选 LLM 润色文案
- 报名链接/社群链接自动生成二维码
- 可上传二维码图片覆盖自动生成结果
- 调用 HTML 海报工具自动渲染 PNG
- 在线预览、复制正文、下载海报

## 目录要求

部署时需要保持以下目录关系：

```text
公众号招募/
  poster-generator/
    player-recruitment-poster-standalone.html
  ux-recruitment-bot/
    app/
    run.py
    requirements.deploy.txt
```

`ux-recruitment-bot` 会复用相邻目录中的 HTML 海报工具：

```text
../poster-generator/player-recruitment-poster-standalone.html
```

## 本地启动

Windows 试用请优先阅读：

```text
MENTOR_WINDOWS_TRIAL.md
```

```powershell
cd D:\公众号招募\ux-recruitment-bot
.\.venv\Scripts\activate
python run.py
```

打开：

```text
http://127.0.0.1:8000/workbench
```

## Windows 内网服务器部署

1. 将 `公众号招募` 整个目录复制到内网服务器。

2. 进入后端目录：

```powershell
cd D:\公众号招募\ux-recruitment-bot
```

3. 创建 `.env`：

```powershell
copy .env.example .env
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

4. 安装并启动：

```powershell
.\start.ps1
```

5. 在服务器浏览器访问：

```text
http://127.0.0.1:8000/workbench
```

6. 同事通过内网访问：

```text
http://服务器内网IP:8000/workbench
```

如果同事打不开，需要检查服务器防火墙是否放行 `8000` 端口。

## Linux 内网服务器部署

1. 将 `公众号招募` 整个目录复制到服务器。

2. 进入后端目录：

```bash
cd /path/to/公众号招募/ux-recruitment-bot
```

3. 创建 `.env`：

```bash
cp .env.example .env
```

4. 安装并启动：

```bash
bash start.sh
```

5. 访问：

```text
http://服务器内网IP:8000/workbench
```

## 生产运行建议

当前 `python run.py` 适合内网试运行。长期部署建议：

- 使用固定服务器运行，不依赖个人电脑
- 配置内网域名或反向代理
- 加访问控制，避免非团队成员访问
- 将 `.env` 只保存在服务器，不提交到 Git
- 定期清理 `app/static/generated/posters` 下的历史海报

## 常见问题

### GitHub Pages 可以部署这个工具吗？

不适合。GitHub Pages 只能托管静态网页，不能运行 FastAPI、Playwright、LLM 调用或公众号 API。

推荐做法是：

```text
GitHub 存代码
内网服务器运行服务
同事通过内网链接访问
```

### 为什么之前海报工具可以放 GitHub Pages？

之前的海报工具是纯前端 HTML，不需要后端。现在的工作台需要后端生成二维码、调用 Playwright 渲染海报，并且后续会接公众号 API，所以需要服务器。

### 需要一直开着谁的电脑？

不需要开个人电脑。服务部署到公司内网服务器后，只要服务器运行，同事都可以访问。
