import requests
from bs4 import BeautifulSoup as bsp
from bs4 import Comment
from selenium import webdriver
import selenium.webdriver.support.ui as ui
# from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

import pandas as pd
import os
import time
import lib
import tqdm
from urllib.request import urlopen



driver = webdriver.Chrome("/home/min/chromedriver")
driver.maximize_window()
# driver = webdriver.Firefox('home/min/Downloads/geckodriver')
hrefs = []

urls = []
src = 'https://lyricstranslate.com'
url_org = 'https://lyricstranslate.com/en/translations/328-1023750-1020671-1037158-1000210-521-1037091-1029190/50/none/none/none/0/0/0/0'


def bs(driver):
    return bsp(driver.page_source, features='lxml')

def driver_get(driver, link, return_link=None):
    driver.get(link)
    while bs(driver).findAll('img', attrs={'src': '/registimage.aspx'}):
        print(link)
        input('Enter when finish verfifying.')
        if return_link:
            driver.get(return_link)
        else:
            driver.get(link)

# urls.append(url_org)
# for i in range(1, 9):
#     url = url_org + '?page={}'.format(i)
#     urls.append(url)
# print(len(urls))
# input()
# for i, url in enumerate(urls):
#     driver.get(url)
#     wait = ui.WebDriverWait(driver, 60)
#     c = wait.until(lambda driver: 
#             bs(driver).findAll('td', attrs={"class": "ltsearch-songtitle"}))

#     for link in c:
#         new_soup = bsp(str(link), 'html.parser', multi_valued_attributes=None)
#         href = new_soup.a['href']
#         hrefs.append(href)

# with open('lyrics_hrefs.txt', 'w') as f:
#     for href in hrefs:
#         f.write(href + '\n')
# exit()

hrefs = lib.read_nonempty('lyrics_hrefs.txt')
print(len(hrefs))
# input()


crd = os.getcwd()
# count = 0
# count = 1143
for i, href in tqdm.tqdm(enumerate(hrefs)):
    # while True:
    href = src + href
    # driver.get(href)
    driver_get(driver, href)
    
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight/12);")
    driver.implicitly_wait(15)
    #click the button to show org lyric 'Click to see the original lyrics'
    original_lyric = driver.find_elements_by_partial_link_text('Click to see the original lyrics')
    
    if original_lyric:
        print('yes') 
        original_lyric[0].click()

    # wait = ui.WebDriverWait(driver, 100)
    timeout = 25
    try:
        element_present = EC.presence_of_element_located((By.ID, 'song-body'))
        ui.WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        print("Timed out waiting for page to load")
        continue
    soup = bsp(driver.page_source, 'lxml')

    en_collumn = soup.find_all('div', class_='song-node-text')
    vi_collumn = soup.find_all('div', class_='translate-node-text')
    
    if not en_collumn or not vi_collumn:
        print('failed on, ', href)
        continue

    en_collumn = en_collumn[0]
    vi_collumn = vi_collumn[0]

    en_lyrics = en_collumn.find_all('div', class_='ltf')
    vi_lyrics = vi_collumn.find_all('div', class_='ltf')
    
    if not en_lyrics or not vi_lyrics:
        print('failed on, ', href)
        continue
    
    # print(en_lyrics)
    # print(vi_lyrics)
    # input()
    
    en_texts = []
    for div in en_lyrics:
        en_texts.append(div.text)
    # print(en_texts)
    # input()

    vi_texts = []
    for div in vi_lyrics:
        vi_texts.append(div.text)
    # print(vi_texts)
    # input()   

    with open('{}_lyric_en.txt'.format(i), 'w') as f:
        for lyric in en_texts:
            f.write(lyric)
    
    with open('{}_lyric_vi.txt'.format(i), 'w') as f:
        for lyric in vi_texts:
            f.write(lyric)
    
