import re
import sys
from collections import OrderedDict

from bs4 import BeautifulSoup

from cloudomate.gateway import bitpay
from cloudomate.gateway.bitpay import BitPay
from cloudomate.hoster.hoster import Hoster
from cloudomate.hoster.vps.solusvm_hoster import SolusvmHoster
from cloudomate.hoster.vps.clientarea import ClientArea
from cloudomate.hoster.vps.vps_hoster import VpsConfiguration, VpsOption
from mechanicalsoup import LinkNotFoundError


class CrownCloud(SolusvmHoster):
    clientarea_url = 'https://crowncloud.net/clients/clientarea.php'

    def __init__(self, settings):
        super(CrownCloud, self).__init__(settings)

    '''
    Information about the Hoster
    '''

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
                'root_password'
            ]
        }

    '''
    Action methods of the Hoster that can be called
    '''

    def get_configuration(self):
        """Get Hoster configuration.

        :return: Returns VpsConfiguration for the VPS Hoster instance
        """
        clientarea = ClientArea(self._browser, self.clientarea_url, self._settings)
        (ip, _, rootpw) = self._extract_vps_information(clientarea)
        if not ip:
            print("No active IP found")
            sys.exit(2)
        return VpsConfiguration(ip, rootpw)

    @classmethod
    def get_options(cls):
        """Get Hoster options.

        :return: Returns list of VpsOption objects
        """
        browser = Hoster._create_browser()
        browser.get('http://crowncloud.net/openvz.php')
        return list(cls.parse_options(browser.get_current_page()))

    def set_root_password(self, password):
        """Set Hoster root password

        :param password: The root password to set
        """
        print("CrownCloud does not support changing root password through their configuration panel.")
        clientarea = ClientArea(self._browser, self.clientarea_url, self._settings)
        (ip, user, rootpw) = self._extract_vps_information(clientarea)
        print(("IP: %s" % ip))
        print(("Root password: %s\n" % rootpw))

        print("https://crownpanel.com")
        print(("Username: %s" % user))
        print(("Password: %s\n" % rootpw))

    def register(self, user_settings, vps_option):
        """
        Register CrownCloud provider, pay through BitPay
        :param user_settings: 
        :param vps_option: 
        :return: 
        """
        self._browser.open(vps_option.purchase_url)
        self.server_form(user_settings)
        self._browser.open('https://crowncloud.net/clients/cart.php?a=view')
        self.select_form_id(self._browser, 'frmCheckout')
        form = self._browser.get_current_form()

        soup = self._browser.get_current_page()
        submit = soup.select('button#btnCompleteOrder')[0]
        form.choose_submit(submit)

        self.user_form(self._browser, user_settings, self.get_gateway().get_name(), errorbox_class='errorbox')
        self._browser.select_form(nr=0)
        page = self._browser.submit_selected()
        return self.get_gateway().extract_info(page.url)

    def server_form(self, user_settings):
        """
        Fills in the form containing server configuration.
        :return: 
        """
        try:
            self.select_form_id(self._browser, 'orderfrm')
            self.fill_in_server_form(self._browser.get_current_form(), user_settings, nameservers=False, rootpw=False,
                                     hostname=False)
            form = self._browser.get_current_form()
            form.form['action'] = 'https://crowncloud.net/clients/cart.php'
            form.form['method'] = 'post'
            form['configoption[1]'] = '56'
            form['configoption[8]'] = '52'
            form['configoption[9]'] = '0'
            form.new_control('hidden', 'a', 'confproduct')
            form.new_control('hidden', 'ajax', '1')
        except LinkNotFoundError:
            self.select_form_id(self._browser, 'frmConfigureProduct')
            self.fill_in_server_form(self._browser.get_current_form(), user_settings, nameservers=False, rootpw=False,
                                     hostname=False)
            print("Using classic form")
            pass
        resp = self._browser.submit_selected()

    @classmethod
    def parse_options(cls, page):
        tables = page.findAll('table')
        for details in tables:
            for column in details.findAll('tr'):
                if len(column.findAll('td')) > 0:
                    yield cls.parse_clown_options(column)

    @staticmethod
    def beautiful_bandwidth(bandwidth):
        if bandwidth == '512 GB':
            return 0.5
        else:
            return float(bandwidth.split(' ')[0])

    @staticmethod
    def parse_clown_options(column):
        elements = column.findAll('td')
        ram = elements[1].text.split('<br>')[0]
        ram = float(ram.split('M')[0]) / 1024
        price = elements[6].text
        price = price.split("<br>")[0]
        price = price.split('$')[1]
        price = float(price.split('/')[0])

        return VpsOption(
            name=elements[0].text,
            memory=ram,
            storage=float(elements[2].text.split('G')[0]),
            cores=int(elements[3].text.split('v')[0]),
            bandwidth=CrownCloud.beautiful_bandwidth(elements[4].text),
            connection=int(elements[4].text.split('GB')[1].split('G')[0]) * 1000,
            price=price,
            purchase_url=elements[7].find('a')['href']
        )

    # TODO: Refactor to return VpsStatus
    def get_status(self):
        clientarea = ClientArea(self._browser, self.clientarea_url, self._settings)
        return clientarea.print_services()

    def _extract_vps_information(self, clientarea):
        emails = clientarea.get_emails()
        for email in emails:
            if 'New VPS Information' in email['title']:
                page = self._browser.open("https://crowncloud.net/clients/viewemail.php?id=" + email['id'])
                (ip, user, rootpw) = self._extract_email_info(page.get_data())
                return ip, user, rootpw
        return None

    @staticmethod
    def _extract_email_info(data):
        soup = BeautifulSoup(data, 'lxml')
        text = soup.find('td', {'class': 'bodyContent'}).text
        ip_match = re.search(r'Main IP: (\d+\.\d+\.\d+\.\d+)', text)
        user_match = re.search(r'Username: (\w+)', text)
        rootpw = re.search(r'Root Password: (\w+)You', text)
        return ip_match.group(1), user_match.group(1), rootpw.group(1)

    def info(self, user_settings):
        clientarea = ClientArea(self._browser, self.clientarea_url, user_settings)
        (ip, user, rootpw) = self._extract_vps_information(clientarea)
        return OrderedDict([
            ('IP address', ip),
            ('Control panel', 'https://crownpanel.com/'),
            ('Username', user),
            ('Password', rootpw),
        ])
