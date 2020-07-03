from main import ProductWrapper
from selenium import webdriver
import unittest

class Test_price_wrapper(unittest.TestCase):
    
    #def sainsburys_tags():
    #    output = {
    #        'link_prefix': 'https://www.sainsburys.co.uk/shop/gb/groceries/product/details/{0}',
    #        'tag_type': 'div',
    #        'tag_attr': 'data-test-id',
    #        'class_name': 'pd-retail-price',
    #        'pause_for_class_name': 'pd__cost__per-unit'
    #        }
    #    return output

    #def morrisons_tags():
    #    output = {
    #        'link_prefix': 'https://groceries.morrisons.com/webshop/product/{0}',
    #        'tag_type': 'meta',
    #        'tag_attr': 'itemprop',
    #        'class_name': 'price',
    #        'pause_for_class_name': 'bop-price__per'
    #        }
    #    return output

    #def asda_tags():
    #    output = {
    #        'link_prefix': 'https://groceries.asda.com/product/{0}',
    #        'tag_type': 'strong',
    #        'tag_attr': 'class',
    #        'class_name': 'co-product__price pdp-main-details__price',
    #        'pause_for_class_name': 'pdp-main-details__price-container'
    #        }
    #    return output

    #def tesco_tags():
    #    output = {
    #        'link_prefix': 'https://www.tesco.com/groceries/en-GB/products/{0}',
    #        'tag_type': 'div',
    #        'tag_attr': 'class',
    #        'class_name': 'price-per-sellable-unit price-per-sellable-unit--price price-per-sellable-unit--price-per-item',
    #        'pause_for_class_name': 'price-details--wrapper'
    #        }
    #    return output

    #def waitrose_tags():
    #    output = {
    #        'link_prefix': 'https://www.waitrose.com/ecom/products/{0}',
    #        'tag_type': 'span',
    #        'tag_attr': 'data-test',
    #        'class_name': 'product-pod-price',
    #        'pause_for_class_name': 'fullDetails___j6CuY'
    #        }
    #    return output

    def test_extract_pw_asda_promo(self):
        asda_tags= {
            'link_prefix': 'https://groceries.asda.com/product/{0}',
            'tag_type': 'strong',
            'tag_attr': 'class',
            'class_name': 'co-product__price pdp-main-details__price',
            'pause_for_class_name': 'pdp-main-details__price-container'
            }
        asda_promo = 'file://../test_data/asda_nybagels_promo.html'
        price_wrapper = ProductWrapper()
        pw = price_wrapper.extract_wrappers(asda_tags, asda_promo)
        price = price_wrapper.get_price(pw)

        self.assertEqual("£1.00", price)

    def test_extract_pw_sainsburys_promo(self):
        sainsburys_tags= {
            'link_prefix': 'https://www.sainsburys.co.uk/shop/gb/groceries/product/details/{0}',
            'tag_type': 'div',
            'tag_attr': 'data-test-id',
            'class_name': 'pd-retail-price',
            'pause_for_class_name': 'pd__cost__per-unit'
            }
        sainsburys_promo = open('./test_data/sainsburys_nybagels_promo.html')
        price_wrapper = ProductWrapper()
        pw = price_wrapper.extract_wrappers(sainsburys_tags, sainsburys_promo)
        price = price_wrapper.get_price(pw)

        self.assertEqual("£1.00", price)

if __name__ == '__main__':
    unittest.main()
