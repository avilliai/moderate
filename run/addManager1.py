# -*- coding:utf-8 -*-
import datetime
import json
import random
import urllib
import urllib.request
from asyncio import sleep

from mirai import Image, Voice, Startup
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain
from mirai.models.events import BotInvitedJoinGroupRequestEvent,NewFriendRequestEvent,MemberJoinRequestEvent,MemberHonorChangeEvent,MemberCardChangeEvent,BotMuteEvent

def main(bot,config):

    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(time + '| 启动成功')
    file = open("Config/banWord.txt", "r")
    js=file.read()
    global banWords
    banWords=json.loads(js)



    global master
    master=int(config.get('master'))
    moderate=config.get("moderate")
    global moderateKey
    moderateKey=moderate.get("key")
    global threshold
    threshold=moderate.get("threshold")
    global configs
    configs=config




    @bot.on(FriendMessage)
    async def quiteG(event:FriendMessage):
        if str(event.message_chain).startswith("退群#") and str(event.sender.id)==str(master):
            dataG=str(event.message_chain).split("#")[1]
            try:
                await bot.quit(int(dataG))
                await bot.send_friend_message(int(master),"已退出: "+str(dataG))
            except:
                print("不正确的群号")

    @bot.on(GroupMessage)
    async def help(event: GroupMessage):
        global banWords
        group=str(event.sender.group.id)
        try:
            banw=banWords.get(group)

            for i in banw:
                if i in str(event.message_chain):
                    id = event.message_chain.message_id
                    try:
                        await bot.recall(id)
                        await bot.send(event,"检测到违禁词"+i+"，撤回")
                    except:
                        print("bot无权限")
        except:
            pass
    @bot.on(GroupMessage)
    async def addBanWord(event:GroupMessage):
        global banWords
        if (event.sender.permission!="MEMBER" or str(event.sender.id)==str(master)) and str(event.message_chain).startswith("/添加违禁词"):
            aimWord=str(event.message_chain)[6:]
            if str(event.sender.group.id) in banWords:
                banw=banWords.get(str(event.sender.group.id))
                banw.append(aimWord)
            else:
                banWords[str(event.sender.group.id)]=[aimWord]

            file = open("Config/banWord.txt", "w")
            js = json.dumps(banWords)
            file.write(js)
            file.close()
            await bot.send(event,"已添加违禁词："+aimWord)
    @bot.on(GroupMessage)
    async def removeBanWord(event:GroupMessage):
        global banWords
        if (event.sender.permission!="MEMBER" or str(event.sender.id)==str(master)) and str(event.message_chain).startswith("/删除违禁词"):
            aimWord=str(event.message_chain)[6:]
            try:
                newData=banWords.get(str(event.sender.group.id)).remove(aimWord)
                banWords[str(event.sender.group.id)]==newData
                file = open("Config/banWord.txt", "w")
                js = json.dumps(banWords)
                file.write(js)
                file.close()
                await bot.send(event,"已移除违禁词："+aimWord)
            except:
                await bot.send(event, "没有已添加的违禁词：" + aimWord)

    @bot.on(GroupMessage)
    async def geturla(event:GroupMessage):
        global moderateKey
        global threshold
        if event.sender.id==1840094972 and event.message_chain.count(Image):
            lst_img = event.message_chain.get(Image)
            img_url = lst_img[0].url
            print(img_url)

            sasda = urllib.request.urlopen(
                "https://api.moderatecontent.com/moderate/?url="+img_url+"&key="+moderateKey).read()
            asf = json.loads(sasda.decode('UTF-8'))
            rate = asf.get('predictions').get('adult')
            print(rate)
            if rate>threshold:
                await bot.recall(event.message_chain.message_id)
                await bot.send(event, "检测到图片违规\npredictions-adult:" + str(rate))
                try:
                    await bot.mute(target=event.sender.group.id, member_id=event.sender.id, time=300)
                except:
                    print("无禁言权限")

    @bot.on(GroupMessage)
    async def setConfiga(event:GroupMessage):
        global configs
        global moderateKey
        global threshold
        if event.sender.id==master:
            if str(event.message_chain).startswith("/阈值"):

                temp=int(str(event.message_chain)[3:])
                if temp>100 or temp<0:
                    await bot.send(event,"设置阈值不合法")
                else:
                    try:
                        threshold=temp
                        configs["moderate"]={"key":moderateKey,"threshold":temp}
                        js=json.dumps(config)
                        with open('config.json', 'w', encoding='utf-8') as fp:
                            fp.write(js)
                        await bot.send(event,"成功修改撤回阈值为"+str(temp))
                    except:
                        await bot.send(event,"阈值设置出错，请进入config.json中手动设置threshold值")
            if str(event.message_chain).startswith("/key"):

                try:
                    key=str(event.message_chain)[4:]


                    moderateKey=key
                    configs["moderate"]={"key":moderateKey,"threshold":threshold}
                    js=json.dumps(config)
                    with open('config.json', 'w', encoding='utf-8') as fp:
                        fp.write(js)
                    await bot.send(event,"成功更新了key")
                except:
                    await bot.send(event,"api-key设置错误，请手动修改config.json中的moderate/key")
