from abc import abstractmethod, ABCMeta
from collections import namedtuple

PaymentInfo = namedtuple('PaymentInfo', ['amount', 'address'])


class Gateway(metaclass=ABCMeta):
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
