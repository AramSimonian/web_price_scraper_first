import platform
import re
import sys
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome import service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

def get_browser_session():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window_size=1420,1080')
#    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--remote-debugging-port=9222")
    
    # Enabling this option blocks Sainsbury's prices
    #chrome_options.add_argument('--headless')

    this_os = platform.system()
    if this_os == 'Linux':
        chrome_exe_name = './chromedriver'
    elif this_os == 'Windows':
        chrome_exe_name = './chromedriver.exe'
        chrome_options.binary_location = 'C:/Temp/web_scraper/GoogleChromePortable/GoogleChromePortable.exe'

    s = Service(chrome_exe_name)

    return webdriver.Chrome(options=chrome_options, service=s)

def get_urls():
    this = sys.modules[__name__]
    this.driver = get_browser_session()
    timeout = 3

    # Lots of URLs for the four main supermarkets
    urls = [
        'https://www.sainsburys.co.uk/gol-ui/SearchResults/nando'
          ]

    # Sainsburys has full link but Tesco, Morrisons & Asda category pages only have relative links
    link_matches = {
        'https://www.sainsburys.co.uk/shop/gb/groceries/product/details/' : 'https://www.sainsburys.co.uk/shop/gb/groceries/product/details/',
        'https://www.sainsburys.co.uk/gol-ui/product/' : 'https://www.sainsburys.co.uk/shop/gb/groceries/product/details/',
        '/groceries/en-GB/products/' : 'https://www.tesco.com',
        '/products/' : 'https://groceries.morrisons.com',
        '/product/' : 'https://groceries.asda.com'
    }

    output_urls = []

    for url in urls:
        # grab = requests.get(url)
        this.driver.get(url)
        
        # This class name will change for each supermarket page
        # <footer class="ft-footer">
        # Tesco         footer__upper
        # Asda          page-navigation__total-items-text  |  footer__container  
        # Sainsburys    footer
        # Morrisons     ft-footer__content
        if url.find('sainsburys') > 0:
            retailer_class_name = 'pagination paginationBottom'
        elif url.find('morrisons') > 0:
            retailer_class_name = 'ft-footer__content'
        elif url.find('tesco') > 0:
            retailer_class_name = 'footer__upper'
        elif url.find('asda') > 0:
            retailer_class_name = 'co-pagination'

        element_present = EC.presence_of_element_located((By.CLASS_NAME, retailer_class_name))
        WebDriverWait(this.driver, timeout).until(element_present)
        
        soup = BeautifulSoup(this.driver.page_source, 'html.parser')
        # soup = BeautifulSoup(r.content, 'html.parser')

        # traverse paragraphs from soup
        for link in soup.find_all("a"):
            data = str(link.get('href'))

            if data:
                
                for link_match in link_matches:
                    if re.match(link_match, data):
                        if data[0] == '/':
                            data = link_matches[link_match] + data

                        output_urls.append(data)
                        exit

    # De-dupe the list and convert to a string
    output_urls = '\n'.join(list(set(output_urls)))

    # opening a file in write mode
    f = open("2023-01-30_urls.txt", "a")
    f.writelines(output_urls)
    f.close()


get_urls()