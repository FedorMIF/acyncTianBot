import random
import re
import aiohttp
from urllib.request import urlopen
from bs4 import BeautifulSoup
import asyncio

async def fetch_html(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

async def get_taro():
    """Parse images from a given URL."""
    url = "https://vedovstvo.by/galereya-taro-rajdera-uejta/"
    html = await fetch_html(url)
    soup = BeautifulSoup(html, 'html.parser')
    images = []
    for div in soup.find_all("div", class_="col-md-3"):
        img = div.find("img")
        #print(img)
        if img and img.get("src") and img.get("alt"):
            images.append([img["src"], img["alt"]])


    #img = random.choice(images)

    #return "https://arcantaro.ru/deck/1/"+random.choice(images)
    return random.choice(images) 

async def find_image_links(url):
    html_content = await fetch_html(url)
    soup = BeautifulSoup(html_content, 'html.parser')
    img_links = [img['src'] for img in soup.find_all('img', src=True) if ('logo' not in img['src']) and ('gb' not in img['src']) and (".jpg" in img['src'])]
    if url == "https://topmemas.top":
        img_links = [url+f"/{im}" for im in img_links]
    elif "https://ru.pinterest.com" in url:
        img_links = [im for im in img_links if "75x75_RS" not in im]
    return img_links

async def get_NY_pic():
    async with aiohttp.ClientSession() as s:
        s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'})

    sites = ["https://otkritkiok.ru/prazdniki/noviy-god"] # , 'https://topmemas.top/', "https://www.memify.ru/"]
        
    site = random.choice(sites)

    async with s.get(site) as response:
        html = await response.text()
    
    soup = BeautifulSoup(html, 'lxml')

    
    file = open('http.txt', 'w+')
    file.write(str(soup))
    # file.write(str(text)+' \n '+str(img_new))
    file.close()

    img_new = []

    if site == "https://otkritkiok.ru/prazdniki/noviy-god":
        img = re.findall(
            r'src="https://cdn.otkritkiok.ru/posts/thumbs/\w+-\w+-\w+-\w+-\w+-\d+.\w+"',
            str(soup))
        for st in img:
            st = re.sub(r'src="', '', st)
            st = re.sub(r'"', '', st)
            img_new.append(st)


    return img_new[random.randint(0, int(len(img_new)/2))]

async def get_pic():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'}
    sites = ['https://topmemas.top', "https://www.memify.ru", "https://vk.com/countryballs_re",
             "https://ru.pinterest.com/eutagia/мемы-на-все-случаи-жизни", "https://pressa.tv/comics" ]
             
    async with aiohttp.ClientSession(headers=headers) as s:
        #tasks = [await fetch_and_parse(s, site) for site in sites]
        tasks = [await find_image_links(site) for site in sites]
        img_new = [img for sublist in tasks for img in sublist]  # Flatten the list

    return random.choice(img_new) #if img_new else None

async def fetch_and_parse(session, site):
    img_new = []
    async with session.get(site) as response:
        html = await response.text()
    soup = BeautifulSoup(html, 'lxml')

    if site == 'http://1001mem.ru/':
        img = re.findall(
            r'src="http://img\.1001mem\.ru/\w+/\w+/\w+\.jpg"',
            str(soup))
        for st in img:
            st = re.sub(r'src="', '', st)
            st = re.sub(r'"', '', st)
            img_new.append(st)
    elif site == 'https://topmemas.top/':
        img = re.findall(
            r'src="img/\w+/\w+\.jpg"',
            str(soup))
        for st in img:
            st = re.sub(r'src="', 'https://topmemas.top/', st)
            st = re.sub(r'"', '', st)
            img_new.append(st)
    elif site == "https://www.memify.ru/":
        img = re.findall(
            r'src="https://www.cdn.memify.ru/media/\w+/\w+/\w+-*\w*\.jpg"',
            str(soup))
        for st in img:
            st = re.sub(r'src="', '', st)
            st = re.sub(r'"', '', st)
            img_new.append(st)

    return img_new

'''
async def get_pic():
    async with aiohttp.ClientSession() as s:
        s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'})

        sites = [ "http://1001mem.ru/", 'https://topmemas.top/', "https://www.memify.ru/"] #'https://vk.com/try2py', 'https://vk.com/tnull', 'https://vk.com/saintbeobanka', 'https://vk.com/stankasiki',

    img_new = []
    for site in sites:
        
        async with s.get(site) as response:
            html = await response.text()

        soup = BeautifulSoup(html, 'lxml')

        if site == 'http://1001mem.ru/':
            img = re.findall(
                r'src="http://img\.1001mem\.ru/\w+/\w+/\w+\.jpg"',
                str(soup))
            for st in img:
                st = re.sub(r'src="', '', st)
                st = re.sub(r'"', '', st)
                img_new.append(st)
        elif site == 'https://topmemas.top/':
            img = re.findall(
                r'src="img/\w+/\w+\.jpg"',
                str(soup))
            for st in img:
                st = re.sub(r'src="', 'https://topmemas.top/', st)
                st = re.sub(r'"', '', st)
                img_new.append(st)
        elif site == "https://www.memify.ru/":
            img = re.findall(
                r'src="https://www.cdn.memify.ru/media/\w+/\w+/\w+-*\w*\.jpg"',
                str(soup))
            for st in img:
                st = re.sub(r'src="', '', st)
                st = re.sub(r'"', '', st)
                img_new.append(st)
        else:
            img = re.findall(
                r'data-src_big="https://\w+-\w+\.\w+\.com/\w+/\w+/\w+-*\w*.jpg\?size=\d+x\d+&amp;quality=\d+&amp;sign=\w+&amp;type=album\|\d+\|\d+"',
                str(soup))
            for st in img:
                st = re.sub(r'&amp;', '&', st)
                st = re.sub(r'\|', '%7C', st)
                st = re.sub(r'data-src_big="', '', st)
                st = re.sub(r'"', '', st)
                img_new.append(st)

            rx = re.compile(r'<div class="pi_text">([^/]+)</div>')
            text = rx.findall(str(soup))
            mems = dict(zip(text, img_new))

            txt = random.choice(text)
            im = mems[txt]


    return random.choice(img_new)
'''

#file = open('http.txt', 'w+')
#file.write(str(mm[0])+"        "+ mm[1])
#file.write(str(text)+' \n '+str(img_new))
#file.close()
