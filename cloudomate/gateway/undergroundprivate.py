from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
import sys
if sys.version_info > (3,0):
    from urllib.request import urlopen
else:
    from urllib2 import urlopen

from bs4 import BeautifulSoup

from cloudomate.gateway.gateway import Gateway, PaymentInfo


class UndergroundPrivate(Gateway):
    @staticmethod
    def get_name():
        return "blockchainv2"

    @classmethod
    def extract_info(cls, url):
        """
        Extracts amount and BitCoin address from a UndergroundPrivate payment URL.
        :param url: the URL (usually retrieved from an iFrame) like "https://www.clientlogin.sx//modules/gateways/blockchainv2.php?invoice=19076"
        :return: a tuple of the amount in BitCoin along with the address
        """

        response = urlopen(url)
        soup = BeautifulSoup(response, 'lxml')

        amount = soup.select_one('input.btcamount')
        amount = amount['value']

        address = soup.select_one('input.btcaddress')
        address = address['value']

        return PaymentInfo(amount, address)

    @staticmethod
    def get_gateway_fee():
        return 0.0
