import nonebot
from nonebot.adapters.cqhttp import Bot as CQHTTPBot

nonebot.init()
driver = nonebot.get_driver()
driver.register_adapter("cqhttp", CQHTTPBot)

app = nonebot.get_asgi()

nonebot.load_builtin_plugins()
nonebot.load_plugin("christinaqqbot.plugins.pixiv")
nonebot.load_plugin("christinaqqbot.plugins.poke")
nonebot.load_plugin("christinaqqbot.plugins.waifu")
nonebot.load_plugin("christinaqqbot.plugins.Rss")
nonebot.load_plugin("christinaqqbot.plugins.mcping")

if __name__ == "__main__":
    nonebot.run(app="bot:app")
