from wecom_bot_svr.app import web

from common import MarkdownMsg
from config import conf

max_out_len = conf["max_out_len"] if "max_out_len" in conf else 500
out_fn = conf["out_fn"] if "out_fn" in conf else "output.md"
is_out_to_file = conf["is_out_to_file"] if "is_out_to_file" in conf else False


@web.get("/hello")
def hello():
    return "<p>Hello, World!</p>"


def query(user_id, msg, chat_id=None):
    content = "## help"
    return MarkdownMsg(content)
