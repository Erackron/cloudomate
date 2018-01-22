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
from cloudomate.hoster.vps.blueangelhost import BlueAngelHost
from cloudomate.hoster.vps.ccihosting import CCIHosting
from cloudomate.hoster.vps.crowncloud import CrownCloud
from cloudomate.hoster.vps.linevast import LineVast
from cloudomate.hoster.vps.pulseservers import Pulseservers
from cloudomate.hoster.vps.undergroundprivate import UndergroundPrivate
from cloudomate.hoster.vps.vps_hoster import VpsHoster
from cloudomate.hoster.vps.vpsoption import VpsOption
from mock.mock import MagicMock
from parameterized import parameterized

providers = [
    (BlueAngelHost,),
    (CCIHosting,),
    (CrownCloud,),
    (LineVast,),
    (Pulseservers,),
    (UndergroundPrivate,),
]


class TestHosters(unittest.TestCase):
    @parameterized.expand(providers)
    def test_hoster_options(self, hoster):
        options = hoster.get_options()
        self.assertTrue(len(list(options)) > 0)


class TestHosterAbstract(unittest.TestCase):

    def test_create_browser(self):
        browser = Hoster._create_browser()
        if browser.session.headers['user-agent'] == requests.utils.default_user_agent():
            self.fail('No Custom User-agent set in browser')

    # TODO: Move to eventual VpsHosterTest
    @staticmethod
    def _create_option():
        return VpsOption(
            name="Option name",
            ram="Option ram",
            cpu="Option cpu",
            storage="Option storage",
            bandwidth="Option bandwidth",
            price=12,
            currency="USD",
            connection="Option connection",
            purchase_url="Option url"
        )


if __name__ == '__main__':
    unittest.main()
