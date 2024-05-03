import random
import re

import aiohttp
from bs4 import BeautifulSoup

async def genquestion():
    async with aiohttp.ClientSession() as s:
        s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'})
    async with s.get("https://psycatgames.com/ru/magazine/conversation-starters/questions-for-couples/") as response:
        data = await response.text()
    soup = BeautifulSoup(data, 'html.parser')

    table = soup.findAll("li")
    #print(table)
    output = []

    for row in table:
        if 'href' in str(row):
            continue
        word = re.findall(r'>.+<', str(row))
        word = word[0].replace('>', '')
        word = word.replace('<', '')
        output.append(word)

    return random.choice(output)

async def genword():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'}
    jar = aiohttp.CookieJar()

    async with aiohttp.ClientSession(headers=headers, cookie_jar=jar) as s:
        async with s.get("https://vfrsute.ru/сканворд/слово-из-5-букв/") as response:
            data = await response.text()

    soup = BeautifulSoup(data, 'html.parser')
    table = soup.findAll("li", class_="words_group-item")
    output = []

    for row in table:
        word = re.findall(r'>\w+<', str(row))
        #print(word)
        try:
            word = word[0].replace('>', '')
            word = word.replace('<', '')
            output.append(word)
        except:
            pass
        

    return random.choice(output) if output else None