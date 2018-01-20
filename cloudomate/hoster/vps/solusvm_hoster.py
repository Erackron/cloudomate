import sys

from mechanicalsoup import LinkNotFoundError
from bs4 import BeautifulSoup
from abc import abstractmethod
import datetime

from cloudomate.hoster.vps.vps_hoster import VpsConfiguration
from cloudomate.hoster.vps.vps_hoster import VpsHoster
from cloudomate.hoster.vps.vps_hoster import VpsStatus
from cloudomate.hoster.vps.clientarea import ClientArea


class SolusvmHoster(VpsHoster):
    """
    SolusvmHoster is the common superclass of all VPS hosters that make use of the Solusvm management package.
    This makes it possible to fill in the registration form in a similar manner for all Solusvm subclasses.
    """

    '''
    Methods that are the same for all subclasses
    '''

    def get_configuration(self):
        url = self.get_clientarea_url()
        clientarea = ClientArea(self._browser, url, self._settings)

        ip = clientarea.get_ip()
        password = self._settings.get('server', 'rootpw')

        return VpsConfiguration(ip, password)

    def get_status(self):
        url = self.get_clientarea_url()
        clientarea = ClientArea(self._browser, url, self._settings)

        services = clientarea.get_services()
        service = services[0]  # Only look at the first one (cloudomate supports just one server per account)
        online = True if service['status'] == 'active' else False
        expiration = datetime.datetime.strptime(service['next_due_date'], '%Y-%m-%d')

        # TODO: Also retrieve used bandwidth, etc. if possible

        return VpsStatus(-1, -1, -1, online, expiration)

    def set_root_password(self, password):
        url = self.get_clientarea_url()
        clientarea = ClientArea(self._browser, url, self._settings)

        if clientarea.set_rootpw_rootpassword_php(password):
            # Succes, save
            self._settings.put('server', 'rootpw', password)
            self._settings.save_settings()

    '''
    Static methods that must be overwritten by subclasses
    '''

    @staticmethod
    @abstractmethod
    def get_clientarea_url():
        """Get the url of the clientarea for this hoster

        :return: Returns the clientarea url
        """
        pass

    '''
    Methods that are used by subclasses to fill parts of the forms that are shared between hosters
    '''

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
            # TODO: Properly handle this warning
            print('Couldn\'t set root password')

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
        form['address1'] = self._settings.get('address', "address")
        form['city'] = self._settings.get('address', "city")
        form['state'] = self._settings.get('address', "state")
        form['postcode'] = self._settings.get('address', "zipcode")
        form['country'] = self._settings.get('address', 'countrycode')
        form['password'] = self._settings.get('user', "password")
        form['password2'] = self._settings.get('user', "password")
        form['paymentmethod'] = payment_method.lower()

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
