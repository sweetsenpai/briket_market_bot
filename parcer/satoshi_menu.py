import bs4.element
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import By
from bs4 import BeautifulSoup as bs
import codecs
import os
import pandas as pd
import gspread
from briket_DB.passwords import credentials

if os.path.isfile('C:/Users/workc/OneDrive/Desktop/briket_market_bot/parcer/Page.html') is False:

    options = Options()
    options.headless = True
    # options.add_experimental_option("detach", True)
    options.add_argument("--window-size=1920,1200")
    DRIVER_PATH = '/chromedriver_win32/chromedriver.exe'
    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
    driver.get('https://satoshisushi.ru')
    button_list = driver.find_elements(By.CLASS_NAME, 'categoryPromo__buttonBox')
    for button in button_list:
        button.click()
    html = driver.page_source
    file = codecs.open("Page.html", "w", "utf−8")
    file.write(html)
    driver.quit()
else:
    f = codecs.open("Page.html", "r", "utf−8")
    html = f.read()

soup = bs(html, 'html.parser')


def get_price(pc):
    for tag in list(pc)[2]:
        try:
            if type(tag) == bs4.element.Tag:
                try:
                    if int(tag.find(itemprop="price")['content']) > 0:
                        return tag.find(itemprop="price")['content']
                except TypeError:
                    continue

        except AttributeError:
            continue
    return


product_cards = soup.find_all(class_='productCard__inner')
product_data = {'name': list(), 'price': list(), 'weght': list(), 'description': list(), 'IMG': list()}


for card in product_cards:
    # Название
    product_data['name'].append(list(card)[2].a.text.replace('\n', '').replace('                        ', '').replace('                    ', ''))
    # Цена
    product_data['price'].append(get_price(card))
    # Вес
    try:
        product_data['weght'].append(list(card)[2].div.div.li.find(class_='productAttributes__value').text)
    except AttributeError:
        product_data['weght'].append(' ')
    # Описание
    product_data['description'].append(card.p.text.replace('\n            ', '').replace('\n                ', '').replace('    ', ''))
    # Изображение
    product_data['IMG'].append(card.img['data-src'])


menu_df = pd.DataFrame(product_data)
menu_df.to_excel('satoshisushi.xlsx', float_format="%.2f")