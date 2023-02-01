import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs
import codecs
import re

# url = 'https://disk.yandex.ru/d/VjfZRBgaGJvp5Q/Горячие%20блюда/Запеченный%20Mac%26Cheese'
# options = Options()
# options.headless = True
# options.add_experimental_option("detach", True)
# options.add_argument("--window-size=1920,1200")
# DRIVER_PATH = '/chromedriver_win32/chromedriver.exe'
# driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
# driver.get(url)

# html = driver.page_source
# soup = bs(html, 'html.parser')
# file = codecs.open("Page.html", "w", "utf−8")
# file.write(html)
# driver.quit()
# dish_card = soup.find_all(class_="public-grid-item-preview")
# print(dish_card[0])

# f = codecs.open("Page.html", "r", "utf−8")
# html = f.read()
# soup = bs(html, 'html.parser')
# dish_cards = soup.find_all(class_="public-grid-item-preview")
# dish_data = {'titel': [], 'price': []}
# print(dish_cards[0].img)
# for card in dish_cards:
#     titel_raw = str(card['title']).replace('р.jpeg', '').replace('р.jpg', '')
#     price = re.findall(r'\d+', titel_raw)
#     titel_clean = titel_raw.replace(price[0], '')
#     dish_data['titel'].append(titel_clean)
#     dish_data['price'].append(price)
key = requests.get('https://oauth.yandex.ru/authorize?response_type=code&client_id=b2e5f7ebd9d14e0bac47853c3fa30a55')

print(key.text)




