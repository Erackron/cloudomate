from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import open
from future import standard_library
standard_library.install_aliases()
import os
import unittest
import sys
if sys.version_info > (3,0):
    from urllib.request import urlopen
    from urllib.parse import urlencode
    import urllib
else:
    from urllib2 import urlopen
    import urllib2
    from urllib import urlencode


import requests
from cloudomate.gateway.bitpay import BitPay
from cloudomate.gateway.coinbase import Coinbase
from unittest.mock import patch, Mock

from cloudomate.util.bitcoinaddress import validate


class TestCoinbase(unittest.TestCase):
    # test url from https://developers.coinbase.com/docs/merchants/payment-pages
    TEST_URL = 'https://www.coinbase.com/checkouts/2b30a03995ec62f15bdc54e8428caa87'
    amount = None
    address = None

    @classmethod
    def setUpClass(cls):
        cls.amount, cls.address = Coinbase.extract_info(cls.TEST_URL)

    def test_address(self):
        self.assertTrue(validate(self.address))

    def test_amount(self):
        self.assertGreater(self.amount, 0)


class TestBitPay(unittest.TestCase):
    amount = None
    address = None
    rate = None

    @classmethod
    def setUpClass(cls):
        html_file = open(os.path.join(os.path.dirname(__file__), 'resources/bitpay_invoice_data.json'), 'r')
        data = html_file.read().encode('utf-8')
        response = requests.Response()
        response.read = Mock(return_value=data)
        #with Mock(return_value = response) as urlopen:
        if sys.version_info > (3, 0):
            with patch.object(urllib.request, 'urlopen', return_value=response):
                cls.amount, cls.address = BitPay.extract_info('https://bitpay.com/invoice?id=KXnWTnNsNUrHK2PEp8TpDC')
        else:
            with patch.object(urllib2, 'urlopen', return_value=response):
                cls.amount, cls.address = BitPay.extract_info('https://bitpay.com/invoice?id=KXnWTnNsNUrHK2PEp8TpDC')


    def test_address(self):
        self.assertEqual(self.address, '12cWmVndhmD56dzYcRuYka3Vpgjb3qdRoL')
        pass

    def test_amount(self):
        self.assertEqual(self.amount, 0.001402)

    def test_address_valid(self):
        self.assertTrue(validate(self.address))
