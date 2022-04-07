# -*- coding: utf-8 -*-
#
# xmind2html
#   Let you paste mindmap(copy from xmind) to anki, with html formate.
#
# v0. rewrite for Anki 2.1 (peixiang.zheng@gmail.com)
#

import sys
import re
import os

from aqt.editor import Editor, EditorWebView
from aqt.qt import QClipboard
from anki.hooks import addHook

ADDON_PATH = os.path.dirname(__file__)
ICONS_PATH = os.path.join(ADDON_PATH, "icons")


##############################################
# Main implementation
##############################################
import sys
import re
re_prefix_table = re.compile(r'^[\t]+')

def makeup(line):
    line = line.replace("★", "<span style=\"color:#F00\">★</span>")
    return line

def read_content(text, add_hightlight=True):
    """从输入输出流读取xmind导出数据，并且对多行的进行合并"""
    lines = []
    for i in text.split("\n"):
        if i.strip() != "":
            lines.append(i)
    max_level = 0
    lines_merge = []
    for index, line in enumerate(lines):
        if add_hightlight:
            line = makeup(line)
        if index != 0 and line[0] != "\t":
            lines_merge[-1] += ("<br>" + line)
        else:
            lines_merge.append(line)
            strip_line = line.lstrip("\t")
            level = len(line) - len(strip_line)
            max_level = max(level, max_level)

    return max_level, lines_merge


def calc_indent(string):
    return len(string) - len(string.lstrip("\t"))


def text_to_html(text):
    max_level, lines = read_content(text)
    ret_html = []
    ret_html.append("""</div><table border= "1" width= "600" >""")
    pattern = """<tr><td width= "25%%" rowspan="%d">%s</td>%s</tr>"""
    for index_i, line_i in enumerate(lines):
        indent_i = calc_indent(line_i)
        not_print = True
        print_line = line_i.lstrip("\t")
        for index_j, line_j in enumerate(lines[index_i + 1:]):
            indent_j = calc_indent(line_j)
            if indent_j <= indent_i:
                not_print = False
                span = index_j + 1
                tail_td = "<td></td>" * (max_level - indent_i) if index_j == 0 else ""
                ret_html.append(pattern % (span, print_line, tail_td))
                break
        span = len(lines) - index_i
        if not_print and index_i + 1 != len(lines):
            tail_td = ""
            ret_html.append(pattern % (span, print_line, tail_td))
        if not_print and index_i + 1 == len(lines):
            tail_td = "<td></td>" * (max_level - indent_i)
            ret_html.append(pattern % (span, print_line, tail_td))
    ret_html.append("</table></div>")
    return "\n".join(ret_html)


def buttonSetup(buttons, editor):
    icon = os.path.join(ICONS_PATH, 'paste.png')
    b = editor.addButton(
        icon=icon, cmd='XmindCopy',
        func=lambda editor: onXmindCopy(editor.web),
        tip='Turn Xmind\'s copy text(table indent outline) to html')
    buttons.append(b)
    return buttons


def onXmindCopy(editor_web_view):
    mode = QClipboard.Clipboard
    clip = editor_web_view.editor.mw.app.clipboard()
    mime = clip.mimeData(mode=mode)
    text = mime.text()
    html = text_to_html(text)
    editor_web_view.editor.doPaste(html, internal=True)


addHook("setupEditorButtons", buttonSetup)
