import platform
import re
import sys
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
    
    # Enabling this option blocks Sainsbury's prices
    #chrome_options.add_argument('--headless')

    this_os = platform.system()
    if this_os == 'Linux':
        chrome_exe_name = './chromedriver'
    elif this_os == 'Windows':
        chrome_exe_name = '.\chromedriver.exe'

    s = Service(chrome_exe_name)

    return webdriver.Chrome(options=chrome_options, service=s)

def get_urls():
    this = sys.modules[__name__]
    this.driver = get_browser_session()
    timeout = 3

    # Lots of URLs for the four main supermarkets
    urls = [
        'https://groceries.asda.com/aisle/price-locked/view-all-price-locked/view-all-price-locked/1215686354018-1215686354019-1215686354020?page=1',
        'https://groceries.asda.com/aisle/price-locked/view-all-price-locked/view-all-price-locked/1215686354018-1215686354019-1215686354020?page=2',
        'https://groceries.asda.com/aisle/price-locked/view-all-price-locked/view-all-price-locked/1215686354018-1215686354019-1215686354020?page=3',
        'https://groceries.asda.com/aisle/price-locked/view-all-price-locked/view-all-price-locked/1215686354018-1215686354019-1215686354020?page=4',
        'https://groceries.asda.com/aisle/price-locked/view-all-price-locked/view-all-price-locked/1215686354018-1215686354019-1215686354020?page=5',
        'https://groceries.asda.com/aisle/price-locked/view-all-price-locked/view-all-price-locked/1215686354018-1215686354019-1215686354020?page=6',
        'https://groceries.asda.com/aisle/price-locked/view-all-price-locked/view-all-price-locked/1215686354018-1215686354019-1215686354020?page=7',
        'https://groceries.asda.com/aisle/price-locked/view-all-price-locked/view-all-price-locked/1215686354018-1215686354019-1215686354020?page=8',
        'https://groceries.asda.com/aisle/price-match/view-all-price-match/view-all-price-match/1215686354045-1215686354052-1215686354053?page=1',
        'https://groceries.asda.com/aisle/price-match/view-all-price-match/view-all-price-match/1215686354045-1215686354052-1215686354053?page=2',
        'https://groceries.asda.com/aisle/price-match/view-all-price-match/view-all-price-match/1215686354045-1215686354052-1215686354053?page=3',
        'https://groceries.asda.com/aisle/bakery/bread-rolls/bread/1215686354843-1215686354847-1215686354871?page=1',
        'https://groceries.asda.com/aisle/bakery/bread-rolls/bread/1215686354843-1215686354847-1215686354871?page=2',
        'https://groceries.asda.com/aisle/bakery/bread-rolls/bread/1215686354843-1215686354847-1215686354871?page=3',
        'https://groceries.asda.com/aisle/bakery/bread-rolls/bread/1215686354843-1215686354847-1215686354871?page=4',
        'https://groceries.asda.com/aisle/meat-poultry-fish/meat-poultry/chicken-turkey/1215135760597-910000975206-910000975462?page=1',
        'https://groceries.asda.com/aisle/meat-poultry-fish/meat-poultry/chicken-turkey/1215135760597-910000975206-910000975462?page=2',
        'https://groceries.asda.com/aisle/meat-poultry-fish/meat-poultry/chicken-turkey/1215135760597-910000975206-910000975462?page=3',
        'https://groceries.asda.com/aisle/meat-poultry-fish/meat-poultry/chicken-turkey/1215135760597-910000975206-910000975462?page=4',
        'https://groceries.asda.com/aisle/meat-poultry-fish/meat-poultry/beef/1215135760597-910000975206-910000975528?page=1',
        'https://groceries.asda.com/aisle/meat-poultry-fish/meat-poultry/beef/1215135760597-910000975206-910000975528?page=2',
        'https://groceries.asda.com/aisle/meat-poultry-fish/meat-poultry/beef/1215135760597-910000975206-910000975528?page=3',
        'https://groceries.asda.com/aisle/meat-poultry-fish/meat-poultry/bacon-sausages-gammon/1215135760597-910000975206-910000975529?page=1',
        'https://groceries.asda.com/aisle/meat-poultry-fish/meat-poultry/bacon-sausages-gammon/1215135760597-910000975206-910000975529?page=2',
        'https://groceries.asda.com/aisle/meat-poultry-fish/meat-poultry/bacon-sausages-gammon/1215135760597-910000975206-910000975529?page=3',
        'https://groceries.asda.com/aisle/meat-poultry-fish/meat-poultry/bacon-sausages-gammon/1215135760597-910000975206-910000975529?page=4',
        'https://groceries.asda.com/aisle/meat-poultry-fish/meat-poultry/pork/1215135760597-910000975206-910000975676?page=1',
        'https://groceries.asda.com/aisle/meat-poultry-fish/meat-poultry/pork/1215135760597-910000975206-910000975676?page=2',
        'https://groceries.asda.com/aisle/meat-poultry-fish/meat-poultry/lamb/1215135760597-910000975206-910000975607',
        'https://groceries.asda.com/aisle/meat-poultry-fish/fish-seafood/salmon/1215135760597-1215337195095-1215685901159',
        'https://groceries.asda.com/dept/chilled-food/milk-butter-cream-eggs/1215660378320-1215339432024',
        'https://groceries.asda.com/aisle/chilled-food/milk-butter-cream-eggs/fresh-milk/1215660378320-1215339432024-1215339434886',
        'https://groceries.asda.com/aisle/chilled-food/milk-butter-cream-eggs/butter-spreads/1215660378320-1215339432024-1215339437646',
        'https://groceries.asda.com/aisle/chilled-food/milk-butter-cream-eggs/butter-spreads/1215660378320-1215339432024-1215339437646?page=2',
        'https://groceries.asda.com/aisle/chilled-food/milk-butter-cream-eggs/eggs/1215660378320-1215339432024-910000975407',
        'https://groceries.asda.com/aisle/chilled-food/cheese/cheddar-regional-cheese/1215660378320-1215341805721-1215341805765',
        'https://groceries.asda.com/aisle/chilled-food/cheese/cheddar-regional-cheese/1215660378320-1215341805721-1215341805765?page=2',
        'https://groceries.asda.com/aisle/chilled-food/cheese/soft-cottage-cheese/1215660378320-1215341805721-1215341805865',
        'https://groceries.asda.com/dept/chilled-food/cooked-meat/1215660378320-1215661243132',
        'https://groceries.asda.com/dept/chilled-food/yogurts-desserts/1215660378320-1215341888021',
        'https://groceries.asda.com/dept/chilled-food/pizza-pasta-garlic-bread/1215660378320-1215661254820',
        'https://groceries.asda.com/aisle/food-cupboard/christmas-treats-food-cupboard/crisps-nuts-nibbles/1215337189632-1215686355041-1215684243372',
        'https://groceries.asda.com/aisle/food-cupboard/christmas-treats-food-cupboard/gravy-table-sauces-condiments/1215337189632-1215686355041-1215686355054',
        'https://groceries.asda.com/aisle/food-cupboard/christmas-treats-food-cupboard/gravy-table-sauces-condiments/1215337189632-1215686355041-1215686355054?page=2',
        'https://groceries.asda.com/aisle/food-cupboard/rice-pasta-noodles/pasta/1215337189632-1215337189669-1215337189706',
        'https://groceries.asda.com/aisle/food-cupboard/rice-pasta-noodles/dry-rice-noodles-grains/1215337189632-1215337189669-1215337189751',
        'https://groceries.asda.com/aisle/food-cupboard/rice-pasta-noodles/dry-rice-noodles-grains/1215337189632-1215337189669-1215337189751?page=2',
        'https://groceries.asda.com/aisle/food-cupboard/rice-pasta-noodles/dry-rice-noodles-grains/1215337189632-1215337189669-1215337189751?page=3',
        'https://groceries.asda.com/aisle/food-cupboard/rice-pasta-noodles/dry-rice-noodles-grains/1215337189632-1215337189669-1215337189751?page=4',
        'https://groceries.asda.com/aisle/food-cupboard/tinned-food/baked-beans/1215337189632-1215165876400-910000975571',
        'https://groceries.asda.com/aisle/food-cupboard/cereals-cereal-bars/everyday-family-cereals/1215337189632-1215337194729-1215650880276',
        'https://groceries.asda.com/aisle/food-cupboard/cereals-cereal-bars/everyday-family-cereals/1215337189632-1215337194729-1215650880276?page=2',
        'https://groceries.asda.com/aisle/food-cupboard/cereals-cereal-bars/everyday-family-cereals/1215337189632-1215337194729-1215650880276?page=3',
        'https://groceries.asda.com/aisle/food-cupboard/cereals-cereal-bars/everyday-family-cereals/1215337189632-1215337194729-1215650880276?page=4',
        'https://groceries.asda.com/aisle/food-cupboard/cereals-cereal-bars/healthier-cereals/1215337189632-1215337194729-1215650880565',
        'https://groceries.asda.com/aisle/food-cupboard/cereals-cereal-bars/free-from-cereals-bars/1215337189632-1215337194729-1215679678945',
        'https://groceries.asda.com/aisle/food-cupboard/cereals-cereal-bars/on-the-go-breakfast/1215337189632-1215337194729-1215650881169',
        'https://groceries.asda.com/aisle/food-cupboard/cereals-cereal-bars/muesli-granola-crisp/1215337189632-1215337194729-1215650881116',
        'https://groceries.asda.com/aisle/food-cupboard/cereals-cereal-bars/porridge-oats/1215337189632-1215337194729-1215650881414',
        'https://groceries.asda.com/aisle/food-cupboard/cereals-cereal-bars/cereal-bars/1215337189632-1215337194729-1215650887221',
        'https://groceries.asda.com/aisle/food-cupboard/cereals-cereal-bars/cereal-bars/1215337189632-1215337194729-1215650887221?page=2',
        'https://groceries.asda.com/aisle/food-cupboard/cereals-cereal-bars/cereal-bars/1215337189632-1215337194729-1215650887221?page=3',
        'https://groceries.asda.com/aisle/food-cupboard/cereals-cereal-bars/cereal-bars/1215337189632-1215337194729-1215650887221?page=4',
        'https://groceries.asda.com/aisle/food-cupboard/tinned-food/tinned-pulses-lentils/1215337189632-1215165876400-1215664349998',
        'https://groceries.asda.com/aisle/food-cupboard/condiments-cooking-ingredients/popular-brands/1215337189632-1215354523758-1215685991390',
        'https://groceries.asda.com/aisle/food-cupboard/condiments-cooking-ingredients/popular-brands/1215337189632-1215354523758-1215685991390?page=2',
        'https://groceries.asda.com/aisle/food-cupboard/condiments-cooking-ingredients/popular-brands/1215337189632-1215354523758-1215685991390?page=3',
        'https://groceries.asda.com/aisle/food-cupboard/condiments-cooking-ingredients/popular-brands/1215337189632-1215354523758-1215685991390?page=4',
        'https://groceries.asda.com/aisle/food-cupboard/condiments-cooking-ingredients/popular-brands/1215337189632-1215354523758-1215685991390?page=5',
        'https://groceries.asda.com/aisle/food-cupboard/condiments-cooking-ingredients/popular-brands/1215337189632-1215354523758-1215685991390?page=6',
        'https://groceries.asda.com/aisle/food-cupboard/condiments-cooking-ingredients/popular-brands/1215337189632-1215354523758-1215685991390?page=7',
        'https://groceries.asda.com/aisle/food-cupboard/condiments-cooking-ingredients/spices/1215337189632-1215354523758-1215685891284',
        'https://groceries.asda.com/aisle/food-cupboard/condiments-cooking-ingredients/spices/1215337189632-1215354523758-1215685891284?page=2',
        'https://groceries.asda.com/aisle/food-cupboard/condiments-cooking-ingredients/dry-herbs/1215337189632-1215354523758-1215685891282',
        'https://groceries.asda.com/aisle/food-cupboard/condiments-cooking-ingredients/marinades-rubs/1215337189632-1215354523758-910000975508',
        'https://groceries.asda.com/aisle/food-cupboard/condiments-cooking-ingredients/stock/1215337189632-1215354523758-1215685891285',
        'https://groceries.asda.com/aisle/food-cupboard/condiments-cooking-ingredients/stock/1215337189632-1215354523758-1215685891285?page=2',
        'https://groceries.asda.com/aisle/food-cupboard/condiments-cooking-ingredients/sauces-condiments/1215337189632-1215354523758-910000975613',
        'https://groceries.asda.com/aisle/food-cupboard/condiments-cooking-ingredients/sauces-condiments/1215337189632-1215354523758-910000975613?page=2',
        'https://groceries.asda.com/aisle/food-cupboard/condiments-cooking-ingredients/sauces-condiments/1215337189632-1215354523758-910000975613?page=3',
        'https://groceries.asda.com/aisle/food-cupboard/condiments-cooking-ingredients/sauces-condiments/1215337189632-1215354523758-910000975613?page=4',
        'https://groceries.asda.com/aisle/food-cupboard/condiments-cooking-ingredients/sauces-condiments/1215337189632-1215354523758-910000975613?page=5',
        'https://groceries.asda.com/aisle/food-cupboard/jams-spreads-desserts/jams-curds/1215337189632-1215685491665-1215685491666',
        'https://groceries.asda.com/aisle/food-cupboard/jams-spreads-desserts/marmalade/1215337189632-1215685491665-1215685491667',
        'https://groceries.asda.com/aisle/food-cupboard/crisps-nuts-popcorn/tortilla-chips-dips/1215337189632-1215165893478-1215684181120',
        'https://groceries.asda.com/aisle/food-cupboard/crisps-nuts-popcorn/multipack-crisps/1215337189632-1215165893478-1215662199368',
        'https://groceries.asda.com/aisle/food-cupboard/crisps-nuts-popcorn/multipack-crisps/1215337189632-1215165893478-1215662199368?page=2',
        'https://groceries.asda.com/aisle/food-cupboard/crisps-nuts-popcorn/multipack-crisps/1215337189632-1215165893478-1215662199368?page=3',
        'https://groceries.asda.com/aisle/food-cupboard/crisps-nuts-popcorn/multipack-crisps/1215337189632-1215165893478-1215662199368?page=4',
        'https://groceries.asda.com/aisle/food-cupboard/crisps-nuts-popcorn/nuts-dried-fruit/1215337189632-1215165893478-910000975624',
        'https://groceries.asda.com/aisle/food-cupboard/crisps-nuts-popcorn/nuts-dried-fruit/1215337189632-1215165893478-910000975624?page=2',
        'https://groceries.asda.com/aisle/food-cupboard/crisps-nuts-popcorn/nuts-dried-fruit/1215337189632-1215165893478-910000975624?page=3',
        'https://groceries.asda.com/aisle/food-cupboard/crisps-nuts-popcorn/nuts-dried-fruit/1215337189632-1215165893478-910000975624?page=4',
        'https://groceries.asda.com/aisle/food-cupboard/crisps-nuts-popcorn/nuts-dried-fruit/1215337189632-1215165893478-910000975624?page=5'

        # 'https://groceries.morrisons.com/browse/meat-poultry-179549?display=500',
        # 'https://groceries.morrisons.com/browse/fish-seafood-184367?display=500',
        # 'https://groceries.morrisons.com/browse/fruit-veg-176738?display=500',
        # 'https://groceries.morrisons.com/browse/bakery-cakes-102210?display=500',
        # 'https://groceries.morrisons.com/browse/food-cupboard-102705?display=5000',
        # 'https://groceries.morrisons.com/browse/frozen-180331?display=1600',
        # 'https://groceries.morrisons.com/browse/drinks-103644?display=1500',
        # 'https://groceries.morrisons.com/browse/household-102063?display=1600',
        # 'https://groceries.morrisons.com/browse/health-wellbeing-medicines-103497?display=1100',
        # 'https://groceries.morrisons.com/browse/toiletries-beauty-102838?display=3100',
        # 'https://groceries.morrisons.com/browse/world-foods-182137?display=1700'
        # 'https://www.sainsburys.co.uk/shop/gb/groceries/food-cupboard/CategoryDisplay?langId=44&storeId=10151&catalogId=10241&categoryId=135652&orderBy=FAVOURITES_ONLY%7CSEQUENCING%7CTOP_SELLERS&beginIndex=0&promotionId=&listId=&searchTerm=&hasPreviousOrder=&previousOrderId=&categoryFacetId1=&categoryFacetId2=&ImportedProductsCount=&ImportedStoreName=&ImportedSupermarket=&bundleId=&parent_category_rn=12422&top_category=12422&pageSize=120#langId=44&storeId=10151&catalogId=10241&categoryId=135652&parent_category_rn=12422&top_category=12422&pageSize=120&orderBy=FAVOURITES_ONLY%7CSEQUENCING%7CTOP_SELLERS&searchTerm=&beginIndex=0&hideFilters=true',
        # 'https://www.sainsburys.co.uk/shop/CategoryDisplay?listId=&catalogId=10241&searchTerm=&beginIndex=120&pageSize=120&orderBy=FAVOURITES_ONLY%7CSEQUENCING%7CTOP_SELLERS&top_category=12422&langId=44&storeId=10151&categoryId=135652&promotionId=&parent_category_rn=12422',
        # 'https://www.sainsburys.co.uk/shop/CategoryDisplay?listId=&catalogId=10241&searchTerm=&beginIndex=240&pageSize=120&orderBy=FAVOURITES_ONLY%7CSEQUENCING%7CTOP_SELLERS&top_category=12422&langId=44&storeId=10151&categoryId=135652&promotionId=&parent_category_rn=12422',
        # 'https://www.sainsburys.co.uk/shop/gb/groceries/food-cupboard/CategoryDisplay?langId=44&storeId=10151&catalogId=10241&categoryId=557354&orderBy=FAVOURITES_ONLY%7CSEQUENCING%7CTOP_SELLERS&beginIndex=0&promotionId=&listId=&searchTerm=&hasPreviousOrder=&previousOrderId=&categoryFacetId1=&categoryFacetId2=&ImportedProductsCount=&ImportedStoreName=&ImportedSupermarket=&bundleId=&parent_category_rn=12422&top_category=12422&pageSize=120#langId=44&storeId=10151&catalogId=10241&categoryId=557354&parent_category_rn=12422&top_category=12422&pageSize=120&orderBy=FAVOURITES_ONLY%7CSEQUENCING%7CTOP_SELLERS&searchTerm=&beginIndex=0&hideFilters=true&facet=',
        # 'https://www.sainsburys.co.uk/shop/CategoryDisplay?listId=&catalogId=10241&searchTerm=&beginIndex=120&pageSize=120&orderBy=FAVOURITES_ONLY%7CSEQUENCING%7CTOP_SELLERS&top_category=12422&langId=44&storeId=10151&categoryId=557354&promotionId=&parent_category_rn=12422',
        # 'https://www.sainsburys.co.uk/shop/CategoryDisplay?listId=&catalogId=10241&searchTerm=&beginIndex=240&pageSize=120&orderBy=FAVOURITES_ONLY%7CSEQUENCING%7CTOP_SELLERS&top_category=12422&langId=44&storeId=10151&categoryId=557354&promotionId=&parent_category_rn=12422'
        #'https://www.sainsburys.co.uk/shop/gb/groceries/food-cupboard/CategoryDisplay?langId=44&storeId=10151&catalogId=10241&categoryId=442362&orderBy=FAVOURITES_ONLY%7CSEQUENCING%7CTOP_SELLERS&beginIndex=0&promotionId=&listId=&searchTerm=&hasPreviousOrder=&previousOrderId=&categoryFacetId1=&categoryFacetId2=&ImportedProductsCount=&ImportedStoreName=&ImportedSupermarket=&bundleId=&parent_category_rn=12422&top_category=12422&pageSize=120#langId=44&storeId=10151&catalogId=10241&categoryId=442362&parent_category_rn=12422&top_category=12422&pageSize=120&orderBy=FAVOURITES_ONLY%7CSEQUENCING%7CTOP_SELLERS&searchTerm=&beginIndex=0&hideFilters=true'
        # 'https://www.sainsburys.co.uk/shop/gb/groceries/food-cupboard/CategoryDisplay?langId=44&storeId=10151&catalogId=10241&categoryId=442361&orderBy=FAVOURITES_ONLY%7CSEQUENCING%7CTOP_SELLERS&beginIndex=0&promotionId=&listId=&searchTerm=&hasPreviousOrder=&previousOrderId=&categoryFacetId1=&categoryFacetId2=&ImportedProductsCount=&ImportedStoreName=&ImportedSupermarket=&bundleId=&parent_category_rn=12422&top_category=12422&pageSize=120#langId=44&storeId=10151&catalogId=10241&categoryId=442361&parent_category_rn=12422&top_category=12422&pageSize=120&orderBy=FAVOURITES_ONLY%7CSEQUENCING%7CTOP_SELLERS&searchTerm=&beginIndex=0',
        # 'https://www.sainsburys.co.uk/shop/CategoryDisplay?listId=&catalogId=10241&searchTerm=&beginIndex=120&pageSize=120&orderBy=FAVOURITES_ONLY%7CSEQUENCING%7CTOP_SELLERS&top_category=12422&langId=44&storeId=10151&categoryId=442361&promotionId=&parent_category_rn=12422',
        # 'https://www.sainsburys.co.uk/shop/CategoryDisplay?listId=&catalogId=10241&searchTerm=&beginIndex=240&pageSize=120&orderBy=FAVOURITES_ONLY%7CSEQUENCING%7CTOP_SELLERS&top_category=12422&langId=44&storeId=10151&categoryId=442361&promotionId=&parent_category_rn=12422',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=1&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=2&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=3&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=4&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=5&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=6&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=7&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=8&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=9&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=10&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=11&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=12&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=13&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=14&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=15&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=16&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=17&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=18&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=19&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=20&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=21&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=22&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=23&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=24&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=25&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=26&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=27&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=28&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=29&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=30&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=31&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=32&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=33&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=34&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=35&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=36&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=37&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=38&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=39&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=40&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=41&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=42&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=43&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=44&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=45&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=46&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=47&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=48&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=49&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=50&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=51&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=52&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=53&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=54&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=55&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=56&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=57&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=58&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=59&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=60&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=61&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=62&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=63&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=64&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=65&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=66&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=67&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=68&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=69&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=70&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=71&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=72&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=73&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=74&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=75&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=76&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=77&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=78&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=79&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=80&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=81&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=82&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=83&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=84&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=85&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=86&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=87&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=88&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=89&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=90&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=91&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=92&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=93&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=94&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=95&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=96&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=97&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=98&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=99&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=100&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=101&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=102&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=103&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=104&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=105&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=106&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=107&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=108&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=109&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=110&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=111&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=112&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=113&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=114&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=115&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=116&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=117&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=118&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=119&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=120&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=121&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=122&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=123&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=124&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=125&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=126&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=127&count=48',
        # 'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?page=128&count=48'
    ]

    # Sainsburys has full link but Tesco, Morrisons & Asda category pages only have relative links
    link_matches = {
        'https://www.sainsburys.co.uk/shop/gb/groceries/product/details/' : 'https://www.sainsburys.co.uk/shop/gb/groceries/product/details/',
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
        element_present = EC.presence_of_element_located((By.CLASS_NAME, 'footer__container'))
        WebDriverWait(this.driver, timeout).until(element_present)
        
        soup = BeautifulSoup(this.driver.page_source, 'html.parser')
    
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
    f = open("urls.txt", "a")
    f.writelines(output_urls)
    f.close()


get_urls()