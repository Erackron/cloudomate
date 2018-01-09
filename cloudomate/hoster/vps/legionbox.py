import itertools
from collections import OrderedDict

from cloudomate.gateway import coinbase
from cloudomate.hoster.vps.solusvm_hoster import SolusvmHoster
from cloudomate.hoster.vps.clientarea import ClientArea
from cloudomate.hoster.vps.vps_hoster import VpsOption


class LegionBox(SolusvmHoster):
    clientarea_url = 'https://legionbox.com/billing/clientarea.php'
    gateway = coinbase

    '''
    Information about the Hoster
    '''

    @staticmethod
    def get_gateway():
        return coinbase

    @staticmethod
    def get_metadata():
        return ("legionbox", "https://legionbox.com/")

    @staticmethod
    def get_required_settings():
        return [
        'firstname',
        'lastname',
        'email',
        'address',
        'city',
        'state',
        'zipcode',
        'phonenumber',
        'password',
        'hostname',
        'rootpw']

    '''
     Action methods of the Hoster that can be called
     '''

    @classmethod
    def get_options(cls):
        browser = cls._create_browser()
        browser.open("https://legionbox.com/virtual-servers/")
        soup = browser.get_current_page()
        options = cls.parse_options(soup.find('div', {'id': 'Linux'}).ul)
        options = itertools.chain(options, cls.parse_options(soup.find('div', {'id': 'SSD-VPS'}).ul))
        return options

    def __init__(self, settings):
        super(LegionBox, self).__init__(settings)

    def start(self):
        self._browser.open("https://legionbox.com/virtual-servers/")
        soup = self._browser.get_current_page()
        options = self.parse_options(soup.find('div', {'id': 'Linux'}).ul)
        options = itertools.chain(options, self.parse_options(soup.find('div', {'id': 'SSD-VPS'}).ul))
        return options

    @classmethod
    def parse_options(cls, options_list):
        items = options_list.findAll('li')
        for item in items:
            yield cls.parse_option(item)

    @staticmethod
    def parse_option(item):
        divs = item.findAll('div')
        return VpsOption(
            name=item.h4.text,
            price=float(item.strong.text[1:]),
            connection=1000,
            cores=divs[2].strong.text[0],
            memory=divs[3].strong.text.split(' ')[0],
            bandwidth='unmetered',
            storage=divs[4].strong.text.split(' ')[0],
            purchase_url=item.a['href']
        )

    def get_status(self, user_settings):
        clientarea = ClientArea(self._browser, self.clientarea_url, user_settings)
        clientarea.print_services()

    def set_rootpw(self, user_settings):
        clientarea = ClientArea(self._browser, self.clientarea_url, user_settings)
        clientarea.set_rootpw_client_data()

    def get_ip(self, user_settings):
        clientarea = ClientArea(self._browser, self.clientarea_url, user_settings)
        return clientarea.get_service_info()[1]

    def info(self, user_settings):
        clientarea = ClientArea(self._browser, self.clientarea_url, user_settings)
        data = clientarea.get_service_info()
        return OrderedDict([
            ('Hostname', data[0]),
            ('IP', data[1]),
        ])

    def register(self, user_settings, vps_option):
        """
        Register LegionBox provider, pay through CoinBase
        :param user_settings: 
        :param vps_option: 
        :return: 
        """
        self._browser.open(vps_option.purchase_url)
        self.server_form(user_settings)
        self._browser.open('https://legionbox.com/billing/cart.php?a=view')
        self.select_form_id(self._browser, 'frmCheckout')
        #promobutton = self.br.get_current_form().find_control(type="submit", nr=0)
        #promobutton.disabled = True
        self.user_form(self._browser, user_settings, self.gateway.name, errorbox_class='errorbox')
        page = self._browser.follow_link("coinbase")
        return self.gateway.extract_info(page.url)
        # page = self.br.follow_link(url_regex="coinbase")
        # return self.gateway.extract_info(page.geturl())

    def server_form(self, user_settings):
        """
        Fills in the form containing server configuration.
        :param user_settings: settings
        :return: 
        """
        self.select_form_id(self._browser, 'orderfrm')
        form = self._browser.get_current_form();
        self.fill_in_server_form(form, user_settings, nameservers=False)
        form['configoption[10]'] = '39'  # Russia
        form['configoption[11]'] = '49'  # Ubuntu 14.10
        form.action = 'https://legionbox.com/billing/cart.php'
        form.new_control('hidden', 'a', 'confproduct')
        form.new_control('hidden', 'ajax', '1')
        self._browser.submit_selected()
