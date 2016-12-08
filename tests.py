#!/usr/bin/python3

import unittest
from functools import partial
from utils import MAN2HTML


M2HO = MAN2HTML()
M2H = partial(M2HO.man2html_base, record_all=True)


class TestMan2Html(unittest.TestCase):
    def test_links(self):
        self.assertEqual(M2HO.global_ref_selection('test http://google.com/ '
                                                   '123'),
                         ('test <a href="http://google.com/">http://google'
                          '.com/</a> 123'))
        self.assertEqual(M2HO.global_ref_selection('test admin@localhost.ru '
                                                   '123'),
                         ('test <a href="mailto:admin@localhost.ru">'
                          'admin@localhost.ru</a> 123'))
        self.assertEqual(M2HO.local_ref_selection('bash(1)'),
                         '<a href="bash#1">bash</a>(1)')
        self.assertEqual(M2HO.local_ref_selection('gcc(12)'),
                         '<a href="gcc#12">gcc</a>(12)')

    def test_bold_single_line(self):
        self.assertEqual(M2H(['.B ls']), '<b>ls</b>')

    def test_italic_single_line(self):
        self.assertEqual(M2H(['.I ls']), '<i>ls</i>')

    def test_bold_multiple_line(self):
        self.assertEqual(M2H([r'123\fBls\fR']), '123<b>ls</b>')
        self.assertEqual(M2H([r'123\fBls\fP']), '123<b>ls</b>')

    def test_italic_multiple_line(self):
        self.assertEqual(M2H([r'123\fBls \fIls\fR\fR']),
                         '123<b>ls <i>ls</i></b>')

    def test_paragraph(self):
        self.assertEqual(M2H(['test', '.nf', '123321', '.fi', 'test'])
                         .replace('\n', ''),
                         'test<p>123321</p>test')

    def test_header_starting(self):
        self.assertEqual(M2H(['.SH "REPORTING BUGS"']).replace('\n', ''),
                         ('</div><h2 id="header-2">REPORTING BUGS</h2>'
                          '<div style="padding-left: 3em;">'))

    def test_padding(self):
        self.assertEqual(M2H(['.RS 4', '123', '.RE']).replace('\n', ''),
                         '<div style="padding-left: 4em;">123</div>')
        self.assertEqual(M2H(['.RS', '123', '.RE']).replace('\n', ''),
                         '<div style="padding-left: 1em;">123</div>')

    def test_pre(self):
        self.assertEqual(M2H(['.Vb 1', '123', '.Ve']).replace('\n', ''),
                         '<pre>123</pre>')

    def test_title(self):
        self.assertEqual(M2HO.man2html(['.TH GCC 1 "2015-04-26" '
                                        '"gcc-4.8" "GNU"']).replace('\n', ''),
                         ('<html>  <head>    <meta charset="utf-8" />'
                          '    <style>      * {        '
                          'font-size: 10pt;      }      .left-block {        '
                          'width: 33%;        float: left;        '
                          'text-align: left;      }      .center-block {'
                          '        width: 33%;        float: left;        '
                          'text-align: center;      }      .right-block {'
                          '        width: 33%;        float: left;        '
                          'text-align: right;      }      i {        '
                          'color: #f99;      }      ul {        '
                          'list-style-type: none;      }    </style>  '
                          '</head>  <body>    <span><div><h1 '
                          'class="left-block">GCC (1)</h1><h1 class="'
                          'center-block">General Commands Manual</h1><h1 '
                          'class="right-block">GCC (1)</h1></div><div '
                          'class="contents"><ul><li><a href="#header-1">'
                          'Exit status:</a></li></ul><li><a href="#header-2">'
                          'REPORTING BUGS</a></li></ul></div></div></span>'
                          '<div><h1 class="left-block">gcc-4.8</h1>'
                          '<h1 class="center-block">2015-04-26</h1>'
                          '<h1 class="right-block">GCC (1)</h1></div>    '
                          '</span>  </body></html>'))

    def test_SS(self):
        self.assertEqual(M2H(['.SS "Exit status:"']).replace('\n', ''),
                         ('</div><br /><h3 id="header-1">Exit status:</h2>'
                          '<div style="padding-left: 3em;">'))

    def test_IP(self):
        self.assertEqual(M2H(['.IP "HEADER" 2', 'test', '123'])
                         .replace('\n', ''),
                         ('<h4 style="display:inline;">HEADER</h4><div '
                          'style="padding-left: 0em;display:inline;">test123'))

    def test_special_chars(self):
        self.assertEqual(M2H([r'a\(cob']).replace('\n', ''), 'a©b')
        self.assertEqual(M2H([r'a\eb']).replace('\n', ''), 'a\\b')
        self.assertEqual(M2H([r'a\(aqb']).replace('\n', ''), "a'b")

    def test_linebreaks(self):
        self.assertEqual(M2H(['a', '.P', 'b']).replace('\n', ''), 'a<br />b')
        self.assertEqual(M2H(['a', '.Sp', 'b']).replace('\n', ''), 'a<br />b')
        self.assertEqual(M2H(['a', '.TP', 'b']).replace('\n', ''), 'a<br />b')
        self.assertEqual(M2H(['a', '.br', 'b']).replace('\n', ''), 'a<br />b')
        self.assertEqual(M2H(['a', '.PP', 'b']).replace('\n', ''), 'a<br />b')


if __name__ == '__main__':
    unittest.main()
