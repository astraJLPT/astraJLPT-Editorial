"""Incremental reader rebuilds preserve one shared stylesheet dependency."""
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'pdf-render/web-tools'))
from shared_styles import ASSET, restore_styles, share_site_styles


class SharedStyles(unittest.TestCase):
    def test_rebuild_after_html_reserialization_keeps_one_stylesheet(self):
        work = ROOT / 'pdf-render/work'
        work.mkdir(exist_ok=True)
        with TemporaryDirectory(dir=work) as directory:
            site = Path(directory)

            def write(name, text):
                path = site / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding='utf-8')

            style = 'margin-inline:1.5rem;padding-block:0.5rem;text-align:center;letter-spacing:0.1em'
            write('papers/test.html', '<html><head></head><body>' +
                  ''.join(f'<p style="{style}">例文{i}</p>' for i in range(4)) + '</body></html>')
            share_site_styles(site, ['papers/test.html'], write)
            original_css = (site / ASSET).read_bytes()
            original = BeautifulSoup((site / 'papers/test.html').read_text(encoding='utf-8'), 'html.parser')
            # rebuild.py reserializes its installed shell with BeautifulSoup.
            for _ in range(2):
                write('papers/test.html', str(BeautifulSoup(
                    (site / 'papers/test.html').read_text(encoding='utf-8'), 'html.parser')))
                share_site_styles(site, ['papers/test.html'], write)
                result = BeautifulSoup((site / 'papers/test.html').read_text(encoding='utf-8'), 'html.parser')
                self.assertEqual(len(result.select('link[rel="stylesheet"]')), 1)
                self.assertEqual(str(result.body), str(original.body))
                self.assertEqual((site / ASSET).read_bytes(), original_css)

    def test_restoration_preserves_other_stylesheet_dependencies(self):
        unrelated = ('<link href="https://example.com/assets/paper-shared.css?v=abcdef" rel="stylesheet"/>'
                     '<link href="../assets/site.css" rel="stylesheet"/>'
                     '<link href="../assets/paper-shared.css?v=abcdef" rel="preload"/>')
        shared = ('<link rel="stylesheet" href="../assets/paper-shared.css?v=abcdef">'
                  '<link href="../assets/paper-shared.css?v=abcdef" rel="stylesheet"/>')
        self.assertEqual(restore_styles(unrelated + shared, {'ps-0': 'text-align:center'}), unrelated)


if __name__ == '__main__':
    unittest.main()
