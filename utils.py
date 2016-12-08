import re
import shlex
from collections import namedtuple


def _compare(item):
    return -len(item[0])

Info = namedtuple('Info', ['name', 'num', 'date', 'ver'])
Heading = namedtuple('Heading', ['name', 'title', 'level'])


class MAN2HTML(object):
    DEFAULT_FONT_SIZE = 10

    HEADER = '''
<html>
  <head>
    <meta charset="utf-8" />
    <style>
      * {{
        font-size: 10pt;
      }}
      .left-block {{
        width: 33%;
        float: left;
        text-align: left;
      }}
      .center-block {{
        width: 33%;
        float: left;
        text-align: center;
      }}
      .right-block {{
        width: 33%;
        float: left;
        text-align: right;
      }}
      i {{
        color: #f99;
      }}
      ul {{
        list-style-type: none;
      }}
{}
    </style>
  </head>
  <body>
    <span>
'''
    FOOTER = '''
    </span>
  </body>
</html>
'''

    def _start_paragraph(self, data):
        closing = '</div><br />' if self.level3_open else ''
        self.level3_open = True
        parts = re.search(r'"(.*)" (\d+)', data)
        inline_style = 'display:block;'
        if parts is None:
            part1, part2 = '', ''
        else:
            part1, part2 = parts.group(1), parts.group(2)
            if (part1[-1] == '.' and part1[:-1].isnumeric()) or \
               len(part1[-1]) == 1:
                inline_style = 'display:inline;'
                part2 = 0
        return '{}<h4 style="{}">{}</h4><div ' \
               'style="padding-left: {}em;{}">'\
            .format(closing, inline_style, part1, part2, inline_style)

    def _start_subheader(self, data):
        closing = '</div><br />' if self.level3_open else ''
        closing += '</div>' if self.level2_open else ''
        self.level3_open = False
        self.level2_open = True
        parts = re.search(r'"(.*)"', data)
        if parts is None:
            result = data.split(' ', 2)[1]
        else:
            result = parts.group(1)
        return '{}<h3 id="{}">{}</h2><div style="padding-left: 3em;">'\
            .format(closing, self.get_header_name(result, 2), result)

    def _start_header(self, data):
        closing = '</div><br />' if self.level3_open else ''
        closing += '</div>' if self.level2_open else ''
        closing += '</div>' if self.level1_open else ''
        self.level3_open = False
        self.level2_open = False
        self.level1_open = True
        parts = re.search(r'"(.*)"', data)
        if parts is None:
            result = data.split(' ', 1)[1]
        else:
            result = parts.group(1)
        return '{}<h2 id="{}">{}</h2><div style="padding-left: 3em;">'\
            .format(closing, self.get_header_name(result, 1), result)

    def _pad_right(self, length):
        try:
            length = int(length.strip())
        except:
            length = 1
        return '<div style="padding-left: {}em;">'.format(length)

    def _pad_left(self, data):
        return '</div>'

    def _start_pre(self, data):
        self._pre_open = True
        return '<pre>'

    def _finish_pre(self, data):
        self._pre_open = False
        return '</pre>'

    def _main_title(self, data):
        self.recording = True
        data_items = shlex.split(data)[:4]
        while len(data_items) < 4:
            data_items.append('')
        self.info = Info(*data_items)
        header1 = '{} ({})'.format(self.info.name, self.info.num)
        header2 = 'General Commands Manual'
        self._page_title = '<div><h1 class="left-block">{0}</h1>' \
                           '<h1 class="center-block">{1}</h1>' \
                           '<h1 class="right-block">{0}</h1></div>'\
            .format(header1, header2)
        return ''

    def _main_footer(self):
        header1 = '{} ({})'.format(self.info.name, self.info.num)
        return '<div><h1 class="left-block">{0}</h1><h1 class="center-' \
               'block">{1}</h1><h1 class="right-block">{2}</h1></div>'\
            .format(self.info.ver, self.info.date, header1)

    def _start_title(self, data):
        self.recording = True
        return r'<h1 class="TH">{}</h1>'.format(data)

    FONT_CHANGING_TAGS = [
        re.compile(r'\\s(\+|\-)?(\d+)'),
    ]
    FONT_CHANGING_OPEN = '</span><span style="font-size:{}pt;">'
    LOCAL_REF_RE1 = re.compile(r'(?<=<i>)([A-Za-z0-9-]*?)</i>\((\d+)\)')
    LOCAL_REF_RE2 = re.compile(r'(?<=<b>)([A-Za-z0-9-]*?)</b>\((\d+)\)')
    LOCAL_REF_RE3 = re.compile(r'([A-Za-z0-9-]*?)\((\d+)\)')

    GLOBAL_REF_RE = re.compile(r'(https?://|ftp://|file:///)([A-Z0-9\-~]+'
                               r'\.?/?)+', re.IGNORECASE)
    MAILTO_REF_RE = re.compile(r'([a-z0-9_\.-]+)@([\da-z\.-]+)'
                               r'\.([a-z\.]{2,6})', re.IGNORECASE)

    def __init__(self):
        self._pre_open = False
        self.level1_open = False
        self.level2_open = False
        self.level3_open = False
        self.list_open = False
        self.info = None
        self.recording = False
        self.closing_tags = []
        self.current_font_size = self.DEFAULT_FONT_SIZE
        self._header_id = 0
        self._headers = []
        self._page_title = ''

        self.INLINE_FUNCTIONS = {
            r'.IP': self._start_paragraph,
            r'.SH': self._start_header,
            r'.Sh': self._start_header,
            r'.RS': self._pad_right,
            r'.RE': self._pad_left,
            r'.SS': self._start_subheader,
            r'.Vb': self._start_pre,
            r'.Ve': self._finish_pre,
            r'.TH': self._main_title,
            r'.Dt': self._start_title,
        }
        self.INLINE_TAGS = sorted({
            r'.de': r'',
            r'.ds': r'',
            r'.nr': r'',
            r'.}f': r'',
            r'.ll': r'',
            r'.in': r'',
            r'.ti': r'',
            r'.el': r'',
            r'.ie': r'',
            r'..': r'',
            r'.if': r'',
            r'.nh': r'',
            r'.zY': r'',
            r'.LP': r'<br />',
            r'.IB': r'<b><i>{}</i></b>',
            '.FN': '<i>{}</i>',
            r'.SM': r'<span style="font-size: 9pt;"></span>',
            r'.RB': r'<b>{}</b>',
            r'.PD': r'<!--{}-->',
            r'.\"': r'<!--{}-->',
            r'.B': r'<b>{}</b>',
            r'\.B': r'<b>{}</b>',
            r'.BR': r'<b>{}</b>',
            r'.I': r'<i>{}</i>',
            r'.IR': r'<i>{}</i>',
            r'.PP': r'<br />',
            r'.P': r'<br />',
            r'.TP': r'<br />',
            r'.br': r'<br />',
            r'.IX ': r'</div><div style="padding-left: 4em;">',
            r'\&': r'<span style="margin-right: 1em">{}</span>',
        }.items(), key=_compare)
        self.TEXT_PART_TAGS = {
            r'\fB': r'<b>',
            r'\f(BI': r'<span class=BI">',
            r'\f(IB': r'<span class=IB">',
            r'\f(CW': r'<span class="CW">',
            r'\f(CI': r'<span class="CI">',
            r'\f(CB': r'<span class="CB">',
            r'\fI': r'<i>',
        }
        self.CLOSING_TAGS = {
            r'\fB': r'</b>',
            r'\f(BI': r'</span>',
            r'\f(IB': r'</span>',
            r'\f(CW': r'</span>',
            r'\f(CI': r'</span>',
            r'\f(CB': r'</span>',
            r'\fI': r'</i>',
        }
        self.CLOSING_TAG_VARIANTS = [r'\fR']
        self.CLOSING_ALL_TAG_VARIANTS = [r'\fP']
        self.NOT_CLOSING_PART_TAGS = sorted({
            r'\(dq': '"',
            r'\(bv': r'|',
            r'.zZ': r'',
            r'\\$1': r'',
            r'\*(L"': '"',
            r'\*(R"': '"',
            r'.nf': r'<p>',
            r'.fi': r'</p>',
            r'\(co': r'©',
            r'.Os': '',
            r'\|': r'',
            r'\`': '`',
            r'("': r'"',
            r'\-': r'-',
            r'.Sp': r'<br />',
            r'C`': r'"',
            r"C'": r'"',
            r'\*(': r'',
            r'\|_': r'_',
            # r'\(bu': r'<b>.</b>',
            r'\fB\f(BI': r'<span class="BI">',
            r'\fB\f(CB': r'<span class="CB">',
            r'\fB\fR': r'</span>',
            r'\e': '\\',
            r'\(aq': "'",
            r'\(bu': '\u2022',
        }.items(), key=_compare)

    @property
    def header_id(self):
        self._header_id += 1
        return self._header_id

    def get_header_name(self, title, level):
        name = 'header-{}'.format(self.header_id)
        self._headers.append(Heading(name, title, level))
        return name

    def get_contents(self):
        result = '<div class="contents">'
        for i in range(len(self._headers)):
            if i == 0 or self._headers[i].level > self._headers[i - 1].level:
                result += '<ul>'
            if self._headers[i].level < self._headers[i - 1].level:
                result += '</ul>'
            result += '<li><a href="#{}">{}</a></li>'\
                .format(self._headers[i].name, self._headers[i].title)
        result += '</ul></div>'
        return result

    def local_ref_selection(self, line):
        line = re.sub(self.LOCAL_REF_RE1,
                      r'<a href="\g<1>#\g<2>">\g<1></a></i>(\g<2>)', line)
        line = re.sub(self.LOCAL_REF_RE2,
                      r'<a href="\g<1>#\g<2>">\g<1></a></b>(\g<2>)', line)
        return re.sub(self.LOCAL_REF_RE3,
                      r'<a href="\g<1>#\g<2>">\g<1></a>(\g<2>)', line)

    def global_ref_selection(self, line):
        line = re.sub(self.GLOBAL_REF_RE, r'<a href="\g<0>">\g<0></a>', line)
        return re.sub(self.MAILTO_REF_RE, r'<a href="mailto:\g<0>">\g<0></a>',
                      line)

    def update_font(self, positions):
        if positions.group(2) == '0':
            self.current_font_size = self.DEFAULT_FONT_SIZE
        else:
            self.current_font_size += int(positions.group(1) +
                                          positions.group(2))

    def change_font(self, line):
        while True:
            replace_data = ''
            replace_position = len(line)
            best_positions = None
            for tag in self.FONT_CHANGING_TAGS:
                positions = re.search(tag, line)
                if positions is None:
                    continue
                replace_group = positions.group(0)
                if line.index(replace_group) < replace_position:
                    best_positions = positions
                    replace_position = line.index(replace_group)
                    replace_data = replace_group
            if not replace_data:
                return line
            self.update_font(best_positions)
            line = line.replace(replace_data,
                                self.FONT_CHANGING_OPEN.format(
                                    self.current_font_size), 1)
        return line

    def apply_part_tags_once(self, line):
        min_pos, current_tag = len(line), ''

        for tag in self.TEXT_PART_TAGS:
            if tag in line:
                if line.index(tag) < min_pos:
                    min_pos = line.index(tag)
                    current_tag = tag

        for tag in self.CLOSING_ALL_TAG_VARIANTS:
            if tag in line and line.index(tag) < min_pos:
                result = ''
                while self.closing_tags:
                    result += self.closing_tags.pop(-1)
                return line.replace(tag, result, 1)

        for CLOSING_TAG in self.CLOSING_TAG_VARIANTS:
            if CLOSING_TAG in line and line.index(CLOSING_TAG) < min_pos:
                if len(self.closing_tags) > 0:
                    result = self.closing_tags.pop(-1)
                else:
                    result = '</.....>'
                return line.replace(CLOSING_TAG, result, 1)

        if not current_tag:
            return line

        if len(self.closing_tags) > 0 and \
           self.closing_tags[-1] == self.CLOSING_TAGS[current_tag] and \
           self.closing_tags[-1] == '</i>':
            return line.replace(current_tag, '', 1)

        self.closing_tags.append(self.CLOSING_TAGS[current_tag])
        return line.replace(current_tag, self.TEXT_PART_TAGS[current_tag], 1)

    def apply_not_closing_tags(self, line):
        for tag, result in self.NOT_CLOSING_PART_TAGS:
            line = line.replace(tag, result)
        return line

    def apply_part_tags(self, line):
        while True:
            new_line = self.apply_part_tags_once(line)
            if line == new_line:
                break
            line = new_line
        return line

    def modify_line(self, line):
        line = line.strip()
        line = self.apply_not_closing_tags(line)
        line = self.apply_part_tags(line)
        line = self.change_font(line)
        for tag, func in self.INLINE_FUNCTIONS.items():
            if line.startswith(tag):
                line = func(line[len(tag):])
        for tag, result in self.INLINE_TAGS:
            if line.startswith(tag):
                line = result.format(line[len(tag):].strip())
        if not self._pre_open:
            line = self.local_ref_selection(line)
            line = self.global_ref_selection(line)
        return line

    def man2html_base(self, text_lines, record_all=False):
        result_lines = []
        for line in text_lines:
            line = line.replace('<', '&lt;').replace('>', '&gt;')
            new_line = self.modify_line(line)
            if self.recording or record_all:
                result_lines.append(new_line)
        return '\n'.join(result_lines)

    def man2html(self, text_lines, styles=''):
        data = self.man2html_base(text_lines)
        beginning = self.HEADER.format(styles) + self._page_title + \
            self.get_contents() + data
        return beginning + '</div></span>' + self._main_footer() + self.FOOTER
