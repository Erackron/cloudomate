from collections import OrderedDict
import sys

from cloudomate.gateway.coinbase import Coinbase
from cloudomate.hoster.vps.solusvm_hoster import SolusvmHoster
from cloudomate.hoster.vps.clientarea import ClientArea
from cloudomate.hoster.vps import vps_hoster


class LegionBox(SolusvmHoster):
    CART_URL = 'https://legionbox.com/billing/cart.php?a=view'
    OPTIONS_URL = 'https://legionbox.com/virtual-servers/'

    '''
    Information about the Hoster
    '''

    @staticmethod
    def get_clientarea_url():
        return 'https://legionbox.com/billing/clientarea.php'

    @staticmethod
    def get_gateway():
        return Coinbase

    @staticmethod
    def get_metadata():
        return 'Legionbox', 'https://legionbox.com/'

    @staticmethod
    def get_required_settings():
        return {
            'user': [
                'firstname',
                'lastname',
                'email',
                'password',
                'phonenumber',
            ],
            'address': [
                'address',
                'city',
                'state',
                'zipcode',
            ],
            'server': [
                'rootpw',
                'hostname',
            ]

        }

    '''
     Action methods of the Hoster that can be called
     '''

    @classmethod
    def get_options(cls):
        browser = cls._create_browser()
        browser.open(cls.OPTIONS_URL)

        # Retrieve the boxes for Linux and SSD servers
        soup = browser.get_current_page()
        linux = soup.select('div#Linux > ul > li')
        ssd = soup.select('div#SSD-VPS > ul > li')
        boxes = linux + ssd

        return [cls._parse_box(box) for box in boxes]


        # options = cls.parse_options(soup.find('div', {'id': 'Linux'}).ul)
        # options = itertools.chain(options, cls.parse_options(soup.find('div', {'id': 'SSD-VPS'}).ul))
        # return options

    def purchase(self, wallet, option):
        self._browser.open(option.purchase_url)
        self._submit_server_form()
        self._browser.open(self.CART_URL)
        page = self._submit_user_form()
        self.pay(wallet, self.get_gateway(), page.url)











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
        self.user_form(self._browser, user_settings, self.gateway.name, errorbox_class='errorbox')

        page = self._browser.follow_link("coinbase")
        return self.gateway.extract_info(page.url)










    '''
    Hoster-specific methods that are needed to perform the actions
    '''

    @staticmethod
    def _parse_box(box):
        details = box.findAll('div')

        name = box.h4.text

        price = box.strong.text
        price = float(price[1:])

        cores = details[2].strong.text
        cores = int(cores[0])

        memory = details[3].strong.text
        memory = float(memory[0:-3])

        storage = details[4].strong.text
        storage = float(storage[0:-3])

        connection = 1  # Not given by Legionbox, assuming 1 Gbps

        purchase_url = box.a['href']

        return vps_hoster.VpsOption(name, cores, memory, storage, sys.maxsize, connection, price, purchase_url)

    def _submit_user_form(self):
        # Select the correct submit button
        form = self._browser.select_form('form#frmCheckout')
        # soup = self._browser.get_current_page()
        # submit = soup.select_one('input.ordernow')
        # form.choose_submit(submit)

        # Let SolusVM class handle the rest
        gateway = self.get_gateway()
        self._fill_user_form(gateway.get_name(), errorbox_class='errorbox')

        # Redirect to Coinbase
        return self._browser.follow_link('coinbase')
        # self._browser.select_form(nr=0)
        # return self._browser.submit_selected()

    def _submit_server_form(self):
        form = self._browser.select_form('form#orderfrm')

        self._fill_server_form()
        form['billingcycle'] = 'monthly'
        form['configoption[5]'] = '24'  # Bandwidth: Unchanged (no extra)
        form['configoption[6]'] = '29'  # Control Panel: None
        form['configoption[10]'] = '39'  # Location: Russia
        form['configoption[11]'] = '49'  # Operating system: Ubuntu 14.10
        form.form['action'] = 'https://legionbox.com/billing/cart.php'

        return self._browser.submit_selected()







    # def server_form(self, user_settings):
    #     """
    #     Fills in the form containing server configuration.
    #     :param user_settings: settings
    #     :return: 
    #     """
    #     self.select_form_id(self._browser, 'orderfrm')
    #     form = self._browser.get_current_form();
    #     self.fill_in_server_form(form, user_settings, nameservers=False)
    #     form['configoption[10]'] = '39'  # Russia
    #     form['configoption[11]'] = '49'  # Ubuntu 14.10
    #     form.action = 'https://legionbox.com/billing/cart.php'
    #     form.new_control('hidden', 'a', 'confproduct')
    #     form.new_control('hidden', 'ajax', '1')
    #     self._browser.submit_selected()










    # def start(self):
    #     self._browser.open("https://legionbox.com/virtual-servers/")
    #     soup = self._browser.get_current_page()
    #     options = self.parse_options(soup.find('div', {'id': 'Linux'}).ul)
    #     options = itertools.chain(options, self.parse_options(soup.find('div', {'id': 'SSD-VPS'}).ul))
    #     return options

    # @classmethod
    # def parse_options(cls, options_list):
    #     items = options_list.findAll('li')
    #     for item in items:
    #         yield cls.parse_option(item)

    # @staticmethod
    # def parse_option(item):
    #     divs = item.findAll('div')
    #     return VpsOption(
    #         name=item.h4.text,
    #         price=float(item.strong.text[1:]),
    #         connection=1000,
    #         cores=divs[2].strong.text[0],
    #         memory=divs[3].strong.text.split(' ')[0],
    #         bandwidth='unmetered',
    #         storage=divs[4].strong.text.split(' ')[0],
    #         purchase_url=item.a['href']
    #     )

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
