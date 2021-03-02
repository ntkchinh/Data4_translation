from bs4 import BeautifulSoup as bsp
import pandas as pd
from selenium import webdriver
import selenium.webdriver.support.ui as ui
import pandas as pd
import time


# driver = webdriver.Chrome("/home/min/chromedriver")

find_result = "http://tonghoiyhoc.vn/tap-chi-trong-nuoc.html"

driver.get(find_result)

# wait = ui.WebDriverWait(driver, 40)


def bs(driver):
    return bsp(driver.page_source, features='lxml')


# results = wait.until(lambda driver: 
#         bs(driver).findAll('a', href=True, attrs={'onclick':'Doc_EN(MemberGA)'})
# )

# print(results)

tvplvn = 'http://jmp.huemed-univ.edu.vn'

import tqdm
import sys

# start_page = int(sys.argv[1])
# start_doc = int(sys.argv[2])
start_page = int(0)
start_doc = int(0)

def driver_get(driver, link, return_link=None):
    driver.get(link)
    while bs(driver).findAll('img', attrs={'src': '/registimage.aspx'}):
        print(link)
        input('Enter when finish verfifying.')
        if return_link:
            driver.get(return_link)
        else:
            driver.get(link)



for count in range(start_page, 42):
    
    print('Working on page {}'.format(count))
    hrefs = []

    driver_get(driver, find_result + '&Page={}'.format(count))


    for elem in driver.find_elements_by_class_name('linkheader'):
        hrefs.append(elem.get_property('href'))


    use_bs = True

    href_count = 0
    for href in tqdm.tqdm(hrefs):
        href_count += 1
        if href_count <= start_doc and count == start_page:
            continue
        link = href

        if link == '':
            continue
        
        driver_get(driver, link)

        if use_bs:

            pair = bs(driver).findAll('image', href=True, attrs={'id=ctl00_ContentG&VN_cmdInBB'})
            
            if len(pair) == 0:
                continue
            
            driver_get(driver, tvplvn+pair[0]["href"], link)
            
        else:
            # driver.find_element_by_partial_link_text('Tải về').click()

            pair = driver.find_elements_by_partial_link_text('Tải Văn bản tiếng Việt')

            pair[0].click()

    print('Done with page {}'.format(count))