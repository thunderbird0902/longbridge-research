"""Regression checks for the report's two-column layout and navigation."""
import unittest

from build_pages import ReportStructure


class ReportStructureTests(unittest.TestCase):
    def validate(self, markup):
        parser = ReportStructure()
        parser.feed(markup)
        return parser.validate()

    def test_sections_remain_inside_content_column(self):
        self.assertEqual([], self.validate(
            '<main><nav><a href="#cases">案例</a></nav>'
            '<div class="report-content"><section id="cases">'
            '<input/><article data-case-detail="memory"></article>'
            '<button data-case-id="memory"></button></section></div></main>'
        ))

    def test_early_container_close_is_rejected(self):
        errors = self.validate(
            '<main><nav></nav><div class="report-content">'
            '<section id="authors"></div></section>'
            '<section id="cases"></section></div></main>'
        )
        self.assertTrue(any('Mismatched closing' in error for error in errors))

    def test_well_formed_sections_cannot_escape_column(self):
        errors = self.validate(
            '<main><nav></nav><div class="report-content"></div>'
            '<section id="cases"></section></main>'
        )
        self.assertTrue(any('escaped' in error for error in errors))

    def test_missing_targets_and_duplicate_ids_are_rejected(self):
        errors = self.validate(
            '<div id="same"></div><div id="same"></div>'
            '<a href="#missing">Link</a><button data-open-case="removed"></button>'
        )
        self.assertEqual(set(errors), {
            'Duplicate id: same', 'Missing anchor: missing', 'Missing case: removed',
        })


if __name__ == '__main__':
    unittest.main()
