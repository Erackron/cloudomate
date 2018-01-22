from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from abc import abstractmethod, ABCMeta
from collections import namedtuple

PaymentInfo = namedtuple('PaymentInfo', ['amount', 'address'])
from future.utils import with_metaclass

class Gateway(with_metaclass(ABCMeta)):
    @staticmethod
    @abstractmethod
    def get_name():
        return ""

    @staticmethod
    @abstractmethod
    def extract_info(url):
        return PaymentInfo(None, None)

    @staticmethod
    @abstractmethod
    def get_gateway_fee():
        return 0.0

    @classmethod
    def estimate_price(cls, cost):
        return cost * (1.0 + cls.get_gateway_fee())
