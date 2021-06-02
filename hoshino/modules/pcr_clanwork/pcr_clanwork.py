from hoshino import Service, R, priv
from hoshino.typing import CQEvent
import aiohttp, os

help = '''[上传作业 boss 图片]
boss：指几周目几王
a1(指一周目一王)
b5-1(指二周目五王非狂暴)
b5-2(指二周目五王狂暴)
如果五王无狂暴，请输入boss b5，以此类推

[查作业 boss]
boss：与上传指令相同

[删作业 boss num]
boss：与上传指令相同
num：指第几个作业，使用查作业指令获取数字

注：为防止乱用，除查作业指令以外，其它指令仅限于管理员使用
'''

sv = Service('pcr_work', enable_on_default=True, visible=True, help_=help)

BOSS = ['a1','a2','a3','a4','a5','a5-1','a5-2','b1','b2','b3','b4','b5','b5-1','b5-2','c1','c2','c3','c4','c5','c5-1','c5-2']

class clanwork():
    def __init__(self):
        self.state = {}

    def makedir(self, gid):
        for item in BOSS:
            RES = R.img(f'clanwork/{gid}/' + item)
            if not os.path.exists(RES.path):
                os.makedirs(RES.path)
            self.state[item] = len(os.listdir(RES.path)) // 2
        return self.state

cw = clanwork()

def get_list_num(gid, bossnum):
    workpath = R.img(f'clanwork/{gid}/{bossnum}').path
    files = next(os.walk(workpath))[2]
    worklist = os.listdir(workpath)
    worklist.sort(key = lambda x: int(x[:-4]))
    name = 1
    for file in worklist:
        if int(file[:-4]) != name:
            break
        else:
            name += 1
    return workpath, len(files), name

async def download(url, gid, bossnum):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as req:
                workpath, num, name = get_list_num(gid, bossnum)
                chunk = await req.read()
                open(os.path.join(f'{workpath}/{name}.png'), 'wb').write(chunk)
                return True
    except Exception as e:
        print(e)
        return False

@sv.on_prefix('上传作业')
async def upload(bot, ev:CQEvent):
    gid = ev.group_id
    msg = ev.message
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '仅限管理员上传作业', at_sender=True)
    if not os.path.exists(R.img(f'clanwork/{gid}').path):
        cw.makedir(gid)
    if len(msg) != 2:
        await bot.finish(ev, '参数错误', at_sender=True)
    elif msg[0]['type'] == 'text' and msg[0]['data']['text'].strip().lower() in BOSS:
        if msg[1]['type'] == 'image':
            url = msg[1]['data']['url']
            if not await download(url, gid, msg[0]['data']['text'].strip().lower()):
                await bot.finish(ev, '上传失败')
        else:
            await bot.finish(ev, '请携带图片', at_sender=True)
    else:
        await bot.finish(ev, '请输入正确的boss', at_sender=True)
    await bot.send(ev, '上传完毕')
    
@sv.on_prefix('查作业')
async def qwork(bot, ev:CQEvent):
    img = []
    gid = ev.group_id
    work = ev.message.extract_plain_text().strip().lower()
    cpath = R.img(f'clanwork/{gid}/{work}').path
    num = get_list_num(gid, work)[1]
    if num == 0:
        await bot.finish(ev, f'没有找到{work}的作业')
    for file in os.listdir(cpath):
        fnum = file[:-4]
        img.append(f'{fnum}：[CQ:image,file=file:///{cpath}/{file}]\n')
    msg = ''.join(img)
    await bot.send(ev, f'已找到{num}份{work}作业：\n{msg}', at_sender=True)

@sv.on_prefix('删作业')
async def dwork(bot, ev:CQEvent):
    gid = ev.group_id
    work = ev.message.extract_plain_text().split()
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '请联系群管理删除作业', at_sender=True)
    bossnum = work[0]
    listnum = work[1]
    path = R.img(f'clanwork/{gid}/{bossnum}/{listnum}.png').path
    os.remove(path)
    await bot.send(ev, f'已删除{bossnum}第{listnum}个作业', at_sender=True)
    
@sv.on_fullmatch('作业数量')
async def queryallwork(bot, ev:CQEvent):
    gid = ev.group_id   
    num = 0
    for work in BOSS:
        list = get_list_num(gid, work)
        num += list[1]
    await bot.send(ev, f'目前作业数量总计{num}份', at_sender=True)

@sv.on_fullmatch('删除所有作业')
async def delallwork(bot, ev:CQEvent):
    gid = ev.group_id
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.finish(ev, '请联系超管删除作业', at_sender=True)
    path = R.img(f'clanwork/{gid}').path
    num = 0
    for dir in os.listdir(path):
        dirpath = R.img(f'{path}/{dir}').path
        for file in os.listdir(dirpath):
            filepath = R.img(f'{dirpath}/{file}').path
            os.remove(filepath)
            num += 1

    await bot.send(ev, f'已删除所有作业，共计{num}份', at_sender=True)
