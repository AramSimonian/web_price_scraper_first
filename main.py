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

sains = {
    'name': 'Sains',
    'site': 'https://www.sainsburys.co.uk/shop/gb/groceries/product/details/new-york-bakery-co-cinnamon---raisin-bagels-x5',
    'tag_type': 'div',
    'tag_id': 'pd-retail-price',
    'tag_attr': 'class',
    'class_name': 'pd__cost__total--promo undefined',
    'pause_for_class_name': 'pd__cost__per-unit'
    }
morrisons = {
    'name': 'Morrisons',
    'site': 'https://groceries.morrisons.com/webshop/product/New-York-Bagel-Co-Cinnamon--Raisin/114353011',
    'tag_type': 'meta',
    'tag_id': '',
    'tag_attr': 'itemprop',
    'class_name': 'price',
    'pause_for_class_name': 'bop-price__wrapper'
    }
asda = {
    'name': 'Asda',
    'site': 'https://groceries.asda.com/product/bagels/new-york-bakery-co-cinnamon-raisin-bagels/1000004372338',
    'tag_type': 'strong',
    'tag_id': '',
    'tag_attr': 'class',
    'class_name': 'co-product__price pdp-main-details__price',
    'pause_for_class_name': 'pdp-main-details__price-container'
    }
tesco = {
    'name': 'Tesco',
    'site': 'https://www.tesco.com/groceries/en-GB/products/253829047',
    'tag_type': 'div',
    'tag_id': '',
    'tag_attr': 'class',
    'class_name': 'price-per-sellable-unit price-per-sellable-unit--price price-per-sellable-unit--price-per-item',
    'pause_for_class_name': 'price-details--wrapper'
    }

#sains
#<div data-test-id="pd-retail-price" class="pd__cost__total--promo undefined">£1.20</div>
##asda
#<strong class="co-product__price pdp-main-details__price">£1.00</strong>
#tesco
#https://www.tesco.com/groceries/en-GB/products/253829047
#<span data-auto="price-value" class="value">1.00</span>

bagels = [sains, morrisons, asda, tesco]

#chrome_options = Options()  
#chrome_options.add_argument("--headless")
#driver = webdriver.Chrome(chrome_options=chrome_options)

#options = webdriver.ChromeOptions()
#options.add_argument('headless')

driver = webdriver.Chrome()

output = 'Bagels:\n'

for bagel in bagels:
    driver.get(bagel['site'])
    #time.sleep(timeout)
    try:
        element_present = EC.presence_of_element_located((By.CLASS_NAME, bagel['pause_for_class_name']))
        WebDriverWait(driver, timeout).until(element_present)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        price_box = soup.find(bagel['tag_type'], attrs={bagel['tag_attr']: bagel['class_name']})

        if price_box is None:
            price = ""
        #price = price_box.text.strip()
        else:
            price = re.findall(r'(\d+\.\d{2}|\d+)', str(price_box))[0]

    except TimeoutException:
        price = 'Unable to retrieve price'
    finally:
        output += "{0}: £{1}\n".format(bagel['name'], price)

with open("C:\\Temp\\price_check.txt", "w") as file:
    file.write(output)

#sains
#<div data-test-id="pd-retail-price" class="pd__cost__total--promo undefined">£1.20</div>
#price_box = soup.find('div', attrs={'class': 'pd__cost__total--promo undefined'})
#<div class="pd__cost__total--promo undefined" data-test-id="pd-retail-price">£1.20</div>

#morrisons
#<span class="nowPrice"> £1 </span>
#price_box = soup.find('span', attrs={'class': 'nowPrice'})
#<meta itemprop="price" content="0.77">

#price = price_box.text.strip()
#print("Sainsbury's bagels: " + price)
#print("Morrisons bagels: " + price)
driver.quit()

