"""Exercise all cross-author themes, expanded content and sidebar at responsive widths."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as p:
        chrome = Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
        executable = os.environ.get('BROWSER_EXECUTABLE') or (str(chrome) if chrome.exists() else None)
        browser = p.chromium.launch(headless=True, **({'executable_path': executable} if executable else {}))
        page = browser.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto((ROOT / 'longbridge-research.html').as_uri())
        page.add_style_tag(content='html{scroll-behavior:auto!important}')
        for width in [1440, 1024, 850, 768, 390]:
            page.set_viewport_size({'width': width, 'height': 900})
            for number in range(1, 13):
                theme = page.locator(f'#common-v2-{number}')
                page.locator(f'.report-nav a[href="#common-v2-{number}"]').click()
                page.wait_for_timeout(30)
                assert 0 <= theme.bounding_box()['y'] <= 125, (width, number)
                assert page.locator(f'.report-nav a[href="#common-v2-{number}"]').get_attribute('aria-current') == 'location'
                for opened in [False, True]:
                    theme.locator('details').evaluate('(e,value)=>e.open=value', opened)
                    assert theme.evaluate('''e => {
                        const outer=e.getBoundingClientRect();
                        return [...e.querySelectorAll('.theme-head,.common-case,.theme-detail>div,a')]
                          .filter(x=>x.getClientRects().length).every(x=>{
                            const r=x.getBoundingClientRect();
                            return r.left>=outer.left-1 && r.right<=outer.right+1;
                          });
                    }'''), (width, number, opened)
                theme.locator('details').evaluate('(e)=>e.open=false')
                if width > 850:
                    assert page.locator(f'.report-nav a[href="#common-v2-{number}"]').evaluate('''e=>{
                        const r=e.getBoundingClientRect(),n=e.closest('nav').getBoundingClientRect();
                        return r.top>=n.top && r.bottom<=n.bottom;
                    }''')
            assert page.locator('.author-method-card').count() == 14
            assert page.locator('.author-method-grid').evaluate('(e)=>e.scrollWidth<=e.clientWidth+1')
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            print('PASS cross-author layout, all 12 anchors and expanded sections:', width)
        assert not errors, errors
        browser.close()


if __name__ == '__main__':
    main()
