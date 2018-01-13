import sys
from abc import abstractmethod

from bs4 import BeautifulSoup
from cloudomate.hoster.vps.vps_hoster import VpsHoster


class SolusvmHoster(VpsHoster):
    @staticmethod
    def fill_in_server_form(form, user_settings, rootpw=True, nameservers=True, hostname=True):
        """
        Fills in the form containing server configuration.
        :return: 
        """
        if hostname:
            form['hostname'] = user_settings.get('server', 'hostname')
        if rootpw:
            form['rootpw'] = user_settings.get('server', 'rootpw')
        if nameservers:
            form['ns1prefix'] = user_settings.get('server', 'ns1')
            form['ns2prefix'] = user_settings.get('server', 'ns2')
        form.new_control('text', 'ajax', 1)
        form.new_control('text', 'a', 'confproduct')
        form.method = "POST"

    @staticmethod
    def user_form(br, user_settings, payment_method, errorbox_class='checkout-error-feedback', acceptos=True):
        """
        Fills in the form with user information.
        :param acceptos:
        :param errorbox_class: the class of the div containing error messages.
        :param payment_method: the payment method, typically coinbase or bitpay
        :param br: browser
        :param user_settings: settings
        :return: 
        """
        form = br.get_current_form()
        form['firstname'] = user_settings.get('user', "firstname")
        form['lastname'] = user_settings.get('user', "lastname")
        form['email'] = user_settings.get('user', "email")
        form['phonenumber'] = user_settings.get('user', "phonenumber")
        form['companyname'] = user_settings.get('user', "companyname")
        form['address1'] = user_settings.get('user', "address")
        form['city'] = user_settings.get('user', "city")
        form['state'] = user_settings.get('user', "state")
        form['postcode'] = user_settings.get('user', "zipcode")
        #form['country'] = [user_settings.get('countrycode')]
        #form.set('country', [user_settings.get('countrycode')])
        form['country'] = user_settings.get('user', 'countrycode')
        form['password'] = user_settings.get('user', "password")
        form['password2'] = user_settings.get('user', "password")
        form['paymentmethod'] = payment_method
        if acceptos:
            form['accepttos'] = True

        page = br.submit_selected()

        if 'checkout' in page.url:
            soup = BeautifulSoup(page.text, 'lxml')
            errors = soup.find('div', {'class': errorbox_class}).text
            print((errors.strip()))
            sys.exit(2)

    @staticmethod
    def select_form_id(browser, form_id):
        """
        Selects the form with specified id.
        :param browser: the browser
        :param form_id: the form element id
        :return: 
        """
        browser.select_form('form#'+form_id)
