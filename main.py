from dotenv import load_dotenv
import os
import platform
import re
import sys
import csv
import mysql.connector as msq
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome import service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

this = sys.modules[__name__]
this.all_tags = {}
this.driver = ''
this.db_connection = ''
this.db_cursor = ''

timeout = 3

def clean_text(text_to_clean, remove_brackets=False):
    output = text_to_clean.strip()
    output = output.replace('\t', '').replace('\n', '').replace('\r', '').replace('  ', '')

    if remove_brackets:
        output.replace('(', '').replace(')', '')

    return output

def get_db_connection(host, port, db_name, username, password):
    this.db_connection = msq.connect(host=host,
                             port=port,
                             unix_socket="/run/mysqld/mysqld10.sock",
                             database=db_name,
                             user=username,
                             password=password)
    this.db_cursor = this.db_connection.cursor()
    return

def execute_sql(sql, with_header):
    this.db_cursor.execute(sql)

    # fetchall outputs the data in the form of a list of tuples
    if with_header:
        results = [this.db_cursor.column_names] + this.db_cursor.fetchall()
    else:
        results = this.db_cursor.fetchall()

    return results

def build_retailer_attribs():
    sm_attribs = execute_sql("SELECT * FROM vw_retailer", False)
    output = {}

    for sm_attrib in sm_attribs:
        (retailer_id,
        retailer_name,
        link_prefix,
        prod_details_type,
        prod_details_attr,
        prod_class_name_or_value,
        price_tag_type,
        price_tag_attr,
        price_class_name_or_value,
        price_per_tag_type,
        price_per_tag_attr,
        price_per_class_name_or_value,
        promo_tag_type,
        promo_tag_attr,
        promo_class_name_or_value,
        pause_for_class_name,
        pause_for_element_id,
        modal_button_class, _ ) = sm_attrib
        output[retailer_name] = {
            'retailer_id': retailer_id,
            'link_prefix': link_prefix,
            'prod_details_type': prod_details_type,
            'prod_details_attr': prod_details_attr,
            'prod_class_name_or_value': prod_class_name_or_value,
            'price_tag_type': price_tag_type,
            'price_tag_attr': price_tag_attr,
            'price_class_name_or_value': price_class_name_or_value,
            'price_per_tag_type': price_per_tag_type,
            'price_per_tag_attr': price_per_tag_attr,
            'price_per_class_name_or_value': price_per_class_name_or_value,
            'promo_tag_type': promo_tag_type,
            'promo_tag_attr': promo_tag_attr,
            'promo_class_name_or_value': promo_class_name_or_value,
            'pause_for_class_name': pause_for_class_name,
            'pause_for_element_id': pause_for_element_id,
            'modal_button_class': modal_button_class
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

def get_retailer_product_by_category():
    price_date = datetime.today().strftime('%Y-%m-%d')
    args = (price_date,)

    this.db_cursor.execute('SELECT * FROM vw_retailer_product_select;')
    this.db_cursor.fetchall()
    return

def coalesce(*arg):
    return next((a for a in arg if a is not None), None)

def price_to_number(price):
    if price.startswith('£'):
        price_value = float(price[1:])
    elif price.endswith('p'):
        price_value = float(price[:-1])
    else:
        price_value = price

    return price_value

class ProductWrapper:
    def extract_wrappers(self, shop_attribs_dict, product_link):
        try:
            # navigate to the grocery item site
            this.driver.get(product_link)
#           if shop_attribs_dict['modal_button_class'] != '':
#                modal_cookie_button = this.driver.find_element_by_class_name(shop_attribs_dict['modal_button_class'])
#                modal_cookie_button.click()

            # The class or element here is used to allow enough of the page to load
            # that we could be sure of extracting the details we need
            if shop_attribs_dict['pause_for_class_name'] != '':
                element_present = EC.presence_of_element_located((By.CLASS_NAME, shop_attribs_dict['pause_for_class_name']))
            elif shop_attribs_dict['pause_for_element_id'] != '':
                element_present = EC.presence_of_element_located((By.ID, shop_attribs_dict['pause_for_element_id']))
            WebDriverWait(this.driver, timeout).until(element_present)
            soup = BeautifulSoup(this.driver.page_source, 'html.parser')
#            prod_wrapper = soup.find(shop_attribs_dict['prod_details_type'],
#                                   attrs={shop_attribs_dict['prod_details_attr']: shop_attribs_dict['prod_class_name_or_value']})
#            prod_string = "".join(str(x) for x in prod_wrapper.contents)
#            prod_soup = BeautifulSoup(prod_string, 'html.parser')

#            price_wrapper = self.get_price_wrapper(prod_soup, shop_attribs_dict)
#            price_per_wrapper = self.get_price_per_wrapper(prod_soup, shop_attribs_dict)
#            promo_wrapper =  self.get_promo_wrapper(prod_soup, shop_attribs_dict)
            price_wrapper = self.get_price_wrapper(soup, shop_attribs_dict)
            price_per_wrapper = self.get_price_per_wrapper(soup, shop_attribs_dict)
            promo_wrapper =  self.get_promo_wrapper(soup, shop_attribs_dict)

            output = price_wrapper, price_per_wrapper, promo_wrapper
        except Exception as e:
            print('Error in extract_wrappers: ', e)
            output = None, None, None

        return output

    def get_price_wrapper(self, prod_soup, shop_attribs_dict):
        try:
            price_wrapper = prod_soup.find(shop_attribs_dict['price_tag_type'],
                                           attrs={shop_attribs_dict['price_tag_attr']: shop_attribs_dict[
                                               'price_class_name_or_value']})
        except Exception as e:
            print('Error in get_price_wrapper: ', e)
            price_wrapper = None

        return price_wrapper

    def get_promo_wrapper(self, prod_soup, shop_attribs_dict):
        try:
            promo_wrapper = prod_soup.find(shop_attribs_dict['promo_tag_type'],
                                           attrs={shop_attribs_dict['promo_tag_attr']: shop_attribs_dict[
                                               'promo_class_name_or_value']})
        except Exception as e:
            print('Error in get_promo_wrapper: ', e)
            promo_wrapper = None

        return promo_wrapper

    def get_price_per_wrapper(self, prod_soup, shop_attribs_dict):
        try:
            price_per_wrapper = prod_soup.find(shop_attribs_dict['price_per_tag_type'],
                                               attrs={shop_attribs_dict['price_per_tag_attr']: shop_attribs_dict['price_per_class_name_or_value']})
        except Exception as e:
            print('Error in get_price_per_wrapper: ', e)
            price_per_wrapper = None

        return price_per_wrapper

    def get_price(self, price_wrapper):
        try:
            if price_wrapper is None:
                price_pounds = 0
                price_pence = 0
            else:
                # Attempt to match pattern £33.33
                if len(price_wrapper.text) > 0:
                    price_wrapper_text = price_wrapper.text
                elif len(price_wrapper['content']) > 0:
                    price_wrapper_text = price_wrapper['content']
                elif len(price_wrapper.span.text)>0:
                    price_wrapper_text = price_wrapper.span.text
                else:
                    print('Unable to extract price from wrapper')
                    price_wrapper_text = ''

                price_pounds_match = re.search(r'(£?((\d+\.\d{1,2})|(\d+)))', price_wrapper_text)
                
                if price_pounds_match:
                    price_pounds = float(price_to_number(price_pounds_match.group()))
                    price_pence = 0
                else:
                    # Attempt to match pattern 33p
                    price_pence_match = re.search(r'((\d{1,2}+p?))', price_wrapper.text)
                    if price_pence_match:
                        price_pounds = 0
                        price_pence = float(price_to_number(price_pence_match.group()))

        except Exception as e:
            print('Error in get_price: ', e)
            price_pounds = 0
            price_pence = 0
            
        price = coalesce(price_pounds, price_pence, 0)

        return price

    def get_price_per(self, price_per_wrapper):
        try:
            if price_per_wrapper is None:
                price_per = 0
            else:
                #price_per = float(re.search(r'(\d+\.\d+|\d+)', str(price_per_wrapper)).group())
                price_per = clean_text(price_per_wrapper.text, True)

        except Exception as e:
            print('Error in get_price: ', e)
            price = 0

        return price_per

    def get_promo(self, promo_wrapper):
        try:
            if (promo_wrapper is None):
                promo = ''
            else:
                promo = clean_text(promo_wrapper.text)
                if len(promo) == 0:
                    promo = ''
        except:
            promo = ''

        return promo

    def get_tesco_promo_price(self, promo_text):
        try:
            # Tesco-specific text
            # £2.50 Clubcard PriceOffer [...]
            tesco_promo_price = re.search(r'(£\d{1,2}(\.\d{2})?)|(\d{2}p)', promo_text)
            tesco_promo_price_value = price_to_number(tesco_promo_price.group())
        except:
            tesco_promo_price_value = None

        return tesco_promo_price_value

    def get_multibuy_promo_price(self, promo_text):
        try:
            # Used by Morrisons, Asda & Tesco
            # (Any/Buy) 3 for £4.25 [...]
            multibuy_text = re.search(r'\d{1} for (£\d{1,2}(\.\d{2})?)', promo_text).group()
            quantity = float(multibuy_text.split(' for £')[0])
            total_promo_cost = float(multibuy_text.split(' for £')[1])
            multibuy_promo_price = total_promo_cost / quantity
        except:
            multibuy_promo_price = None

        return multibuy_promo_price

    def get_promo_price(self, promo_text):
        promo_price = coalesce(self.get_multibuy_promo_price(promo_text), self.get_tesco_promo_price(promo_text))

        return promo_price

    def get_offer_dates(self, promo_text):

        date_format_dmy = '%d/%m/%Y'
        date_format_ymd = '%Y-%m-%d'
        try:
            if len(promo_text)==0:
                offer_start_date = '2000-01-01'
                offer_end_date = '2000-01-01'
            else:
                # Find all matches for dd/mm/yyyy and sort them
                offer_dates = re.findall(r'\d{2}\/\d{2}\/\d{4}', promo_text)

                if offer_dates is None or len(offer_dates)==0:
                    # No dates found, but there is a promo, so there is an
                    # offer start date at least, i.e. today
                    offer_start_date = datetime.today().strftime(date_format_ymd)
                    offer_end_date = '2000-01-01'
                elif len(offer_dates)==1:
                    # Just one date found, so probably the end date
                    offer_start_date = datetime.today().strftime(date_format_ymd)
                    offer_end_date = datetime.strptime(offer_dates[0], date_format_dmy).strftime(date_format_ymd)
                elif len(offer_dates)>1:
                    # Two or more dates found, so probably the start & end dates
                    offer_start_date = datetime.strptime(offer_dates[0], date_format_dmy).strftime(date_format_ymd)
                    offer_end_date = datetime.strptime(offer_dates[1], date_format_dmy).strftime(date_format_ymd)
        except:
            # Prepare for duff/null dates within promo text
            offer_start_date = '2000-01-01'
            offer_end_date = '2000-01-01'

        return offer_start_date, offer_end_date

def write_output(price_list):
    with open("./price_check.txt", "w", encoding='utf8') as file:
        date = datetime.datetime.now().date()
        hour = datetime.datetime.now().hour
        minute = datetime.datetime.now().minute
        file.write('{} {:02d}:{:02d}\n'.format(date, hour, minute))
        file.write(price_list)

def main():
    load_dotenv()
    get_db_connection(os.environ.get('ps_host'),
                        os.environ.get('ps_port'),
                        os.environ.get('ps_db_name'),
                        os.environ.get('ps_username'),
                        os.environ.get('ps_password'))

    this.all_tags = build_retailer_attribs()

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window_size=1420,1080')
#    chrome_options.add_argument('--disable-gpu')
    
    # Enabling this option blocks Sainsbury's prices
    #chrome_options.add_argument('--headless')

    this_os = platform.system()
    if this_os == 'Linux':
        chrome_exe_name = './chromedriver'
    elif this_os == 'Windows':
        chrome_exe_name = '.\chromedriver.exe'

    s = Service(chrome_exe_name)

    this.driver = webdriver.Chrome(options=chrome_options, service=s)

    output = ''
    product_wrapper = ProductWrapper()

    if len(sys.argv)==2 and sys.argv[1].isnumeric():
        where_category_id = '= ' + sys.argv[1]
    else:
        where_category_id = '>=0'
    retailer_products = execute_sql('SELECT * FROM vw_retailer_product_select WHERE category_id {}'.format(where_category_id), False)

    for retailer_product in retailer_products:
        (category_id,
         retailer_product_id,
         product_id,
         product_name,
         retailer_id,
         retailer_name,
         product_link_suffix) = retailer_product

        shop_attribs_dict = get_shop_attribs_dict(retailer_name)
        product_link = shop_attribs_dict['link_prefix'] + product_link_suffix

#        wrappers = product_wrapper.extract_wrappers(shop_attribs_dict, product_link)
        price_wrapper, price_per_wrapper, promo_wrapper = product_wrapper.extract_wrappers(shop_attribs_dict, product_link)

        # Some promo prices need to be extracted from promo text
        promo_text = product_wrapper.get_promo(promo_wrapper)
        promo_price = product_wrapper.get_promo_price(promo_text)
        non_promo_price = product_wrapper.get_price(price_wrapper)
        price = coalesce(promo_price, non_promo_price)
        price_per = product_wrapper.get_price_per(price_per_wrapper)

        current_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        offer_start_date, offer_end_date = product_wrapper.get_offer_dates(promo_text)

        arg_list = (retailer_product_id, current_time, price, price_per, promo_text, offer_start_date, offer_end_date)

        this.db_cursor.callproc('usp_price_upsert', arg_list)
        this.db_connection.commit()


    this.driver.quit()

main()