"""Browser regression: page loads once, then all internal reading works offline.

Run with a Python environment containing Playwright. BROWSER_EXECUTABLE can point
at an installed Chrome; otherwise Playwright's Chromium installation is used.
"""
import functools
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def check(browser, url, offline_from_start=False):
    context = browser.new_context(viewport={'width': 1440, 'height': 900})
    if offline_from_start:
        context.set_offline(True)
    page = context.new_page()
    errors, requests = [], []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(url, wait_until='load')
    page.wait_for_function('!document.documentElement.hasAttribute("data-offline-preparing")')
    page.add_style_tag(content='html{scroll-behavior:auto!important}')
    context.set_offline(True)
    context.on('request', lambda request: requests.append(request.url))
    assert page.locator('#offline-status').inner_text() == '全部页面已加载，可断网阅读'
    for option in page.locator('#author-map-picker option').evaluate_all('(xs)=>xs.map(x=>x.value)'):
        page.locator('#author-map-picker').select_option(option)
        for view in ['map', 'study', 'notes']:
            page.locator('.research-tabs:visible [data-view="' + view + '"]').click()
            assert page.locator('.research-panel:visible').count() == 1
    page.locator('#q').fill('成本')
    assert page.locator('#results .post').count() > 0
    for case in page.locator('.case-index-card').evaluate_all('(xs)=>xs.map(x=>x.dataset.caseId)'):
        page.locator('[data-case-id="' + case + '"]').click()
        assert page.locator('.curated-case:visible').get_attribute('data-case-detail') == case
    page.locator('#author-map-picker').select_option('1')
    page.locator('.research-tabs:visible [data-view="notes"]').click()
    note_search = page.locator('.research-panel:visible .author-note-search')
    note_search.fill('成本')
    saved_scroll = page.evaluate('scrollY')
    # A library entry the browser has never visited must open without a request.
    page.locator('a[href="library/25730309.html"]').first.evaluate('(a)=>a.click()')
    reader = page.frame_locator('#offline-frame')
    reader.locator('h1').wait_for()
    assert '想赚钱' in reader.locator('h1').inner_text()
    assert page.locator('#offline-reader').evaluate('(e)=>e.open')
    # The index is also resident, and its search scripts run inside the reader.
    reader.locator('a[href="../longform-library.html"]').click()
    reader.locator('#q').wait_for()
    reader.locator('#q').fill('25730309')
    reader.locator('#q').fill('成本')
    assert reader.locator('#results .post').count() > 0
    reader.locator('#results a[href^="library/"]').first.click()
    reader.locator('h1').wait_for()
    page.locator('#offline-reader-back').click()
    reader.locator('#q').wait_for()
    page.locator('#offline-reader-close').click()
    page.wait_for_function('!document.getElementById("offline-reader").open')
    assert note_search.input_value() == '成本'
    assert abs(page.evaluate('scrollY') - saved_scroll) < 2
    # Browser forward/back follows the internal reading history too.
    page.go_forward()
    reader.locator('h1').wait_for()
    page.go_back()
    page.wait_for_function('!document.getElementById("offline-reader").open')
    # Narrow screen and Escape must not leave a blocking overlay behind.
    page.set_viewport_size({'width': 390, 'height': 844})
    page.locator('a[href="library/25730309.html"]').first.evaluate('(a)=>a.click()')
    reader.locator('h1').wait_for()
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    assert reader.locator('html').evaluate('(e)=>e.scrollWidth <= innerWidth')
    page.keyboard.press('Escape')
    page.wait_for_function('!document.getElementById("offline-reader").open')
    assert not errors, errors
    assert not requests, requests
    context.close()
    print('PASS:', url, '— author tabs, cases, searches, articles, index, history; zero requests after load')


def main():
    handler = functools.partial(QuietHandler, directory=str(ROOT))
    server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
    Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            executable = os.environ.get('BROWSER_EXECUTABLE')
            chrome = Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
            if not executable and chrome.exists():
                executable = str(chrome)
            browser = p.chromium.launch(headless=True, **({'executable_path': executable} if executable else {}))
            check(browser, f'http://127.0.0.1:{server.server_port}/longbridge-research.html')
            check(browser, (ROOT / 'longbridge-research.html').as_uri(), offline_from_start=True)
            browser.close()
    finally:
        server.shutdown()
        server.server_close()


if __name__ == '__main__':
    main()
