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
    sainsburys_tags = {
        'link_prefix': 'https://www.sainsburys.co.uk/shop/gb/groceries/product/details/{0}',
        'prod_details_type': 'div',
        'prod_details_attr': 'class',
        'prod_class_name_or_value': 'pd__wrapper',
        'price_tag_type': 'div',
        'price_tag_attr': 'data-test-id',
        'price_class_name_or_value': 'pd-retail-price',
        'promo_tag_type': 'a',
        'promo_tag_attr': 'class',
        'promo_class_name_or_value': 'promotion-message__link',
        'pause_for_class_name': 'pd__cost__per-unit',        # id = pd-unit-price
        'modal_button_class': ''
    }
    morrisons_tags = {
        'link_prefix': 'https://groceries.morrisons.com/products/{0}',
        'prod_details_type': 'section',
        'prod_details_attr': 'class',
        'prod_class_name_or_value': 'bop-section bop-basicInfo',
        'price_tag_type': 'meta',
        'price_tag_attr': 'itemprop',
        'price_class_name_or_value': 'price',
        'promo_tag_type': 'p',
        'promo_tag_attr': 'class',
        'promo_class_name_or_value': 'bop-promotion__description',
        'pause_for_class_name': 'ft-footer',
        'pause_for_element_id': 'productInformation',
        'modal_button_class': ''        # id = onetrust-accept-btn-handler
    }
    asda_tags = {
        'link_prefix': 'https://groceries.asda.com/product/{0}',
        'prod_details_type': 'div',
        'prod_details_attr': 'class',
        'prod_class_name_or_value': 'pdp-main-details',
        'price_tag_type': 'strong',
        'price_tag_attr': 'class',
        'price_class_name_or_value': 'co-product__price pdp-main-details__price',
        'promo_tag_type': 'span',
        'promo_tag_attr': 'class',
        'promo_class_name_or_value': 'co-product__promo-text',
        'pause_for_class_name': 'pdp-main-details__price-container',
        'pause_for_element_id': '',
        'modal_button_class': ''
    }
    tesco_tags = {
        'link_prefix': 'https://www.tesco.com/groceries/en-GB/products/{0}',
        'prod_details_type': 'div',
        'prod_details_attr': 'class',
        'prod_class_name_or_value': 'product-details-tile__main',
        'price_tag_type': 'div',
        'price_tag_attr': 'class',
        'price_class_name_or_value': 'price-per-sellable-unit price-per-sellable-unit--price price-per-sellable-unit--price-per-item',
        'promo_tag_type': 'div',
        'promo_tag_attr': 'class',
        'promo_class_name_or_value': 'list-item-content promo-content-small',
        'pause_for_class_name': 'price-details--wrapper',
        'pause_for_element_id': '',
        'modal_button_class': ''
    }
    waitrose_tags = {
        'link_prefix': 'https://www.waitrose.com/ecom/products/{0}',
        'prod_details_type': 'section',
        'prod_details_attr': 'class',
        'prod_class_name_or_value': 'productDetailContainer___3jFlc',
        'price_tag_type': 'span',
        'price_tag_attr': 'data-test',
        'price_class_name_or_value': 'product-pod-price',
        'promo_tag_type': 'span',
        'promo_tag_attr': 'class',
        'promo_class_name_or_value': 'offerDescription___1A6Ew underline___2kMYl',
        'pause_for_class_name': '',
        'pause_for_element_id': 'fullDetails',
        'modal_button_class': 'button___1TVlR secondary___GAGEQ'
    }
    superdrug_tags = {
        'link_prefix': 'https://www.superdrug.com/{0}',
        'prod_details_type': 'div',
        'prod_details_attr': 'class',
        'prod_class_name_or_value': 'content-wrapper pdp',
        'price_tag_type': 'span',
        'price_tag_attr': 'itemprop',
        'price_class_name_or_value': 'price',
        'promo_tag_type': 'a',
        'promo_tag_attr': 'class',
        'promo_class_name_or_value': 'promotion__item',
        'pause_for_class_name': 'bvRatingReview',
        'pause_for_element_id': '',
        'modal_button_class': ''
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
        'prod_details_type': 'div',
        'prod_details_attr': 'id',
        'prod_class_name_or_value': 'estore_pdp_trcol',
        'price_tag_type': 'div',
        'price_tag_attr': 'id',
        'price_class_name_or_value': 'PDP_productPrice',
        'promo_tag_type': 'li',
        'promo_tag_attr': 'class',
        'promo_class_name_or_value': 'pdp-promotion-redesign',
        'pause_for_class_name': 'global-footer',
        'pause_for_element_id': '',
        'modal_button_class': ''
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
            # skip rows beginning with a hash
            if row[0][0] == '#':
                yield ''
            else:
                yield row


class ProductWrapper:
    def extract_wrappers(self, shop_attribs_dict, product_link):
        try:
            # navigate to the grocery item site
            this.driver.get(product_link)
#           if shop_attribs_dict['modal_button_class'] != '':
#                modal_cookie_button = this.driver.find_element_by_class_name(shop_attribs_dict['modal_button_class'])
#                modal_cookie_button.click()

            if shop_attribs_dict['pause_for_class_name'] != '':
                element_present = EC.presence_of_element_located((By.CLASS_NAME, shop_attribs_dict['pause_for_class_name']))
            elif shop_attribs_dict['pause_for_element_id'] != '':
                element_present = EC.presence_of_element_located((By.ID, shop_attribs_dict['pause_for_element_id']))
            WebDriverWait(this.driver, timeout).until(element_present)
            soup = BeautifulSoup(this.driver.page_source, 'html.parser')
            prod_wrapper = soup.find(shop_attribs_dict['prod_details_type'],
                                   attrs={shop_attribs_dict['prod_details_attr']: shop_attribs_dict['prod_class_name_or_value']})
            prod_string = "".join(str(x) for x in prod_wrapper.contents)
            prod_soup = BeautifulSoup(prod_string, 'html.parser')

            price_wrapper = self.get_price_wrapper(prod_soup, shop_attribs_dict)
            promo_wrapper =  self.get_promo_wrapper(prod_soup, shop_attribs_dict)

            output = price_wrapper, promo_wrapper
        except Exception as e:
            print('Error in extract_wrappers: ', e)
            output = None, None

        return output

    def get_price_wrapper(self, prod_soup, shop_attribs_dict):
        try:
            price_wrapper = prod_soup.find(shop_attribs_dict['price_tag_type'],
                                           attrs={shop_attribs_dict['price_tag_attr']: shop_attribs_dict[
                                               'price_class_name_or_value']})
        except:
            price_wrapper = None

        return price_wrapper

    def get_promo_wrapper(self, prod_soup, shop_attribs_dict):
        try:
            promo_wrapper = prod_soup.find(shop_attribs_dict['promo_tag_type'],
                                           attrs={shop_attribs_dict['promo_tag_attr']: shop_attribs_dict[
                                               'promo_class_name_or_value']})
        except:
            promo_wrapper = None

        return promo_wrapper

    def get_price(self, prod_wrapper):
        try:
            # prod_wrapper is a tuple comprising price and offer
            price_wrapper = prod_wrapper[0]
            if price_wrapper is None:
                price = 'Unable to locate price wrapper'
            else:
                price = '£' + re.findall(r'(\d+\.\d+|\d+)', str(price_wrapper))[0]
        except TimeoutException:
            price = 'Unable to retrieve price - timeout'
        except IndexError:
            price = 'Unable to retrieve price'

        return price.strip()

    def get_promo(self, prod_wrapper):
        try:
            # prod_wrapper is a tuple comprising price and offer
            promo_wrapper = prod_wrapper[1]
            if (promo_wrapper is None) or (len(promo_wrapper.text.strip()) == 0):
                promo = ''
            else:
                promo = ' - Offer - ' + promo_wrapper.text
        except:
            promo = ''

        return promo.strip()

def write_output(price_list):
    with open("price_check.txt", "w", encoding='utf8') as file:
        date = datetime.datetime.now().date()
        hour = datetime.datetime.now().hour
        minute = datetime.datetime.now().minute
        file.write('{} {:02d}:{:02d}\n'.format(date, hour, minute))
        file.write(price_list)

def main():
    this.all_tags = build_supermarket_attribs()

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window_size=1420,1080')
    #chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')

    this.driver = webdriver.Chrome(options=chrome_options)

    output = ''
    product_wrapper = ProductWrapper()

    price_data = get_product_detail_row('price_links.csv')

    for product_item in price_data:
        if product_item != '':
            shop, product_type, product_stub = product_item
            shop_attribs_dict = get_shop_attribs_dict(shop)

            product_link = build_product_link(shop_attribs_dict['link_prefix'], product_stub)

            wrappers = product_wrapper.extract_wrappers(shop_attribs_dict, product_link)
            price = product_wrapper.get_price(wrappers)
            promo = product_wrapper.get_promo(wrappers)

            output += '{0}, {1}: {2} {3}\n'.format(shop.title(), product_type.title(), price, promo)

    write_output(output)

    this.driver.quit()


main()
