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

product_details = [
                        ['sainsburys','ny bagels','new-york-bakery-co-cinnamon---raisin-bagels-x5'],
                        ['morrisons','ny bagels','New-York-Bagel-Co-Cinnamon--Raisin/114353011'],
                        ['asda','ny bagels','new-york-bakery-co-cinnamon-raisin-bagels/1000004372338'],
                        ['tesco','ny bagels','253829047'],
                        ['sainsburys','warburtons bagels','warburtons-cinnamon-raisin-bagel-x5'],
                        ['morrisons','warburtons bagels','warburtons-bagels-cinnamon-raisin-475566011'],
                        ['asda','warburtons bagels','1000112419729'],
                        ['tesco','warburtons bagels','303351662'],
                        ['waitrose','warburtons bagels','new-york-bakery-co-cinnamon-raisin-bagels/488463-162428-162429'],
                   ]

def build_supermarket_attribs():
    sainsburys_tags = {
        'link_prefix': 'https://www.sainsburys.co.uk/shop/gb/groceries/product/details/{0}',
        'tag_type': 'div',
        'tag_attr': 'data-test-id',
        'class_name': 'pd-retail-price',
        'pause_for_class_name': 'pd__cost__per-unit'
        }
    morrisons_tags = {
        'link_prefix': 'https://groceries.morrisons.com/webshop/product/{0}',
        'tag_type': 'meta',
        'tag_attr': 'itemprop',
        'class_name': 'price',
        'pause_for_class_name': 'bop-price__per'
        }
    asda_tags = {
        'link_prefix': 'https://groceries.asda.com/product/bagels/{0}',
        'tag_type': 'strong',
        'tag_attr': 'class',
        'class_name': 'co-product__price pdp-main-details__price',
        'pause_for_class_name': 'pdp-main-details__price-container'
        }
    tesco_tags = {
        'link_prefix': 'https://www.tesco.com/groceries/en-GB/products/{0}',
        'tag_type': 'div',
        'tag_attr': 'class',
        'class_name': 'price-per-sellable-unit price-per-sellable-unit--price price-per-sellable-unit--price-per-item',
        'pause_for_class_name': 'price-details--wrapper'
        }
    waitrose_tags = {
        'link_prefix': 'https://www.waitrose.com/ecom/products/{0}',
        'tag_type': 'div',
        'tag_attr': 'data-test',
        'class_name': 'priceAndActions___16N4-',
        'pause_for_class_name': 'fullDetails___j6CuY'
        }

    output = {
        'sainsburys': sainsburys_tags,
        'morrisons': morrisons_tags,
        'asda': asda_tags,
        'tesco': tesco_tags,
        'waitrose': waitrose_tags
        }
    return output

def get_shop_from_link(link):
    shop = link.split(".")
    return shop[1]

def get_shop_attribs_dict(shop):
    return this.all_tags[shop]

def build_product_link(link_prefix, product_stub):
    return link_prefix.format(product_stub)

def extract_price_wrapper(shop_attribs_dict, product_link):
    try:
        # navigate to the grocery item site
        this.driver.get(product_link)

        element_present = EC.presence_of_element_located((By.CLASS_NAME, shop_attribs_dict['pause_for_class_name']))
        WebDriverWait(this.driver, timeout).until(element_present)
        soup = BeautifulSoup(this.driver.page_source, 'html.parser')
        output = soup.find(shop_attribs_dict['tag_type'], attrs={shop_attribs_dict['tag_attr']: shop_attribs_dict['class_name']})
    except:
        output = None

    return output

def get_price_from_wrapper(price_wrapper):

    try:
        if price_wrapper is None:
            price = 'Unable to locate price wrapper'
        else:
            price = '£' + re.findall(r'(\d+\.\d{2}|\d+)', str(price_wrapper))[0]
    except TimeoutException:
        price = 'Unable to retrieve price - timeout'

    return price

def main():
    this.all_tags = build_supermarket_attribs()

    this.driver = webdriver.Chrome()

    output = ''

    for product_detail in product_details:
        shop, product_type, product_stub = product_detail
        shop_attribs_dict = get_shop_attribs_dict(shop)

        product_link = build_product_link(shop_attribs_dict['link_prefix'], product_stub)

        price_wrapper = extract_price_wrapper(shop_attribs_dict, product_link)
        price = get_price_from_wrapper(price_wrapper)

        output += '{0}, {1}: {2}\n'.format(shop.title(), product_type.title(), price)

    with open("C:\\Temp\\price_check.txt", "w") as file:
        file.write(output)

    driver.quit()

main()
