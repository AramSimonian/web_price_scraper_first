import urllib3
import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

timeout = 3

nybagel_links = ['https://www.sainsburys.co.uk/shop/gb/groceries/product/details/new-york-bakery-co-cinnamon---raisin-bagels-x5',
               'https://groceries.morrisons.com/webshop/product/New-York-Bagel-Co-Cinnamon--Raisin/114353011',
               'https://groceries.asda.com/product/bagels/new-york-bakery-co-cinnamon-raisin-bagels/1000004372338',
               'https://www.tesco.com/groceries/en-GB/products/253829047']

def build_supermarket_tags():
    sainsburys_tags = {
        'tag_type': 'div',
        'tag_id': 'pd-retail-price',
        'tag_attr': 'class',
        'class_name': 'pd__cost__total--promo undefined',
        'pause_for_class_name': 'pd__cost__per-unit'
        }
    morrisons_tags = {
        'tag_type': 'meta',
        'tag_id': '',
        'tag_attr': 'itemprop',
        'class_name': 'price',
        'pause_for_class_name': 'bop-price__wrapper'
        }
    asda_tags = {
        'tag_type': 'strong',
        'tag_id': '',
        'tag_attr': 'class',
        'class_name': 'co-product__price pdp-main-details__price',
        'pause_for_class_name': 'pdp-main-details__price-container'
        }
    tesco_tags = {
        'tag_type': 'div',
        'tag_id': '',
        'tag_attr': 'class',
        'class_name': 'price-per-sellable-unit price-per-sellable-unit--price price-per-sellable-unit--price-per-item',
        'pause_for_class_name': 'price-details--wrapper'
        }

    output = {
        'sainsburys': sainsburys_tags,
        'morrisons': morrisons_tags,
        'asda': asda_tags,
        'tesco': tesco_tags
        }
    return output

def get_shop_from_link(link):
    shop = link.split(".")
    return shop[1]

def main():
    all_tags = build_supermarket_tags()

    driver = webdriver.Chrome()

    output = 'Bagels:\n'

    for bagel_link in nybagel_links:
        # navigate to the grocery item site
        driver.get(bagel_link)

        # determine the shop and retrieve the tag info
        shop = get_shop_from_link(bagel_link)

        pause_for_class_name = all_tags[shop]['pause_for_class_name']
        tag_type = all_tags[shop]['tag_type']
        tag_attr = all_tags[shop]['tag_attr']
        class_name = all_tags[shop]['class_name']


        try:
            element_present = EC.presence_of_element_located((By.CLASS_NAME, pause_for_class_name))
            WebDriverWait(driver, timeout).until(element_present)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            price_box = soup.find(tag_type, attrs={tag_attr: class_name})

            if price_box is None:
                price = ""
            else:
                price = re.findall(r'(\d+\.\d{2}|\d+)', str(price_box))[0]

        except TimeoutException:
            price = 'Unable to retrieve price'
        finally:
            output += "{0}: £{1}\n".format(shop.title(), price)

    with open("C:\\Temp\\price_check.txt", "w") as file:
        file.write(output)

    driver.quit()

main()
