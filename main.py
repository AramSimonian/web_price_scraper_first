import urllib3
import re
import sys
import datetime
import csv
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

def build_supermarket_attribs():
    """
    <div class="pd__cost">
        <div data-test-id="pd-retail-price" class="pd__cost__total undefined">£5.50</div>
        <span data-test-id="pd-unit-price" class="pd__cost__per-unit">8p / ea</span>
    </div>
    """
    """
    """
    sainsburys_tags = {
        'link_prefix': 'https://www.sainsburys.co.uk/shop/gb/groceries/product/details/{0}',
        'price_tag_type': 'div',
        'price_tag_attr': 'data-test-id',
        'price_class_name_or_value': 'pd-retail-price',
        'promo_tag_type': 'a',
        'promo_tag_attr': 'class',
        'promo_class_name_or_value': 'promotion-message__link',
        'pause_for_class_name': 'pd__cost__per-unit'
    }
    morrisons_tags = {
        'link_prefix': 'https://groceries.morrisons.com/webshop/product/{0}',
        'price_tag_type': 'meta',
        'price_tag_attr': 'itemprop',
        'price_class_name_or_value': 'price',
        'promo_tag_type': '',
        'promo_tag_attr': '',
        'promo_class_name_or_value': '',
        'pause_for_class_name': 'ft-footer'
    }
    asda_tags = {
        'link_prefix': 'https://groceries.asda.com/product/{0}',
        'price_tag_type': 'strong',
        'price_tag_attr': 'class',
        'price_class_name_or_value': 'co-product__price pdp-main-details__price',
        'promo_tag_type': '',
        'promo_tag_attr': '',
        'promo_class_name_or_value': '',
        'pause_for_class_name': 'pdp-main-details__price-container'
    }
    tesco_tags = {
        'link_prefix': 'https://www.tesco.com/groceries/en-GB/products/{0}',
        'price_tag_type': 'div',
        'price_tag_attr': 'class',
        'price_class_name_or_value': 'price-per-sellable-unit price-per-sellable-unit--price price-per-sellable-unit--price-per-item',
        'promo_tag_type': '',
        'promo_tag_attr': '',
        'promo_class_name_or_value': '',
        'pause_for_class_name': 'price-details--wrapper'
    }
    waitrose_tags = {
        'link_prefix': 'https://www.waitrose.com/ecom/products/{0}',
        'price_tag_type': 'span',
        'price_tag_attr': 'data-test',
        'price_class_name_or_value': 'product-pod-price',
        'promo_tag_type': '',
        'promo_tag_attr': '',
        'promo_class_name_or_value': '',
        'pause_for_class_name': 'fullDetails___j6CuY'
    }
    superdrug_tags = {
        'link_prefix': 'https://www.superdrug.com/{0}',
        'price_tag_type': 'span',
        'price_tag_attr': 'itemprop',
        'price_class_name_or_value': 'price',
        'promo_tag_type': '',
        'promo_tag_attr': '',
        'promo_class_name_or_value': '',
        'pause_for_class_name': 'bvRatingReview'
    }

    """
    <div id="estore_product_price_widget" class="estore_product_price_widget_redesign price-reDesign">
        <div class="price price_redesign" id="PDP_productPrice">£5.85</div>
        <div class="productid productid_redesign" id="productId">5345006</div>
        <span id="schemaOrgPrice" style="display:none;">5.85</span>
        <input type="hidden" name="cm_productPrice" id="cm_productPrice" value="£5.85">
        <div class="details details_redesign">65 UNI | £0.09 per 1UNI</div>
    </div>
    """
    boots_tags = {
        'link_prefix': 'https://www.boots.com/{0}',
        'price_tag_type': 'div',
        'price_tag_attr': 'id',
        'price_class_name_or_value': 'PDP_productPrice',
        'pause_for_class_name': 'global-footer'
    }

    output = {
        'sainsburys': sainsburys_tags,
        'morrisons': morrisons_tags,
        'asda': asda_tags,
        'tesco': tesco_tags,
        'waitrose': waitrose_tags,
        'superdrug': superdrug_tags,
        'boots': boots_tags
    }
    return output


def get_shop_from_link(link):
    shop = link.split(".")
    return shop[1]


def get_shop_attribs_dict(shop):
    return this.all_tags[shop]


def build_product_link(link_prefix, product_stub):
    return link_prefix.format(product_stub)


def get_product_detail_row(filename):
    # open the file
    with open(filename, "r") as product_detail:
        data_reader = csv.reader(product_detail)
        for row in data_reader:
            # return a row from the file
            yield row


class ProductWrapper:
    def extract_wrappers(self, shop_attribs_dict, product_link):
        try:
            # navigate to the grocery item site
            this.driver.get(product_link)

            element_present = EC.presence_of_element_located((By.CLASS_NAME, shop_attribs_dict['pause_for_class_name']))
            WebDriverWait(this.driver, timeout).until(element_present)
            soup = BeautifulSoup(this.driver.page_source, 'html.parser')
            try:
                price_wrapper = soup.find(shop_attribs_dict['price_tag_type'],
                                   attrs={shop_attribs_dict['price_tag_attr']: shop_attribs_dict['price_class_name_or_value']})
            except:
                price_wrapper = None
            try:
                promo_wrapper = soup.find(shop_attribs_dict['promo_tag_type'],
                                          attrs={shop_attribs_dict['promo_tag_attr']: shop_attribs_dict['promo_class_name_or_value']})
            except:
                promo_wrapper = None

            output = price_wrapper, promo_wrapper
        except:
            output = None, None

        return output

    def get_price(self, price_wrapper):

        try:
            if price_wrapper is None:
                price = 'Unable to locate price wrapper'
            else:
                price = '£' + re.findall(r'(\d+\.\d+|\d+)', str(price_wrapper))[0]
        except TimeoutException:
            price = 'Unable to retrieve price - timeout'

        return price

    def get_promo(self, promo_wrapper):
        try:
            if promo_wrapper is None:
                promo = ''
            else:
                promo = promo_wrapper.text
        except:
            promo = None

        return promo

def write_output(price_list):
    with open("price_check.txt", "w") as file:
        date = datetime.datetime.now().date()
        hour = datetime.datetime.now().hour
        minute = datetime.datetime.now().minute
        file.write('{} {:02d}:{:02d}\n'.format(date, hour, minute))
        file.write(price_list)

def main():
    this.all_tags = build_supermarket_attribs()

    this.driver = webdriver.Chrome()

    output = ''
    product_wrapper = ProductWrapper()

    price_data = get_product_detail_row('price_links.csv')

    for product_item in price_data:
        shop, product_type, product_stub = product_item
        shop_attribs_dict = get_shop_attribs_dict(shop)

        product_link = build_product_link(shop_attribs_dict['link_prefix'], product_stub)

        wrappers = product_wrapper.extract_wrappers(shop_attribs_dict, product_link)
        price = product_wrapper.get_price(wrappers[0])
        promo = product_wrapper.get_promo(wrappers[1])

        output += '{0}, {1}: {2} {3}\n'.format(shop.title(), product_type.title(), price, promo)

    write_output(output)

    this.driver.quit()


main()
