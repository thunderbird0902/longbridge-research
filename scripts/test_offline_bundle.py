"""Verify complete, safe and repeatable embedding of the offline library."""
import json
import re
import unittest

from embed_offline import ROOT, embed_report


class OfflineBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = (ROOT / 'longbridge-research.html').read_text(encoding='utf-8')
        cls.payload = re.search(
            r'<script id="offline-pages" type="application/json">(.*?)</script>',
            cls.report, re.S,
        ).group(1)
        cls.pages = json.loads(cls.payload)

    def test_every_local_page_is_embedded_without_changes(self):
        paths = [ROOT / 'longform-library.html', *sorted((ROOT / 'library').glob('*.html'))]
        self.assertEqual(set(self.pages), {p.relative_to(ROOT).as_posix() for p in paths})
        for path in paths:
            self.assertEqual(self.pages[path.relative_to(ROOT).as_posix()], path.read_text(encoding='utf-8'))

    def test_embedded_documents_cannot_end_the_json_script(self):
        self.assertNotIn('<', self.payload)

    def test_regeneration_is_idempotent(self):
        self.assertEqual(self.report, embed_report(self.report))


if __name__ == '__main__':
    unittest.main()
