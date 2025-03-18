# coding: utf-8
# Copyright (c) dterazhao. All rights reserved.
from time import sleep

from bs4 import BeautifulSoup
from flask import Response, stream_with_context
from markdown import markdown
from markdown_it import MarkdownIt
from markupsafe import Markup
from mdit_py_plugins import footnote, front_matter
from wecom_bot_svr.app import web

from common import MarkdownMsg, FileMsg, logger
from config import conf

try:
    from services.agents import generate
except ImportError:
    def generate(query: str, stream=False, converter=None, sleep_t=0.002):
        content = f"""### 列表示例
1. 项目绑定资源
   - 无相关业务项目先创建项目
   - 在已有或刚新建项目上绑定资源
2. 注册pulsar数据源
   - 填写基础信息和表字段
"""
        content = converter(content) if converter else content
        for i in range(len(content)):
            sleep(sleep_t)
            yield f"{content[i]}"

max_out_len = conf["max_out_len"] if "max_out_len" in conf else 500
out_fn = conf["out_fn"] if "out_fn" in conf else "output.md"
is_out_to_file = conf["is_out_to_file"] if "is_out_to_file" in conf else False

exts = ['fenced_code', 'tables', 'toc']

mdt = (
    MarkdownIt('commonmark')
    .use(front_matter.front_matter_plugin)
    .use(footnote.footnote_plugin)
    .enable('table')
)


def md2html(md):
    html = markdown(md.replace('- ', '\n▪ '), extensions=exts)
    html = html.replace('<code>', '<pre>').replace('</code>', '</pre>')
    soup = BeautifulSoup(html, 'html.parser')
    for table in soup.find_all('table'):
        table['class'] = 'table table-bordered table-striped table-condensed table-hover table-responsive table-dark'
    html = Markup(str(soup))
    return html


@web.get("/query/<query>")
def q(query=''):
    return Response(stream_with_context(generate(query, stream=False, converter=mdt.render)))


@web.get("/stream/query/<query>")
def stream_q(query=''):
    return Response(stream_with_context(generate(query, stream=True)))


def query(user_id, msg, chat_id=None):
    content = "".join(i for i in generate(msg))
    if "```" not in content:
        content = f"```markdown{content}```"
    logger.info(f"len({len(content)})\n{content}")
    if len(content) > max_out_len or is_out_to_file:
        with open(out_fn, 'w') as f:
            f.write(content)
        return FileMsg(out_fn)
    return MarkdownMsg(content)
