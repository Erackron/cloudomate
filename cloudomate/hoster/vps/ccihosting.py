import sys

from cloudomate.gateway.coinbase import Coinbase
from cloudomate.hoster.vps.solusvm_hoster import SolusvmHoster
from cloudomate.hoster.vps.vps_hoster import VpsOption


class CCIHosting(SolusvmHoster):
    CART_URL = 'https://www.ccihosting.com/accounts/cart.php?a=confdomains'
    OPTIONS_URL = 'https://www.ccihosting.com/offshore-vps.html'

    '''
    Information about the Hoster
    '''

    @staticmethod
    def get_clientarea_url():
        return 'https://www.ccihosting.com/accounts/clientarea.php'

    @staticmethod
    def get_gateway():
        return Coinbase

    @staticmethod
    def get_metadata():
        return 'CCIHosting', 'https://www.ccihosting.com/'

    @staticmethod
    def get_required_settings():
        return {
            'user': ['firstname', 'lastname', 'email', 'phonenumber', 'password'],
            'address': ['address', 'city', 'state', 'zipcode', 'countrycode'],
            'server': ['hostname', 'rootpw', 'ns1', 'ns2']
        }

    '''
    Action methods of the Hoster that can be called
    '''

    @classmethod
    def get_options(cls):
        browser = cls._create_browser()
        browser.open(self.OPTIONS_URL)
        return list(cls._parse_options(browser.get_current_page()))

    def purchase(self, wallet, option):
        self._browser.open(option.purchase_url)
        self._server_form()  # Add item to cart
        self._browser.open(self.CART_URL)

        summary = self._browser.get_current_page().find('div', class_='summary-container')
        self._browser.follow_link(summary.find('a', class_='btn-checkout'))

        self._browser.select_form(selector='form[name=orderfrm]')
        self._fill_user_form(self.get_gateway().get_name())

        coinbase_url = self._browser.get_current_page().find('form')['action']
        self.pay(wallet, self.get_gateway(), coinbase_url)

    '''
    Hoster-specific methods that are needed to perform the actions
    '''

    def _server_form(self):
        """
        Using a form does not work for some reason, so use post request instead
        """
        self._browser.post('https://www.ccihosting.com/accounts/cart.php', {
            'ajax': '1',
            'a': 'confproduct',
            'configure': 'true',
            'i': '0',
            'billingcycle': 'monthly',
            'hostname': self._settings.get('server', 'hostname'),
            'rootpw': self._settings.get('server', 'rootpw'),
            'ns1prefix': self._settings.get('server', 'ns1'),
            'ns2prefix': self._settings.get('server', 'ns2'),
            'configoption[214]': '1193',  # Ubuntu 16.04
            'configoption[258]': '955',
        })

    @classmethod
    def _parse_options(cls, page):
        tables = page.findAll('div', class_='p_table')
        for column in tables:
            yield cls._parse_cci_options(column)

    @staticmethod
    def _parse_cci_options(column):
        header = column.find('div', class_='phead')
        price = column.find('span', class_='starting-price')
        info = column.find('ul').findAll('li')
        return VpsOption(
            name=header.find('h2').contents[0],
            price=float(price.contents[0]),
            cores=int(info[1].find('strong').contents[0]),
            memory=float(info[2].find('strong').contents[0]),
            storage=float(info[3].find('strong').contents[0]),
            bandwidth=sys.maxsize,
            connection=0.01,  # See FAQ at https://www.ccihosting.com/offshore-vps.html
            purchase_url=column.find('a')['href']
        )

