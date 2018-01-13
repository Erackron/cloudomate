from abc import abstractmethod

from cloudomate.hoster.hoster import Hoster
from collections import namedtuple


VpsConfiguration = namedtuple('VpsConfiguration', ['ip', 'root_password'])
VpsOption = namedtuple('VpsOption', ['name',
                                     'cores',
                                     'memory',          # Memory in GB
                                     'storage',         # Storage in GB
                                     'bandwidth',
                                     'connection',
                                     'price',           # Price in USD
                                     'purchase_url'])

VpsStatus = namedtuple('VpsStatus', ['memory_used',
                                     'storage_used',
                                     'bandwidth_used',
                                     'online',          # Boolean
                                     'expiration'])     # ISO datetime


class VpsHoster(Hoster):
    # TODO: Find out if get_clientarea_url should be implemented as a method

    @abstractmethod
    def get_configuration(self):
        """Get Hoster configuration.

        :return: Returns VpsConfiguration for the VPS Hoster instance
        """
        pass

    @classmethod
    @abstractmethod
    def get_options(cls):
        """Get Hoster options.

        :return: Returns list of VpsOption objects
        """
        pass

    @abstractmethod
    def get_status(self):
        """Get Hoster configuration.

        :return: Returns VpsStatus of the VPS Hoster instance
        """
        pass

    @abstractmethod
    def set_root_password(self, password):
        """Set Hoster root password

        :param password: The root password to set
        """
