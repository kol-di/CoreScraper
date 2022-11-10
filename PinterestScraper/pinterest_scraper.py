from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import time
import os


WORK_DIR = os.path.join(os.getcwd(), 'images')

try:
    os.chdir(WORK_DIR)
except FileNotFoundError:
    os.mkdir(WORK_DIR)
    os.chdir(WORK_DIR)


class PageEndError(Exception):
    pass


def get_image_batch(driver):
    scrollnum = 1
    sleepTimer = 2

    while True:
        last_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollBy(0,5000)")
        print('scroll-down')
        time.sleep(sleepTimer)
        new_height = driver.execute_script("return document.body.scrollHeight")

        if last_height == new_height:
            print('Page end')
            raise PageEndError

        yield


def get_image(tag, storage_folder, img_cnt):
    url = f'https://in.pinterest.com/search/pins/?q={tag}'
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(executable_path='chromedriver.exe', options=options)
    driver.get(url)

    soup = BeautifulSoup(driver.page_source, 'html5lib')
    prev_soup = set(soup.find_all('img'))

    try:
        cur_img_cnt = 0
        while cur_img_cnt < img_cnt:
            next(get_image_batch(driver))
            soup = BeautifulSoup(driver.page_source, 'html5lib')
            cur_img_cnt = len(soup.find_all('img'))
            print('Images in soup', cur_img_cnt)
            new_soup = set(soup.find_all('img'))
            print('New images', len(prev_soup.intersection(new_soup)))
            prev_soup = new_soup
    except PageEndError:
        pass

    storage_path = os.path.join(os.getcwd(), storage_folder)
    if not os.path.exists(storage_path):
        os.mkdir(storage_path)
    os.chdir(storage_path)

    for link in soup.find_all('img'):
        img_link = link.get('src')
        img_name = img_link.rsplit('/', 1)[-1].strip('.jpg') + '.png'
        print(img_name)
        with open(img_name, 'wb') as f:
            img = requests.get(img_link)
            f.write(img.content)


get_image('breakcore', 'breakcore', 100)

