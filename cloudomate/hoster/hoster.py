from abc import abstractmethod, ABCMeta

from fake_useragent import UserAgent
from mechanicalsoup import StatefulBrowser

from cloudomate import wallet as wallet_util


class Hoster(metaclass=ABCMeta):
    def __init__(self, settings):
        self._browser = self._create_browser()
        self._settings = settings

    @abstractmethod
    def get_configuration(self):
        """Get Hoster configuration.

        :return: Returns configuration for the Hoster instance
        """
        pass

    @staticmethod
    @abstractmethod
    def get_gateway():
        """Get payment gateway used by the Hoster.

        :return: Returns the payment gateway module
        """
        pass

    @staticmethod
    @abstractmethod
    def get_metadata():
        """Get metadata about the Hoster.

        :return: Returns tuple of name and website url
        """
        pass

    @classmethod
    @abstractmethod
    def get_options(cls):
        """Get Hoster options.

        :return: Returns list of Hoster options
        """
        pass

    @staticmethod
    @abstractmethod
    def get_required_settings():
        """Get settings required by the Hoster.

        :return: Returns dictionary with sections as keys and the required settings in those sections as values
        """
        pass

    @abstractmethod
    def get_status(self):
        """Get Hoster configuration.

        :return: Returns status of the Hoster instance
        """
        pass

    @classmethod
    def pay(cls, wallet, gateway, url):
        """Do a payment (should be moved to the payment gateways?)

        :param gateway: gateway through which to make the payment
        :param url: url from which the amount and address can be extracted
        """
        name, _ = cls.get_metadata()

        # Make the payment
        print("Purchasing {} instance".format(name))
        amount, address = gateway.extract_info(url)
        print(('Paying %s BTC to %s' % (amount, address)))
        fee = wallet_util.get_network_fee()
        print(('Calculated fee: %s' % fee))
        transaction_hash = wallet.pay(address, amount, fee)
        print('Done purchasing')
        return transaction_hash

    @abstractmethod
    def purchase(self, wallet, option):
        """Purchase Hoster.

        :param wallet: The Electrum wallet to use for payments
        :param option: Hoster option to purchase
        """
        pass

    @staticmethod
    def _create_browser():
        user_agent = UserAgent()
        return StatefulBrowser(user_agent=user_agent.random)
