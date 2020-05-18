import urllib3
import re
import sys
import datetime
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

nybagel_links = [
    'https://www.sainsburys.co.uk/shop/gb/groceries/product/details/new-york-bakery-co-cinnamon---raisin-bagels-x5',
    'https://groceries.morrisons.com/webshop/product/New-York-Bagel-Co-Cinnamon--Raisin/114353011',
    'https://groceries.asda.com/product/bagels/new-york-bakery-co-cinnamon-raisin-bagels/1000004372338',
    'https://www.tesco.com/groceries/en-GB/products/253829047']

product_details = [
    ['sainsburys', 'ny bagels', 'new-york-bakery-co-cinnamon---raisin-bagels-x5'],
    ['morrisons', 'ny bagels', 'New-York-Bagel-Co-Cinnamon--Raisin/114353011'],
    ['asda', 'ny bagels', 'bagels/new-york-bakery-co-cinnamon-raisin-bagels/1000004372338'],
    ['tesco', 'ny bagels', '253829047'],
    ['waitrose', 'ny bagels', 'new-york-bakery-co-cinnamon-raisin-bagels/488463-162428-162429'],
    ['sainsburys', 'warburtons bagels', 'warburtons-cinnamon-raisin-bagel-x5'],
    ['morrisons', 'warburtons bagels', 'warburtons-bagels-cinnamon-raisin-475566011'],
    ['asda', 'warburtons bagels', 'bagels/1000112419729'],
    ['tesco', 'warburtons bagels', '303351662'],
    ['sainsburys', 'yeo valley strawb yog', 'yeo-valley-organic-yogurt-strawberry-450g'],
    ['morrisons', 'yeo valley strawb yog', 'yeo-valley-family-farm-strawberry-yogurt-216892011'],
    ['asda', 'yeo valley strawb yog', 'big-pots/yeo-valley-strawberry-yogurt/24151900'],
    ['tesco', 'yeo valley strawb yog', '250983242'],
    ['waitrose', 'yeo valley strawb yog', 'yeo-valley-strawberry-bio-live-yeogurt/053024-26459-26460'],
    ['sainsburys', 'mcvities dark chocolate dig 433g', 'mcvities-digestives-dark-chocolate-433g'],
    ['morrisons','mcvities dark chocolate dig 433g','mcvitie-s-digestives-dark-chocolate-408294011'],
    ['asda','mcvities dark chocolate dig 433g','chocolate-biscuits/mc-vities-digestives-dark-chocolate/1000052709666'],
    ['sainsburys', 'mcvities dark chocolate dig 2x316g', 'mcvities-digestives-dark-chocolate-x2-316g'],
    ['asda', 'mcvities dark chocolate dig 2x316g', 'chocolate-biscuits/mc-vities-digestives-dark-chocolate-twin-pack/1000046413189'],
    ['asda','lavazza qualita rossa coffee single pack','filter-cafetiere-coffee/lavazza-qualita-rossa-ground-coffee/19344'],
    ['tesco','lavazza qualita rossa coffee single pack','254889083'],
    ['morrisons','lavazza qualita rossa coffee single pack','lavazza-qualit-rossa-ground-coffee-113704011'],
    ['waitrose','lavazza qualita rossa coffee single pack','lavazza-qualita-rossa-espresso/016519-7923-7924'],
    ['sainsburys','lavazza qualita rossa coffee twin pack','lavazza-coffee/lavazza-qualita-rossa-ground-coffee-twin-pack-espresso-x2-250g'],
    ['asda','lavazza qualita rossa coffee twin pack','filter-cafetiere-coffee/lavazza-qualita-rossa-ground-coffee/1000008931457'],
    ['tesco','lavazza qualita rossa coffee twin pack','257352903'],
    ['morrisons','lavazza qualita rossa coffee twin pack','lavazza-qualita-rossa-ground-coffee-497497011'],
    ['waitrose','lavazza qualita rossa coffee twin pack','lavazza-qualita-rossa-espresso/030254-14779-14780'],
]


def build_supermarket_attribs():
    sainsburys_tags = {
        'link_prefix': 'https://www.sainsburys.co.uk/shop/gb/groceries/product/details/{0}',
        'price_tag_type': 'div',
        'price_tag_attr': 'data-test-id',
        'price_class_name_or_value': 'pd-retail-price',
        'pause_for_class_name': 'pd__cost__per-unit'
    }
    morrisons_tags = {
        'link_prefix': 'https://groceries.morrisons.com/webshop/product/{0}',
        'price_tag_type': 'meta',
        'price_tag_attr': 'itemprop',
        'price_class_name_or_value': 'price',
        'pause_for_class_name': 'bop-price__per'
    }
    asda_tags = {
        'link_prefix': 'https://groceries.asda.com/product/{0}',
        'price_tag_type': 'strong',
        'price_tag_attr': 'class',
        'price_class_name_or_value': 'co-product__price pdp-main-details__price',
        'pause_for_class_name': 'pdp-main-details__price-container'
    }
    tesco_tags = {
        'link_prefix': 'https://www.tesco.com/groceries/en-GB/products/{0}',
        'price_tag_type': 'div',
        'price_tag_attr': 'class',
        'price_class_name_or_value': 'price-per-sellable-unit price-per-sellable-unit--price price-per-sellable-unit--price-per-item',
        'pause_for_class_name': 'price-details--wrapper'
    }
    waitrose_tags = {
        'link_prefix': 'https://www.waitrose.com/ecom/products/{0}',
        'price_tag_type': 'span',
        'price_tag_attr': 'data-test',
        'price_class_name_or_value': 'product-pod-price',
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


class PriceWrapper:
    def extract_wrappers(self, shop_attribs_dict, product_link):
        try:
            # navigate to the grocery item site
            this.driver.get(product_link)

            element_present = EC.presence_of_element_located((By.CLASS_NAME, shop_attribs_dict['pause_for_class_name']))
            WebDriverWait(this.driver, timeout).until(element_present)
            soup = BeautifulSoup(this.driver.page_source, 'html.parser')
            output = soup.find(shop_attribs_dict['price_tag_type'],
                               attrs={shop_attribs_dict['price_tag_attr']: shop_attribs_dict['price_class_name_or_value']})
           # promo_wrapper = soup.find(shop_attribs_dict['promo_tag_type'],
           #                           attrs={shop_attribs_dict['promo_tag_attr']: shop_attribs_dict['promo_class_name_or_value']})
        except:
            output = None

        return output

    def get_price(self, price_wrapper):

        try:
            if price_wrapper is None:
                price = 'Unable to locate price wrapper'
            else:
                price = '£' + re.findall(r'(\d+\.\d{2}|\d+)', str(price_wrapper))[0]
        except TimeoutException:
            price = 'Unable to retrieve price - timeout'

        return price

    def get_promo(self, promo_wrapper):
        try:
            if promo_wrapper is None:
                promo = 'Unable to locate promo wrapper'
            else:
                promo = None
        except:
            promo = None

        return promo

def main():
    this.all_tags = build_supermarket_attribs()

    this.driver = webdriver.Chrome()

    output = ''
    price_wrapper = PriceWrapper()

    for product_detail in product_details:
        shop, product_type, product_stub = product_detail
        shop_attribs_dict = get_shop_attribs_dict(shop)

        product_link = build_product_link(shop_attribs_dict['link_prefix'], product_stub)

        pw = price_wrapper.extract_wrappers(shop_attribs_dict, product_link)
        price = price_wrapper.get_price(pw)

        output += '{0}, {1}: {2}\n'.format(shop.title(), product_type.title(), price)

    with open("C:\\Temp\\price_check.txt", "w") as file:
        file.write('{0} {1}:{2}:{3}\n'.format(datetime.datetime.now().date(), datetime.datetime.now().hour, datetime.datetime.now().minute, datetime.datetime.now().second))
        file.write(output)

    this.driver.quit()


main()
