"""Embed the complete local reading library in the report; no network/runtime dependencies."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEAD_START, HEAD_END = '<!-- OFFLINE HEAD START -->', '<!-- OFFLINE HEAD END -->'
DATA_START, DATA_END = '<!-- OFFLINE READER START -->', '<!-- OFFLINE READER END -->'
STATUS = '<p id="offline-status" role="status">正在准备离线内容…</p>'


def embed_report(text, root=ROOT):
    for start, end in [(HEAD_START, HEAD_END), (DATA_START, DATA_END)]:
        text = re.sub(re.escape(start) + r'.*?' + re.escape(end), '', text, flags=re.S)
    text = re.sub(r'<p id="offline-status"[^>]*>.*?</p>', '', text, flags=re.S)
    pages = {'longform-library.html': (root / 'longform-library.html').read_text(encoding='utf-8')}
    pages.update({file.relative_to(root).as_posix(): file.read_text(encoding='utf-8')
                  for file in sorted((root / 'library').glob('*.html'))})
    payload = json.dumps(pages, ensure_ascii=False, separators=(',', ':')).replace('<', r'\u003c')
    css = (root / 'scripts/offline-reader.css').read_text(encoding='utf-8')
    script = (root / 'scripts/offline-reader.js').read_text(encoding='utf-8')
    head = HEAD_START + '<style>' + css + '</style><script>document.documentElement.setAttribute("data-offline-preparing", "");</script>' + HEAD_END
    reader = DATA_START + '''<dialog id="offline-reader" aria-labelledby="offline-reader-title">
<div class="offline-reader-bar"><button id="offline-reader-back" type="button">返回报告</button><span id="offline-reader-title">本地正文</span><button id="offline-reader-close" type="button">关闭阅读</button></div>
<iframe id="offline-frame" title="离线正文阅读" referrerpolicy="no-referrer"></iframe></dialog>'''
    reader += '<script id="offline-pages" type="application/json">' + payload + '</script><script>' + script + '</script>' + DATA_END
    text = text.replace('</head>', head + '</head>', 1)
    text = text.replace('</header>', STATUS + '</header>', 1)
    return text.replace('</body>', reader + '</body>', 1)


if __name__ == '__main__':
    report = ROOT / 'longbridge-research.html'
    report.write_text(embed_report(report.read_text(encoding='utf-8')), encoding='utf-8')
    print('Embedded longform index and all local articles into the report')
