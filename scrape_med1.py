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
import tqdm
import sys
import lib
from urllib.request import urlopen
from urllib.parse import urlparse




driver = webdriver.Chrome("/home/min/chromedriver")
driver.maximize_window()
src = 'http://tonghoiyhoc.vn'


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

def getting_hrefs():

    hrefs_source = []
    hrefs = []
    for i in range(2015, 2021):
        href1 = src + '/nam-{}/trang-1.htm'.format(i)
        href2 = src + '/nam-{}/trang-2.htm'.format(i)
        hrefs_source.append(href1)
        hrefs_source.append(href2)
    hrefs_source = hrefs_source[0:-1]
    assert len(hrefs_source)==11
    print(hrefs_source)
    input()

    for source in hrefs_source:
        print(source)
        driver_get(driver, source)
        wait = ui.WebDriverWait(driver, 10)
        c = wait.until(lambda driver: 
                bs(driver).findAll('a', attrs={"class": "cate"}))
        # print(c)
        if not c:
            continue
        for link in c:
            href = link.get('href')
            # print(href)
            hrefs.append(href)

    print(len(hrefs))
    with open('tonghoi_yHoc_hrefs.txt', 'w') as f:
        for href in hrefs:
            f.write(str(href) + '\n')

# with open('tonghoi_yHoc_hrefs.txt', 'r') as f:
#     hrefs = f.readlines()
# assert len(hrefs)==87

# count = 0
# new_hrefs = []
def click_file_link(link_to_file):
    schema = urlparse(link_to_file).scheme
    if scheme.upper() not in ['HTTP', 'HTTPS']:
        raise InvalidSchemaException('Schema "%s" is not supported' % scheme)
    link_to_file.click()

def getting_docs():
    for href in tqdm.tqdm(hrefs):
    # print(href)
        driver_get(driver, href)
        wait = ui.WebDriverWait(driver, 10)

        links_to_files = driver.find_elements_by_xpath("//tr/td/p/a")
    # print(links_to_files)

        if links_to_files:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/12);")
            # print('files are found!')
            for i, link in enumerate(links_to_files):
                count += 1
                print(count)
                # if i==5:
                #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                # elif i==15:
                #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight*2/3);")
                # elif i==25:
                #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight*5/6);")
                
                # if i in [18]:
                #     continue
                try: 
                    link.click()
                except:
                    print("link is not valid")
                    continue
            

    print('Done')
    print('Downloaded: ',count)


#====================================

# try:
            #     wait = ui.WebDriverWait(driver, 10)
            #     # element_present = EC.presence_of_element_located((By.xpath, '//tr/td/p/a'))
            #     # ui.WebDriverWait(driver, timeout).until(element_present)
            #     link.click()
            # except TimeoutException:
            #     print("link is not accessible")
            #     continue
            
            # link = ui.WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'link.dismiss')))
            
            # try:
            #     validate(str(link))
            #     print("String is a valid URL")
            #     link.click()
            # except ValidationError as exception:
            #     print("String is not valid URL")
            #     continue
            # try:
            #     response = requests.get(str(link))
            #     print("URL is valid and exists on the internet")
             # except requests.ConnectionError as exception:
            #     print("URL does not exist on Internet")
            #     continue
            # link = wait.until(expected_conditions.element_to_be_clickable((By.XPATH,
            
           