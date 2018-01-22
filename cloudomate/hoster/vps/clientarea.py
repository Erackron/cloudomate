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

ClientAreaService = namedtuple('ClientAreaService', ['name', 'price', 'next_due', 'status', 'url'])


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
        self._login(user_settings.get('user', 'email'), user_settings.get('user', 'password'))




    def get_ip(self, service=None):
        if service is None:
            service = self.get_services_first()

        page = self._browser.open(service.url)
        soup = self._browser.get_current_page()
        rows = soup.select('div#domain > div.row')
        for row in rows:
            divs = row.findAll('div')
            if 'IP' in divs[0].strong.text:
                return divs[1].text.strip()

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

        return ClientAreaService(name, p, next_due, status, url)

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

    #
    # Legacy methods, currently not used
    #   

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
