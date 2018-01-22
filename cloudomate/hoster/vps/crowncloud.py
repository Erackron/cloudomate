from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from builtins import int
from future import standard_library
standard_library.install_aliases()
import re
import sys
from collections import OrderedDict

from bs4 import BeautifulSoup

from cloudomate.gateway.bitpay import BitPay
from cloudomate.hoster.hoster import Hoster
from cloudomate.hoster.vps.solusvm_hoster import SolusvmHoster
from cloudomate.hoster.vps.clientarea import ClientArea
from cloudomate.hoster.vps.vps_hoster import VpsConfiguration, VpsOption
from mechanicalsoup import LinkNotFoundError
from cloudomate.hoster.vps import vps_hoster


class CrownCloud(SolusvmHoster):
    CART_URL = 'https://crowncloud.net/clients/cart.php?a=view'
    OPTIONS_URL = 'http://crowncloud.net/openvz.php'

    '''
    Information about the Hoster
    '''

    @staticmethod
    def get_clientarea_url():
        return 'https://crowncloud.net/clients/clientarea.php'

    @staticmethod
    def get_gateway():
        return BitPay

    @staticmethod
    def get_metadata():
        return "CrownCloud", "https://crowncloud.net/"

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
                'rootpw'
            ]
        }

    '''
    Action methods of the Hoster that can be called
    '''

    @classmethod
    def get_options(cls):
        browser = cls._create_browser()
        browser.open(cls.OPTIONS_URL)

        # Get all pricing boxes
        page = browser.get_current_page()
        return list(cls._parse_options(page))

    def purchase(self, wallet, option):
        self._browser.open(option.purchase_url)
        self._submit_server_form()
        self._browser.open(self.CART_URL)
        page = self._submit_user_form()
        self.pay(wallet, self.get_gateway(), page.url)

    '''
    Hoster-specific methods that are needed to perform the actions
    '''

    @classmethod
    def _parse_options(cls, page):
        tables = page.findAll('table')
        for table in tables:  # There are multiple tables with server options on the page
            for row in table.findAll('tr'):
                if len(row.findAll('td')) > 0:  # Ignore headers
                    r = cls._parse_row(row)
                    if not r is None:
                        yield r

    @staticmethod
    def _parse_row(row):
        details = row.findAll('td')

        name = details[0].text

        price = details[6].text
        if 'yearly only' in price:
            return None  # Only yearly price possible
        try:
            i = price.index('/')
        except ValueError:
            return None  # Invalid price string
        price = int(price[1:i])

        cores = int(details[3].text[0])

        memory = float(details[1].text[0:4]) / 1000

        storage = details[2].text.split(' GB')
        storage = int(storage[0])

        bandwidth = details[4].text.split(' GB')
        bandwidth = bandwidth[0]

        connection = details[4].text
        i = connection.index('Gbps')
        connection = int(connection[i-1])

        purchase_url = details[7].find('a')['href']

        return vps_hoster.VpsOption(name, cores, memory, storage, bandwidth, connection, price, purchase_url)

    def _submit_server_form(self):
        try:
            form = self._browser.select_form('form#orderfrm')
            self._fill_server_form()

            form.form['action'] = 'https://crowncloud.net/clients/cart.php'
            print("Frm1")
            # form.form['method'] = 'post'
        except LinkNotFoundError:
            print("Frm2")
            form = self._browser.select_form('form#frmConfigureProduct')
            self._fill_server_form()

        form['billingcycle'] = 'monthly'
        form['configoption[1]'] = '56'
        form['configoption[8]'] = '52'

        try:  # The extra bandwidth option is not always available
            form['configoption[9]'] = '0'
        except LinkNotFoundError:
            pass

        return self._browser.submit_selected()

    def _submit_user_form(self):
        # Select the correct submit button
        form = self._browser.select_form('form#frmCheckout')
        soup = self._browser.get_current_page()
        submit = soup.select('button#btnCompleteOrder')[0]
        form.choose_submit(submit)

        # Let SolusVM handle the rest
        gateway = self.get_gateway()
        self._fill_user_form(gateway.get_name(), errorbox_class='errorbox')

        # Redirect to BitPay
        self._browser.select_form(nr=0)
        return self._browser.submit_selected()





    # def set_root_password(self, password):
    #     """Set Hoster root password

    #     :param password: The root password to set
    #     """
    #     print("CrownCloud does not support changing root password through their configuration panel.")
    #     clientarea = ClientArea(self._browser, self.clientarea_url, self._settings)
    #     (ip, user, rootpw) = self._extract_vps_information(clientarea)
    #     print(("IP: %s" % ip))
    #     print(("Root password: %s\n" % rootpw))

    #     print("https://crownpanel.com")
    #     print(("Username: %s" % user))
    #     print(("Password: %s\n" % rootpw))


    # # TODO: Refactor to return VpsStatus
    # def get_status(self):
    #     clientarea = ClientArea(self._browser, self.clientarea_url, self._settings)
    #     return clientarea.print_services()

    # def _extract_vps_information(self, clientarea):
    #     emails = clientarea.get_emails()
    #     for email in emails:
    #         if 'New VPS Information' in email['title']:
    #             page = self._browser.open("https://crowncloud.net/clients/viewemail.php?id=" + email['id'])
    #             (ip, user, rootpw) = self._extract_email_info(page.get_data())
    #             return ip, user, rootpw
    #     return None

    # @staticmethod
    # def _extract_email_info(data):
    #     soup = BeautifulSoup(data, 'lxml')
    #     text = soup.find('td', {'class': 'bodyContent'}).text
    #     ip_match = re.search(r'Main IP: (\d+\.\d+\.\d+\.\d+)', text)
    #     user_match = re.search(r'Username: (\w+)', text)
    #     rootpw = re.search(r'Root Password: (\w+)You', text)
    #     return ip_match.group(1), user_match.group(1), rootpw.group(1)

    # def info(self, user_settings):
    #     clientarea = ClientArea(self._browser, self.clientarea_url, user_settings)
    #     (ip, user, rootpw) = self._extract_vps_information(clientarea)
    #     return OrderedDict([
    #         ('IP address', ip),
    #         ('Control panel', 'https://crownpanel.com/'),
    #         ('Username', user),
    #         ('Password', rootpw),
    #     ])
