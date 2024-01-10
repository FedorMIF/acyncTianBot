import re

async def add(text):
    import time
    import aiofiles
    t = time.localtime()
    time_day = time.strftime("%d.%m - %H:%M:%S", t)
    async with aiofiles.open('log.txt', 'a') as file_log:
        await file_log.write(str(time_day) +' : ' + text + '\n')
    

async def time():
    import time
    t = time.localtime()
    current_time = time.strftime("%c", t)
    return str(current_time)


async def bro_list():
    import aiofiles
    bros = []
    async with aiofiles.open('bro.txt', 'r') as file_bro:
        async for st in file_bro:
            st = re.sub(r'\n', '', str(st))
            bros.append(int(st))
        return bros


async def kis_list():
    import aiofiles
    kis = []
    async with aiofiles.open('kis.txt', 'r') as file_bro:
        async for st in file_bro:
            st = re.sub(r'\n', '', str(st))
            kis.append(int(st))
        return kis


async def to_bro_list(bro_id):
    with open('bro.txt', 'a') as f:
        f.write('\n' + bro_id)


async def to_kis_list(kis_id):
    with open('kis.txt', 'a') as f:
        f.write('\n' + kis_id)


async def get_file():
    print("Я тут")
    return open('log.txt', 'r', encoding='Windows-1251')
