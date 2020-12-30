#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nonebot
from nonebot.adapters.cqhttp import Bot as CQHTTPBot
# Custom your logger
# 
# from nonebot.log import logger, default_format
# logger.add("error.log",
#            rotation="00:00",
#            diagnose=False,
#            level="ERROR",
#            format=default_format)

# You can pass some keyword args config to init function
nonebot.init()
driver = nonebot.get_driver()
driver.register_adapter("cqhttp", CQHTTPBot)

app = nonebot.get_asgi()

nonebot.load_builtin_plugins()
nonebot.load_plugin("christinaqqbot.plugins.pixiv")
nonebot.load_plugin("christinaqqbot.plugins.poke")
nonebot.load_plugin("christinaqqbot.plugins.waifu")
nonebot.load_plugin("christinaqqbot.plugins.Rss")
# nonebot.load_plugin("christinaqqbot.plugins.QQcmd")

# Modify some config / config depends on loaded configs
# 
# config = nonebot.get_driver().config
# do something...


if __name__ == "__main__":
    nonebot.run(app="bot:app")
