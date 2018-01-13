from collections import OrderedDict

from cloudomate.gateway.coinbase import Coinbase
from cloudomate.hoster.vps.solusvm_hoster import SolusvmHoster
from cloudomate.hoster.vps.clientarea import ClientArea
from cloudomate.hoster.vps.vpsoption import VpsOption
from cloudomate.wallet import determine_currency

from cloudomate.hoster.vps import vps_hoster
import sys


class Pulseservers(SolusvmHoster):
    clientarea_url = 'https://www.pulseservers.com/billing/clientarea.php'



    OPTIONS_URL = 'https://pulseservers.com/vps-linux.html'
    CART_URL = 'https://www.pulseservers.com/billing/cart.php?a=confdomains'



    '''
    Information about the Hoster
    '''

    @staticmethod
    def get_gateway():
        return Coinbase

    @staticmethod
    def get_metadata():
        return ('PulseServers', 'https://pulseservers.com')

    @staticmethod
    def get_required_settings():
        return {
            'user': ['firstname', 'lastname', 'email', 'phonenumber', 'address', 'city', 'state', 'zipcode', 'password'],
            'server': ['hostname', 'rootpw']
        }


    '''
    Action methods of the Hoster that can be called
    '''

    def get_configuration(self):
        pass

    @classmethod
    def get_options(cls):
        browser = cls._create_browser()
        browser.open(cls.OPTIONS_URL)

        # Get all pricing boxes
        soup = browser.get_current_page()
        boxes = soup.select('div.pricing-box')
        return [cls._parse_box(box) for box in boxes]

    def get_status(self):
        pass

    def purchase(self, wallet, option):
        self._browser.open(option.purchase_url)
        self._fill_server_form()
        self._browser.open(self.CART_URL)
        page = self._fill_user_form()
        self.pay(wallet, self.get_gateway(), page.url)

    def set_root_password(self, password):
        pass


    '''
    Hoster-specific methods that are needed to perform the actions
    '''

    def _fill_server_form(self):
        form = self._browser.select_form('form#orderfrm')

        self.fill_in_server_form(form, self._settings, nameservers=False)
        form.set('billingcycle', 'monthly')
        form.form['action'] = 'https://www.pulseservers.com/billing/cart.php'
        form.form['method'] = 'get'
        form.new_control('hidden', 'a', 'confproduct')
        form.new_control('hidden', 'ajax', '1')

        self._browser.submit_selected()

    def _fill_user_form(self):
        # Select the correct submit button
        form = self._browser.select_form('form#mainfrm')
        soup = self._browser.get_current_page()
        submit = soup.select_one('input.ordernow')
        form.choose_submit(submit)

        # Let SolusVM class handle the rest
        gateway = self.get_gateway()
        self.user_form(self._browser, self._settings, gateway.get_name(), errorbox_class='errorbox')

        # Redirect to Coinbase
        self._browser.select_form(nr=0)
        return self._browser.submit_selected()

    @staticmethod
    def _parse_box(box):
        details = box.findAll('li')

        name = details[0].h4.text

        price = details[1].h1.text
        price = float(price[1:])

        cores = details[2].strong.text
        cores = int(cores.split(' ')[0])

        memory = details[3].strong.text
        memory = float(memory[0:-2])

        storage = details[4].strong.text
        if storage == '1TB':
            storage = 1000.0
        else:
            storage = float(storage[0:-2])

        connection = details[5].strong.text
        connection = int(connection[0:-7])

        purchase_url = details[9].a['href']

        return vps_hoster.VpsOption(name, cores, memory, storage, sys.maxsize, connection, price, purchase_url)







    # def get_status(self, user_settings):
    #     clientarea = ClientArea(self._browser, self.clientarea_url, user_settings)
    #     return clientarea.print_services()

    # def set_rootpw(self, user_settings):
    #     clientarea = ClientArea(self._browser, self.clientarea_url, user_settings)
    #     clientarea.set_rootpw_rootpassword_php()

    # def get_ip(self, user_settings):
    #     clientarea = ClientArea(self._browser, self.clientarea_url, user_settings)
    #     return clientarea.get_ip()

    # def info(self, user_settings):
    #     clientarea = ClientArea(self._browser, self.clientarea_url, user_settings)
    #     data = clientarea.get_service_info()
    #     return OrderedDict([
    #         ('Hostname', data[0]),
    #         ('IP address', data[1]),
    #         ('Nameserver 1', data[2].split('.com')[0] + '.com'),
    #         ('Nameserver 2', data[2].split('.com')[1]),
    #     ])
