# -*- coding:utf-8 -*-
import datetime
import json

from mirai import Image, Voice, Startup
from mirai import Mirai, WebSocketAdapter, GroupMessage
from mirai.models import BotInvitedJoinGroupRequestEvent,NewFriendRequestEvent

from run import addManager1

if __name__ == '__main__':
    with open('config.json','r',encoding='utf-8') as fp:
        data=fp.read()
    config=json.loads(data)
    qq=int(config.get('botQQ'))
    key=config.get("vertify_key")
    port= int(config.get("port"))
    bot = Mirai(qq, adapter=WebSocketAdapter(
        verify_key=key, host='localhost', port=port
    ))

    addManager1.main(bot, config)
    bot.run()











    def startVer():
        file_object = open("./mylog.log")
        try:
            all_the_text = file_object.read()
        finally:
            file_object.close()
        print(all_the_text)




    startVer()
    loadUser()
    bot.run()