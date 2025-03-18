import random
import time

from wecom_bot_svr.app import WecomBotServer, ReqMsg


def handle_command(req_msg: ReqMsg, server: WecomBotServer, msg):
    # TODO: Implement line starting with '#' handling"
    random_number = random.choice([0, 1, 2])
    if random_number == 0:
        time.sleep(3)
        return "Return after 3 seconds"
    elif random_number == 1:
        time.sleep(7)
        return "Return after 7 seconds"
    else:
        return "Return immediately"
