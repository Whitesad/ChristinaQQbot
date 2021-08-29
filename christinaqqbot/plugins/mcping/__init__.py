import json
import nonebot
from nonebot import on_command
from nonebot.adapters.cqhttp import Bot,Event

from nonebot.rule import to_me

from christinaqqbot.utils.rule import  _gruop_white_list

from .util import MinecraftPing

mcping=on_command('mcping',rule=to_me()&_gruop_white_list)

@mcping.handle()
async def handle_ping(bot: Bot, event: Event, state: dict):
    mc_ping_dict=nonebot.get_driver().config.mcping
    for group in mc_ping_dict:
        if(mc_ping_dict[group][0]==event.group_id):
            host=mc_ping_dict[group][1]
            server = MinecraftPing(host,25565)
            success, error = server.ping()
            if(success):
                reply=('server:'+server.host+'\r\n'
                +'status:🟢\r\n'
                +'player:'+str(server.player_count)+'/'+str(server.player_limit)+'\r\n'
                +'player list:\r\n'
                )
                for user in server.players:
                    reply=reply+str(user)+'\r\n'
                reply=reply[:-2]
                
            else:
                reply='server:'+server.host+'\r\n'
                +'status:🔴'
            await mcping.finish(reply)