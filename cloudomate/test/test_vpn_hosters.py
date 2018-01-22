from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
import unittest

import requests

from cloudomate.hoster.hoster import Hoster
from cloudomate import wallet
from cloudomate.hoster.vpn.azirevpn import AzireVpn
from cloudomate.util.settings import Settings


from mock.mock import MagicMock
from parameterized import parameterized

providers = [
    (AzireVpn,),
]


class TestHosters(unittest.TestCase):
    def setUp(self):
        self.settings = Settings()
        self.settings.read_settings("resources/test_settings.cfg")

    @parameterized.expand(providers)
    def test_vpn_hoster_options(self, hoster):
        options = hoster.get_options()
        self.assertTrue(len(list(options)) > 0)

    @parameterized.expand(providers)
    def test_vpn_hoster_configuration(self, hoster):
        config = hoster(self.settings).get_configuration()
        self.assertTrue(len(config) > 0)



if __name__ == '__main__':
    unittest.main()
