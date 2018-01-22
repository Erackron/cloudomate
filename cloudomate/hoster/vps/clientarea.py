# coding=utf-8
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import OrderedDict
import datetime
from collections import namedtuple
from forex_python.converter import CurrencyRates

from bs4 import BeautifulSoup

ServiceInformation = namedtuple('ServiceInformation', ['name', 'price', 'next_due', 'status', 'url'])


class ClientArea(object):
    """
    Clientarea is the name of the control panel used in many VPS providers. The purpose of this class is to use
    this control panel in an automated manner.
    """
    ACTION_POSTFIX = '?action=services&language=english'


    def __init__(self, browser, clientarea_url, user_settings):
        self._browser = browser
        self._services = None
        self._url = clientarea_url

        self.home_page = None
        self.services = None
        self.user_settings = user_settings
        self._login(user_settings.get('user', 'email'), user_settings.get('user', 'password'))





    def get_services(self):
        if self._services is None:
            response = self._browser.open(self._url + self.ACTION_POSTFIX)
            soup = self._browser.get_current_page()
            rows = soup.select('table#tableServicesList tbody tr')
            self._services = [self._parse_service_row(row) for row in rows]

        return self._services

    def get_services_first(self):
        return self.get_services()[0]

    def _parse_service_row(self, row):
        columns = row.findAll('td')

        name = columns[0].strong.text

        price = columns[1].text
        i = price.index('.')
        p = float(price[1:i+3])
        if 'EUR' in price:
            c = CurrencyRates()
            usd = c.convert("EUR", "USD", p)
            usd = round(usd, 2)
            p = usd

        next_due = columns[2].span.text
        next_due = datetime.datetime.strptime(next_due, '%Y-%m-%d')

        status = columns[3].span.text.lower()

        url = columns[4].a['href']
        url = url.split('.php')
        url = self._url + url[1]

        return ServiceInformation(name, p, next_due, status, url)




    # def _services(self):
    #     if self.services is not None:
    #         return
    #     response = self._browser.open(self._url + "?action=services")
    #     return self._extract_services(response.content)

    # def _extract_services(self, html):
    #     soup = BeautifulSoup(html, 'lxml')
    #     rows = soup.find('table', {'id': 'tableServicesList'}).tbody.findAll('tr')
    #     self.services = []
    #     for row in rows:
    #         tds = row.findAll('td', recursive=False)
    #         classes = tds[3].span['class']
    #         status = ''
    #         for c in classes:
    #             if 'status-' in c:
    #                 status = c.split('status-')[1]

    #         self.services.append({
    #             'id': tds[4].a['href'].split('id=')[1],
    #             'product': tds[0].strong.text,
    #             'price': tds[1].contents[0],
    #             'term': tds[1].contents[2],
    #             'next_due_date': tds[2].text[0:10],
    #             'status': status,
    #             'url': self._url + tds[4].a['href'].split('.php')[1],
    #         })
    #     return self.services














    def _login(self, email, password):
        """
        Login into the clientarea. Exits program if unsuccesful.
        :return: The clientarea homepage on succesful login.
        """
        self._browser.open(self._url)
        self._browser.select_form('.logincontainer form')
        self._browser['username'] = email
        self._browser['password'] = password
        page = self._browser.submit_selected()
        if "incorrect=true" in page.url:
            print("Login failure")
            sys.exit(2)
        self.home_page = page

    # def get_services(self):
    #     """
    #     Parse and list purchased services from clientarea_url?a=action.
    #     :return: the list of services in dict format.
    #     """
    #     if self.services is None:
    #         self._services()
    #     return self.services

    def print_services(self):
        """
        Print parsed VPS configurations.
        """
        self._services()
        row_format = "{:5}" + "{:15}" * 5
        print((row_format.format('#', 'Product', 'Price', 'Term', 'Next due date', 'Status', 'Id')))

        i = 0
        for service in self.services:
            print((row_format.format(
                str(i),
                service['product'],
                service['price'].replace('€', ''),
                service['term'],
                service['next_due_date'],
                service['status'],
                service['id'],
            )))
            i = i + 1
        return self.services

    def _get_vserverid(self, url):
        page = self._browser.open(url)
        match = re.search(r'vserverid = (\d+)', page.text)
        return match.group(1)

    def get_client_data_ip(self, client_data_url):
        """
        Get the ip of specified service through client_data.php. For some clientarea providers this is the way to obtain 
        the IP address.
        :param client_data_url: the URL pointing towards the clientarea's client_data.php
        :return: the IP address
        """
        data = self.get_client_data(client_data_url)
        return data['mainip']

    def get_client_data(self, client_data_url):
        service = self.get_specified_service()
        self._ensure_active(service)
        vserverid = self._get_vserverid(service['url'])
        millis = int(round(time.time() * 1000))
        page = self._browser.open(client_data_url + '?vserverid=%s&_=%s' % (vserverid, millis))
        return json.loads(page.get_data())

    def get_client_data_info_dict(self, client_data_url):
        data = self.get_client_data(client_data_url)
        return OrderedDict([
            ('Used bandwidth', data['bandwidthused'] + ' / ' + data['bandwidthtotal']),
            ('Used memory', data['memoryused'] + ' / ' + data['memorytotal']),
            ('Used storage', data['hddused'] + ' / ' + data['hddtotal']),
            ('IP address', data['mainip']),
        ])

    def get_specified_service(self):
        """
        If number is set through config or cli, return the service according to the number, else return the first 
        service.
        :return: the chosen service
        """
        number = self._get_number()
        self._services()
        self._verify_number(number)
        return self.services[number]

    def _verify_number(self, number):
        self._services()
        if not 0 <= number < len(self.services):
            print(("Wrong index: %s not between 0 and %s" % (number, len(self.services) - 1)))
            sys.exit(2)

    def set_rootpw_client_data(self, password):
        """
        Set the rootpassword for the appropriate service through client_data.php.
        :return: 
        """
        service = self.get_specified_service()
        self._ensure_active(service)
        millis = int(round(time.time() * 1000))

        vserverid = self._get_vserverid(service['url'])
        url = self._url + '?action=productdetails&id=%s&vserverid=%s&modop=custom&a=ChangeRootPassword' \
                                    '&newrootpassword=%s&ajax=1&ac=Custom_ChangeRootPassword&_=%s' \
              % (service['id'], vserverid, password, millis)
        response = self._browser.open(url)
        response_json = json.loads(response.text)
        if response_json['success'] is True:
            print("Password changed successfully")
            return True
        else:
            print((response_json['msg']))
            return False

    def set_rootpw_rootpassword_php(self, password):
        """
        Set the rootpassword for the appropriate service through rootpassword.php.
        :return: 
        """
        service = self.get_specified_or_active_service()
        self._ensure_active(service)
        data = {
            'newrootpassword': password,
            'rootpassword': 'Change'
        }
        data = urllib.parse.urlencode(data)
        url = self._url.replace('clientarea', 'rootpassword') + '?id=' + service['id']
        page = self._browser.open(url, data)
        if 'Password Updated' in page.get_data():
            print("Password changed successfully")
            return True
        else:
            print("Setting password failed")
            return False

    @staticmethod
    def _ensure_active(service):
        if service['status'] != 'active':
            print(("Service is %s" % service['status']))
            sys.exit(2)

    def get_service_info(self):
        """
        Get info for the specified service. This depends on the state of the service and on the provider. Contains
        info like ip address, hostname, passwords...
        :return: 
        """
        service = self.get_specified_or_active_service()
        self._ensure_active(service)
        page = self._browser.open(service['url'])
        return self._extract_service_info(page.text)

    def get_ip(self):
        """
        Get the ip address for a service.
        If a number is specified: return the IP address of this service.
        If no number is specified, the IP address of first active service is returned.
        :return: the chosen IP address
        """
        return self.get_service_info()[1]

    def get_specified_or_active_service(self):
        """
        Get either the specified (by number) service or the first active service.
        :return: the service
        """
        service = self.get_specified_service()
        if service['status'] != 'active' and not self.user_settings.has_key('server', 'number'):
            for s in self.services:
                if s['status'] == 'active':
                    service = s
                    break
        self._ensure_active(service)
        return service

    @staticmethod
    def _extract_service_info(html):
        soup = BeautifulSoup(html, 'lxml')
        domain = soup.find('div', {'id': 'domain'})
        cols = domain.findAll('div', {'class': 'row'}, recursive=False)
        info = []
        for col in cols:
            data = col.find('div', {'class': 'text-left'})
            info.append(data.text.strip())
        return info

    def _get_number(self):
        if self.user_settings.has_key('server', 'number'):
            return int(self.user_settings.get('server', 'number'))
        return 0

    def get_emails(self):
        page = self._browser.open(self._url + "?action=emails")
        return self._extract_emails(page.get_data())

    @staticmethod
    def _extract_emails(data):
        soup = BeautifulSoup(data, 'lxml')
        table = soup.find('table', {'id': 'tableEmailsList'}).tbody
        emails = []
        for row in table.findAll('tr'):
            emails.append({
                'id': row['onclick'].split('\'')[1].split('id=')[1],
                'title': row.findAll('td')[1].text
            })
        return emails
