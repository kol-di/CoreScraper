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
    sleep_timer = 1

    batch_cnt = 0
    while True:
        batch_cnt += 1
        print(f'Batch {batch_cnt}')
        last_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollBy(0,5000)")
        time.sleep(sleep_timer)
        new_height = driver.execute_script("return document.body.scrollHeight")

        if last_height == new_height:
            print('Page end')
            raise PageEndError

        yield


def save_images(image_tags):
    for tag in image_tags:
        img_link = tag.get('src')
        img_name = img_link.rsplit('/', 1)[-1].strip('.jpg') + '.png'
        with open(img_name, 'wb') as f:
            img = requests.get(img_link)
            f.write(img.content)


def cd_to_image_folder(storage_folder):
    storage_path = os.path.join(os.getcwd(), storage_folder)
    if not os.path.exists(storage_path):
        os.mkdir(storage_path)
    os.chdir(storage_path)


def get_image(tag, storage_folder, img_cnt):
    url = f'https://in.pinterest.com/search/pins/?q={tag}'
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(executable_path='chromedriver.exe', options=options)
    driver.get(url)

    cd_to_image_folder(storage_folder)

    soup = BeautifulSoup(driver.page_source, 'html5lib')
    prev_window_soup = set(soup.find_all('img'))
    save_images(prev_window_soup)
    cur_img_cnt = len(prev_window_soup)
    print(f'Collected {cur_img_cnt} new images')
    image_batch_collector = get_image_batch(driver)
    try:
        while cur_img_cnt < img_cnt:
            next(image_batch_collector)
            soup = BeautifulSoup(driver.page_source, 'html5lib')

            next_window_soup = set(soup.find_all('img'))
            unique_soup = next_window_soup - prev_window_soup
            save_images(unique_soup)

            print(f'Collected {len(unique_soup)} new images, '
                  f'{len(next_window_soup.intersection(prev_window_soup))} old images.')
            prev_window_soup = next_window_soup
            cur_img_cnt += len(unique_soup)
    except PageEndError:
        print(f'Page exhausted, collected {cur_img_cnt} images')
        pass
    else:
        print(f'Collected {cur_img_cnt} images')


get_image('breakcore', 'breakcore', 100)

