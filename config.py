import importlib
import json
import os

# 场景ID
from spec_line_proc_funcs import hash_proc

# 场景分布的目录，按照顺序来搜索命令处理模块
scene_dirs = ["services", "activities", "public"]

conf = {}
if os.path.exists("config.json"):
    with open("config.json") as f:
        conf = json.load(f)

# 特殊处理函数
special_line_prefix = ([("#", hash_proc.handle_command)] +
                       ([("", getattr(importlib.import_module("services.serv_proc"),
                                      conf["proc_fun"]))] if "proc_fun" in conf else []))

# 企业微信配置
wecom_token = conf["wecom_token"] if "wecom_token" in conf else "xxx"  # 3个x
wecom_aes_key = conf[
    "wecom_aes_key"] if "wecom_aes_key" in conf else "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # 43个x
wecom_corp_id = conf["wecom_corp_id"] if "wecom_corp_id" in conf else ""
wecom_bot_key = conf["wecom_bot_key"] if "wecom_bot_key" in conf else "xxxxx"  # 机器人配置中的webhook key
wecom_bot_name = conf["wecom_bot_name"] if "wecom_bot_name" in conf else "xbot"  # 跟机器人名字一样，用于切分群组聊天中的@消息
wecom_svr_host = conf["wecom_svr_host"] if "wecom_svr_host" in conf else "0.0.0.0"
wecom_svr_port = conf["wecom_svr_port"] if "wecom_svr_port" in conf else 5001
wecom_svr_path = conf["wecom_svr_path"] if "wecom_svr_path" in conf else "/wecom_bot"
timeout = conf["timeout"] if "timeout" in conf else 2
fail_timeout = conf["fail_timeout"] if "fail_timeout" in conf else 10
intranet = conf["intranet"] if "intranet" in conf else False
