长桥投资思想研究 · 完整离线版

入口：longbridge-research.html
长文索引：longform-library.html

迁移方法
1. 主报告已内嵌长文索引和全部本地正文。只复制 longbridge-research.html，也能使用全部页内功能和本地正文阅读。
2. 电脑：用 Chrome、Edge 或 Safari 打开 longbridge-research.html。
3. iPad：在“文件”中解压；若系统预览不能完整运行筛选，请用支持本地 HTML 的文件浏览器打开，或从电脑通过同一 Wi-Fi 提供静态网页后用 Safari 访问。
4. 线上使用：首次等待页面显示“全部页面已加载，可断网阅读”，之后即使断网，也能切换作者、案例、目录、搜索，以及打开此前未读过的本地正文。
5. 本地正文在页内阅读窗口打开，可返回上一页或关闭阅读，回到报告原来的位置。原帖等外部链接仍需要联网。
6. 若需要断网后关闭浏览器再重新打开，请保存主 HTML 到本地，或提前下载 ZIP；线上网址的重新加载仍取决于网络和浏览器缓存。

完整性
- 主页面无外部脚本、样式、字体或按需下载的正文。阅读窗口使用主 HTML 内已包含的页面，不请求网络。
- ZIP 同时保留独立长文索引和 library 文件夹；单独打开 longform-library.html 时，应保持它与 library 文件夹的相对位置。
- focused-delivery-manifest.json 与 local-library-manifest.json 保存覆盖口径和文件清单。

维护
- 修改独立长文、长文索引或离线阅读器后，运行 python3 scripts/embed_offline.py 更新主报告中的内嵌内容。
- python3 scripts/build_pages.py 会检查内嵌版本、页面结构和本地链接，避免发布内容不一致的离线包。
- 浏览器断网回归测试：在安装 Playwright 的 Python 环境中运行 scripts/test_offline_browser.py。
