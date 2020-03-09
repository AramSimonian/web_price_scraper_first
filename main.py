import urllib3
from bs4 import BeautifulSoup

sains_bagel = 'https://www.sainsburys.co.uk/shop/gb/groceries/product/details/new-york-bakery-co-cinnamon---raisin-bagels-x5'
morrisons_bagel = 'https://groceries.morrisons.com/webshop/product/New-York-Bagel-Co-Cinnamon--Raisin/114353011'

http = urllib3.PoolManager()
response = http.request('GET', sains_bagel)
soup = BeautifulSoup(response.data, 'html.parser')

#sains
#<div data-test-id="pd-retail-price" class="pd__cost__total--promo undefined">£1.20</div>
price_box = soup.find('div', attrs={'class': 'pd__cost__total--promo undefined'})

#morrisons
#<span class="nowPrice"> £1 </span>
#price_box = soup.find('span', attrs={'class': 'nowPrice'})

price = price_box.text.strip()
print(price)
