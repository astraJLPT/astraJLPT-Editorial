"""Standalone exports preserve authored markup and embed rendering dependencies."""
from pathlib import Path
import sys,tempfile,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'pdf-render/web-tools'))
from bs4 import BeautifulSoup
import web_assets as web

class WebAssets(unittest.TestCase):
    def setUp(self):
        work=ROOT/'pdf-render/work';work.mkdir(exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=work);self.addCleanup(self.temp.cleanup)
        self.site=Path(self.temp.name);(self.site/'assets').mkdir();(self.site/'papers').mkdir()
        self.page=self.site/'papers/unit.html'
        self.binding=patch.object(web,'SITE',self.site);self.binding.start();self.addCleanup(self.binding.stop)
        (self.site/'assets/one.css').write_text('p {color:red;background:url("picture.png")}','utf-8')
        (self.site/'assets/two.css').write_text('p {color:blue}','utf-8')
        (self.site/'assets/picture.png').write_bytes(b'fixture-image')
        (self.site/'assets/questions.js').write_text('globalThis.questions=[1,2];','utf-8')
        (self.site/'assets/app.js').write_text('document.querySelector("#answer");','utf-8')
        (self.site/'other.html').write_text('<p>Other</p>','utf-8')

    def test_stylesheet_forms_order_media_and_body_bytes(self):
        body='<!-- authored -->\n<p id="q"><ruby>漢<rt>かん</rt></ruby>  字 &amp; <input id="answer"></p>\n'
        forms=['<link rel="stylesheet" href="../assets/one.css">',"<link href='../assets/one.css' rel='stylesheet'/>",'<LINK media="screen and (min-width: 1px)"\n HREF="../assets/one.css?v=123" REL="stylesheet" />']
        for first in forms:
            markup=first+'<link href="../assets/two.css" rel="stylesheet">'+body
            result=web.inline_resources(markup,self.page);soup=BeautifulSoup(result,'html.parser')
            self.assertEqual(len(soup.select('link[rel="stylesheet"]')),0)
            self.assertEqual(len(soup.select('style')),2)
            self.assertLess(result.index('color:red'),result.index('color:blue'))
            self.assertTrue(result.endswith(body))
            self.assertIn('data:image/png;base64,',result)
            if 'media=' in first:self.assertEqual(soup.style['media'],'screen and (min-width: 1px)')
            self.assertEqual(web.inline_resources(result,self.page),result)

    def test_scripts_keep_order_defer_initialization_and_literal_strings(self):
        literal='<script>const text=\'<link rel="stylesheet" href="missing.css">\';</script>'
        markup=literal+"<script defer='' src='../assets/questions.js' id='question-data'></script><script src='../assets/app.js' defer></script>"
        result=web.inline_resources(markup,self.page)
        self.assertTrue(result.startswith(literal))
        scripts=BeautifulSoup(result,'html.parser').select('script')
        self.assertTrue(all('src' not in s.attrs and 'defer' not in s.attrs for s in scripts))
        self.assertIn('globalThis.questions',scripts[1].get_text())
        self.assertIn("document.addEventListener('DOMContentLoaded'",scripts[2].get_text())

    def test_html_and_svg_images_and_data_uris(self):
        markup="<img alt='kept' src='../assets/picture.png'/><svg><image xlink:href='../assets/picture.png'/></svg><img src='data:image/png;base64,eA=='>"
        result=web.inline_resources(markup,self.page)
        self.assertIn("alt='kept'",result)
        self.assertEqual(result.count('data:image/png;base64,'),3)
        web.assert_embedded_resources(result)

    def test_missing_escaping_and_unhandled_dependencies_fail(self):
        for markup in ['<link rel="stylesheet" href="../assets/missing.css">','<link rel="stylesheet" href="../../outside.css">','<style>@import "missing.css";</style>','<img srcset="missing.png 2x">','<link rel="alternate stylesheet" href="../assets/one.css">']:
            with self.subTest(markup=markup),self.assertRaises((ValueError,FileNotFoundError)):
                web.inline_resources(markup,self.page)

    def test_rebase_changes_actual_links_only_and_keeps_query_fragment(self):
        literal='<script>const sample=\'href="missing.html"\';</script>'
        markup=literal+"<a href='../other.html?q=1&amp;x=2#part'>next</a><a href='#q'>same</a><a href='https://example.com/'>web</a>"
        result=web.rebase_links(markup,self.page,self.site/'export.html')
        self.assertTrue(result.startswith(literal))
        links=BeautifulSoup(result,'html.parser').select('a')
        self.assertEqual(links[0]['href'],'other.html?q=1&x=2#part')
        self.assertEqual(links[1]['href'],'#q')
        self.assertEqual(links[2]['href'],'https://example.com/')

    def test_reader_guard_parses_class_tokens_and_accepts_serialized_shell(self):
        self.page.write_text("<body class='reader-page extra'><link href='../assets/one.css' rel='stylesheet'/><p>本文</p></body>",'utf-8')
        result=web.standalone_html(self.page)
        self.assertIn('<p>本文</p>',result)
        self.assertNotIn('<link',result)
        self.page.write_text('<body class="catalog">not a reader</body>','utf-8')
        with self.assertRaisesRegex(ValueError,'Only generated paper'):web.standalone_html(self.page)

if __name__=='__main__':unittest.main()
