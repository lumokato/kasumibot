# coding=utf-8
from bs4 import BeautifulSoup
import urllib.request
import urllib.error
import urllib.parse
import json
import time

baseurl = "https://ak-data-2.sapk.ch/api/v2/pl4"


def getURL(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
    }
    try:
        response = urllib.request.Request(url=url, headers=headers, method="GET")
        req = urllib.request.urlopen(response)
        info = str(BeautifulSoup(req.read().decode('utf-8'), "html.parser"))
    except urllib.error.URLError as e:
        return e
    return info

def getID(nickname):#获取牌谱屋角色ID
    nickname = urllib.parse.quote(nickname) #UrlEncode转换
    url = baseurl + "/search_player/"+nickname+"?limit=9"
    data = json.loads(getURL(url))
    if data == [] :
        return -1
    return data


def selectLevel(room_level):
    level_list = []
    if room_level == "0":
        level_list.append("16.12.9")#所有南场信息
        level_list.append("15.11.8")#所有东场信息
    elif room_level == "1":
        level_list.append("9")#金南
        level_list.append("8")#金东
    elif room_level == "2":
        level_list.append("12")#玉南
        level_list.append("11")#玉东
    elif room_level == "3":
        level_list.append("16")#王座南
        level_list.append("15")#王座东
    return level_list


def selectInfo(id,room_level): #信息查询
    localtime = time.time()
    urltime = str(int(localtime*1000)) #时间戳
    basicurl = baseurl+"/player_stats/"+str(id)+"/1262304000000/"+urltime+"?mode="
    extendurl = baseurl+"/player_extended_stats/"+str(id)+"/1262304000000/"+urltime+"?mode="
    data_list = []
    level_list = selectLevel(room_level)
    for i in range(0,2):
        data_list.append(getURL(basicurl + level_list[i]))
        data_list.append(getURL(extendurl + level_list[i]))
    return data_list

def selectRecond(id):
    localtime = time.time()
    urltime = str(int(localtime * 1000))  # 时间戳
    basicurl = baseurl + "/player_stats/" + str(id) + "/1262304000000/" + urltime + "?mode=16.12.9.15.11.8"
    count = str(json.loads(getURL(basicurl))["count"])
    recondurl = baseurl + "/player_records/"+str(id)+"/"+urltime+"/1262304000000?limit=5&mode=16.12.9.15.11.8&descending=true&tag="+count
    recond = getURL(recondurl)
    return recond
