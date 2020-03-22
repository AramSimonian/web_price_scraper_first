import urllib3
import re
import sys
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

this = sys.modules[__name__]
this.all_tags = {}
this.driver = ''

timeout = 3

nybagel_links = ['https://www.sainsburys.co.uk/shop/gb/groceries/product/details/new-york-bakery-co-cinnamon---raisin-bagels-x5',
               'https://groceries.morrisons.com/webshop/product/New-York-Bagel-Co-Cinnamon--Raisin/114353011',
               'https://groceries.asda.com/product/bagels/new-york-bakery-co-cinnamon-raisin-bagels/1000004372338',
               'https://www.tesco.com/groceries/en-GB/products/253829047']

def build_supermarket_tags():
    sainsburys_tags = {
        'tag_type': 'div',
        'tag_attr': 'class',
        'class_name': 'pd__cost__total--promo undefined',
        'pause_for_class_name': 'pd__cost__per-unit'
        }
    morrisons_tags = {
        'tag_type': 'meta',
        'tag_attr': 'itemprop',
        'class_name': 'price',
        'pause_for_class_name': 'bop-price__wrapper'
        }
    asda_tags = {
        'tag_type': 'strong',
        'tag_attr': 'class',
        'class_name': 'co-product__price pdp-main-details__price',
        'pause_for_class_name': 'pdp-main-details__price-container'
        }
    tesco_tags = {
        'tag_type': 'div',
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

def get_shop_tags(shop):
    pause_for_class_name = this.all_tags[shop]['pause_for_class_name']
    tag_type = this.all_tags[shop]['tag_type']
    tag_attr = this.all_tags[shop]['tag_attr']
    class_name = this.all_tags[shop]['class_name']

    return pause_for_class_name, tag_type, tag_attr, class_name

def extract_price_wrapper_from_link(product_link, shop):
    # retrieve the tag info for the shop
    pause_for_class_name, tag_type, tag_attr, class_name = get_shop_tags(shop)

    # navigate to the grocery item site
    this.driver.get(product_link)

    element_present = EC.presence_of_element_located((By.CLASS_NAME, pause_for_class_name))
    WebDriverWait(this.driver, timeout).until(element_present)
    soup = BeautifulSoup(this.driver.page_source, 'html.parser')
    return soup.find(tag_type, attrs={tag_attr: class_name})

def get_shop_and_price_from_link(product_link):
    # determine the shop
    shop = get_shop_from_link(product_link)

    try:
        price_wrapper = extract_price_wrapper_from_link(product_link, shop)
        if price_wrapper is None:
            price = 'Unable to locate price wrapper'
        else:
            price = '£' + re.findall(r'(\d+\.\d{2}|\d+)', str(price_wrapper))[0]
    except TimeoutException:
        price = 'Unable to retrieve price - timeout'

    return "{0}: {1}\n".format(shop.title(), price)


def main():
    this.all_tags = build_supermarket_tags()

    this.driver = webdriver.Chrome()

    output = 'Bagels:\n'

    for bagel_link in nybagel_links:
        output += get_shop_and_price_from_link(bagel_link)

    with open("C:\\Temp\\price_check.txt", "w") as file:
        file.write(output)

    driver.quit()

main()
