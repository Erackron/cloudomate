from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
import unittest
import sys

from parameterized import parameterized
from mock.mock import MagicMock

from cloudomate.exceptions.vps_out_of_stock import VPSOutOfStockException
from cloudomate.hoster.vps.blueangelhost import BlueAngelHost
from cloudomate.hoster.vps.ccihosting import CCIHosting
from cloudomate.hoster.vps.crowncloud import CrownCloud
from cloudomate.hoster.vps.legionbox import LegionBox
from cloudomate.hoster.vps.linevast import LineVast
from cloudomate.hoster.vps.pulseservers import Pulseservers
from cloudomate.hoster.vps.undergroundprivate import UndergroundPrivate

from cloudomate.util.fakeuserscraper import UserScraper

providers = [
    (LineVast,),  # TODO: Find out why the integration test for this one is unstable
    (BlueAngelHost,),
    (CCIHosting,),
    (CrownCloud,),
    (LegionBox,),
    (Pulseservers,),
    (UndergroundPrivate,),
]


class TestHosters(unittest.TestCase):
    @parameterized.expand(providers)
    def test_hoster_options(self, hoster):
        options = hoster().start()
        self.assertTrue(len(list(options)) > 0)

    @parameterized.expand(providers)
    @unittest.skipIf(len(sys.argv) >= 2 and sys.argv[1] == 'discover', 'Integration tests have to be run manually')
    def test_hoster_purchase(self, hoster):
        user_settings = UserScraper().get_user()
        host = hoster()
        options = list(host.start())[0]
        wallet = MagicMock()
        wallet.pay = MagicMock()

        try:
            host.purchase(user_settings, options, wallet)
            wallet.pay.assert_called_once()
        except VPSOutOfStockException as exception:
            self.skipTest(exception)


if __name__ == '__main__':
    unittest.main()
