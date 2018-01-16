import sys

from cloudomate.hoster.vps.vps_hoster import VpsHoster
from mechanicalsoup import LinkNotFoundError
from bs4 import BeautifulSoup


class SolusvmHoster(VpsHoster):
    def _fill_server_form(self):
        """Fills the server configuration form (should be currently selected) as much as possible

        """
        form = self._browser.get_current_form()

        try:
            form['hostname'] = self._settings.get('server', 'hostname')
        except LinkNotFoundError:
            pass

        try:
            form['rootpw'] = self._settings.get('server', 'rootpw')
        except LinkNotFoundError:
            pass

        try:
            form['ns1prefix'] = self._settings.get('server', 'ns1')
            form['ns2prefix'] = self._settings.get('server', 'ns2')
        except LinkNotFoundError:
            pass

        # As an alternative to the default Ajax request
        form.new_control('hidden', 'a', 'confproduct')
        form.new_control('hidden', 'ajax', '1')
        form.form['method'] = 'get'

    def _fill_user_form(self, payment_method, errorbox_class='checkout-error-feedback'):
        """Fills the user information form (should be currently selected) as much as possible

        :param payment_method: the name of the payment method
        :param errorbox_class: the class of the div element containing error messages
        :return: the page received after submitted the form
        """
        form = self._browser.get_current_form()

        form['firstname'] = self._settings.get('user', "firstname")
        form['lastname'] = self._settings.get('user', "lastname")
        form['email'] = self._settings.get('user', "email")
        form['phonenumber'] = self._settings.get('user', "phonenumber")
        form['companyname'] = self._settings.get('user', "companyname")
        form['address1'] = self._settings.get('user', "address")
        form['city'] = self._settings.get('user', "city")
        form['state'] = self._settings.get('user', "state")
        form['postcode'] = self._settings.get('user', "zipcode")
        form['country'] = self._settings.get('user', 'countrycode')
        form['password'] = self._settings.get('user', "password")
        form['password2'] = self._settings.get('user', "password")
        form['paymentmethod'] = payment_method

        try:
            form['accepttos'] = True  # Attempt to accept the terms and conditions
        except LinkNotFoundError:
            pass

        page = self._browser.submit_selected()

        # Error handling
        if 'checkout' in page.url:
            soup = BeautifulSoup(page.text, 'lxml')
            errors = soup.find('div', {'class': errorbox_class}).text
            print((errors.strip()))
            sys.exit(2)

        return page
