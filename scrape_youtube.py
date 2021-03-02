from bs4 import BeautifulSoup as bsp
import pandas as pd
from selenium import webdriver
import selenium.webdriver.support.ui as ui
import time


driver = webdriver.Chrome("/home/min/chromedriver")

find_result = "https://www.youtube.com/c/JREClips/videos"

driver.get(find_result)

wait = ui.WebDriverWait(driver, 40)


def bs(driver):
    return bsp(driver.page_source, features='lxml')


results = wait.until(lambda driver: 
        bs(driver).findAll('a', href=True, attrs={'id':'video-title'})
)

# print(results)

tvplvn = 'https://www.youtube.com'

import tqdm
import sys
import youtube_dl

def download_subs(url, lang="en"):
    opts = {
        "skip_download": True,
        "writesubtitles": "%(name)s.vtt",
        "subtitlelangs": lang
    }

    with youtube_dl.YoutubeDL(opts) as yt:
        yt.download([url])

# url_list = ['https://www.youtube.com/watch?v=8Lvrikv6oPs']
# download_subs(url)
hrefs = []
for elem in driver.find_elements_by_id('video-title'):
        hrefs.append(elem.get_property('href'))

for url in tqdm(hrefs):
    download_subs(url, lang='en')
    download_subs(url, lang='vi')

# start_page = int(sys.argv[1])
# start_doc = int(sys.argv[2])


def driver_get(driver, link, return_link=None):
    driver.get(link)
    while bs(driver).findAll('img', attrs={'src': '/registimage.aspx'}):
        print(link)
        input('Enter when finish verfifying.')
        if return_link:
            driver.get(return_link)
        else:
            driver.get(link)

# for elem in driver.find_elements_by_id('video-title'):
    #     hrefs.append(elem.get_property('href'))

# for count in range(start_page, 649):
# count = 0
# while True:
    # count += 1
    # print('Working on page {}'.format(count))
    # hrefs = []

    # driver_get(driver, find_result + '&page={}'.format(count))


    # for elem in driver.find_elements_by_partial_link_text(''):
    #     hrefs.append(elem.get_property('href'))


    # use_bs = True

    # href_count = 0
    # for href in tqdm.tqdm(hrefs):
    #     href_count += 1
    #     if href_count <= start_doc and count == start_page:
    #         continue
    #     link = href

    #     if link == '':
    #         continue
        
    #     driver_get(driver, link)

    #     if use_bs:

    #         vi = bs(driver).findAll('a', href=True, attrs={'title': 'Tải văn bản tiếng Việt'})
    #         en = bs(driver).findAll('a', href=True, attrs={'title': 'Tải văn bản tiếng Anh'})
            
    #         if len(vi) == 0:
    #             continue
    #         if len(en) == 0:
    #             continue
            
    #         driver_get(driver, tvplvn+vi[0]["href"], link)
    #         driver_get(driver, tvplvn+en[0]["href"], link)
    #     else:
    #         driver.find_element_by_partial_link_text('Tải về').click()

    #         vi = driver.find_elements_by_partial_link_text('Tải Văn bản tiếng Việt')
    #         en = driver.find_elements_by_partial_link_text('Tải Văn bản tiếng Anh')

    #         vi[0].click()
    #         en[0].click()  

    # print('Done with page {}'.format(count))