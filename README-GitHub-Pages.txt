长桥研究站点 · GitHub Pages 部署

项目类型
纯静态 HTML / CSS / JavaScript 站点，无后端、数据库或 npm 依赖。
主报告：longbridge-research.html；长文索引：longform-library.html。
library/ 内有 759 篇文章。原始内容约 26.6 MiB，主报告约 16.5 MiB，首次访问需要加载完整报告。
外部原帖链接需要联网。GitHub Pages 发布后，网页内容可公开访问。

已添加的部署支持
- index.html：网站根地址入口，自动进入主报告，保留查询参数和页内锚点。
- .github/workflows/pages.yml：推送 main 后自动检查、打包并发布。
- scripts/build_pages.py：检查本地 HTML 链接，只复制站点文件至 _site/，生成离线 ZIP。
- .nojekyll：无需 Jekyll 处理。
- .gitignore：排除生成目录和系统文件。
原有报告、文章和 JSON 清单未修改。

首次部署
1. 目标仓库为 https://github.com/thunderbird0902/longbridge-research 。
2. 上传此项目时，在终端运行：

   cd /Users/wangjing/Documents/longbridge-research-offline
   git init -b main
   git add .gitignore .nojekyll .github scripts index.html longbridge-research.html longform-library.html library focused-delivery-manifest.json local-library-manifest.json README-离线使用.txt README-GitHub-Pages.txt
   git commit -m "Prepare static research site for GitHub Pages"
   git remote add origin git@github.com:thunderbird0902/longbridge-research.git
   git push -u origin main

   推送时使用已配置的 GitHub 登录方式；HTTPS 不支持用 GitHub 账户密码认证。
3. 打开仓库 Settings → Pages → Build and deployment → Source，选择 GitHub Actions。
4. 打开 Actions → Deploy GitHub Pages → Run workflow，选择 main 运行。
   首次推送若因尚未设置 Pages 而失败，完成第 3 步后重新运行即可。
5. 等待 build 和 deploy 都成功，点击部署任务显示的网站地址。

最终访问地址
https://thunderbird0902.github.io/longbridge-research/
主报告：https://thunderbird0902.github.io/longbridge-research/longbridge-research.html
长文索引：https://thunderbird0902.github.io/longbridge-research/longform-library.html
离线下载：https://thunderbird0902.github.io/longbridge-research/longbridge-research-offline.zip
等待 Pages 发布成功后即可访问。

本地验证
在项目目录执行：
   python3 scripts/build_pages.py
   python3 -m http.server 8000 --directory _site --bind 127.0.0.1
浏览器打开 http://127.0.0.1:8000/ ，按 Ctrl+C 停止预览。
_site/ 是可重新生成的发布目录，不要把手工修改放在这里。

以后更新
修改原始 HTML / library / JSON 文件后提交并推送 main，自动重新发布。
无需提交 _site/ 或离线 ZIP；离线包会在每次发布时重新生成。
若使用其他默认分支，需同步修改 pages.yml 中的 branches: [main]。

官方说明
https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
