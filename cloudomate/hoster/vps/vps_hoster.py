from abc import abstractmethod

from cloudomate.hoster.hoster import Hoster
from collections import namedtuple


VpsConfiguration = namedtuple('VpsConfiguration', ['ip', 'root_password'])
VpsOption = namedtuple('VpsOption', ['name',
                                     'cores',
                                     'memory',          # Memory in GB
                                     'storage',         # Storage in GB
                                     'bandwidth',       # Bandwidth in GB
                                     'connection',      # Connection speed in Gbps
                                     'price',           # Price in USD
                                     'purchase_url'])

VpsStatus = namedtuple('VpsStatus', ['memory_used',     # Memory in GB
                                     'storage_used',    # Storage in GB
                                     'bandwidth_used',  # Bandwidth used in GB
                                     'online',          # Boolean
                                     'expiration'])     # Python Datetime object


class VpsHoster(Hoster):
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
