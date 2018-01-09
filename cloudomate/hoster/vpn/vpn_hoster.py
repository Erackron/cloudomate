from abc import abstractmethod

from cloudomate.hoster.hoster import Hoster
from collections import namedtuple


VpnConfiguration = namedtuple('VpnConfiguration', ['username', 'password', 'ovpn'])
VpnOption = namedtuple('VpnOption', ['name', 'protocol', 'price', 'bandwidth', 'speed'])  # Price in USD
VpnStatus = namedtuple('VpnStatus', ['online', 'expiration'])   # Online is a boolean, expiration an ISO datetime


class VpnHoster(Hoster):
    @abstractmethod
    def get_configuration(self):
        """Get Hoster configuration.

        :return: Returns VpnConfiguration for the VPN Hoster instance
        """
        pass

    @classmethod
    @abstractmethod
    def get_options(cls):
        """Get Hoster options.

        :return: Returns list of VpnOption objects
        """
        pass

    @abstractmethod
    def get_status(self):
        """Get Hoster configuration.

        :return: Returns VpnStatus of the VPN Hoster instance
        """
        pass