# coding: utf-8
# Copyright (c) dterazhao. All rights reserved.
from time import sleep
import threading

from bs4 import BeautifulSoup
from flask import Response, stream_with_context
from markdown import markdown
from markdown_it import MarkdownIt
from markupsafe import Markup
from mdit_py_plugins import footnote, front_matter
from wecom_bot_svr.app import web, WecomBotServer, ReqMsg

from common import MarkdownMsg, FileMsg, logger
from config import conf

try:
    from services.agents import generate, generate_, get_query, head_t
except ImportError:
    head_t = ""


    def get_query(query: str):
        return query


    def generate_(query: str, stream=False, converter=None):
        content = f"""### 列表示例
1. 项目绑定资源
   - 无相关业务项目先创建项目
   - 在已有或刚新建项目上绑定资源
2. 注册pulsar数据源
   - 填写基础信息和表字段
"""
        return converter(content) if converter else content


    def generate(query: str, stream=False, converter=None, consumer=None, sleep_t=0.002):
        content = generate_(query, stream, converter)
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


caches = {}


def gen_content(query, stream=False, converter=None):
    if query.startswith("c@"):
        q = get_query(query.lstrip("c@"))
        if q == "all":
            caches.clear()
        else:
            caches.pop(q)

        def gen():
            yield f"{q}相关缓存已经清除"

        content = gen()
    else:
        q = get_query(query)
        if q in caches:
            def gen():
                response = mdt.render(caches[q])
                yield """<!DOCTYPE html><html>{head}<body class="markdown-body">""".format(head=head_t)
                for i in range(len(response)):
                    sleep(0.02)
                    yield f"{response[i]}"
                yield '</body></html>'

            content = gen()
        else:
            def add2caches(c):
                if q not in ["help", "example"]:
                    caches.update({q: c})

            content = generate(q, stream=stream, converter=converter, consumer=add2caches)
    return content


@web.get("/query/<query>")
def q(query=''):
    return Response(stream_with_context(gen_content(query, stream=False, converter=mdt.render)))


@web.get("/stream/query/<query>")
def stream_q(query=''):
    return Response(stream_with_context(gen_content(query, True)))


def query(req_msg: ReqMsg, server: WecomBotServer, msg):
    if msg.strip() not in ["help", "example"]:
        server.send_markdown(req_msg.chat_id, f"点击**[查询流式输出]({conf["out_link"]}/{msg})**可快速获取结果")
    if "wait_result" in conf and conf["wait_result"]:
        content = generate_(msg)
        logger.info(f"len({len(content)})\n{content}")
        if len(content) > max_out_len or is_out_to_file:
            with open(out_fn, 'w') as f:
                f.write(content)
            return FileMsg(out_fn)
        return MarkdownMsg(content)
    else:
        return ""
