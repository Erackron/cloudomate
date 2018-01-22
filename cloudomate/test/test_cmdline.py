from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
import unittest
from argparse import Namespace

import cloudomate.cmdline as cmdline
from cloudomate.hoster.vpn.azirevpn import AzireVpn
from cloudomate.hoster.vps.linevast import LineVast
from cloudomate.hoster.vps.vpsoption import VpsOption
from cloudomate.util.settings import Settings
from mock.mock import MagicMock


class TestCmdLine(unittest.TestCase):
    def setUp(self):
        self.config = Settings()
        self.config.read_settings("resources/test_settings.cfg")

    # TODO: Implement get_metadata for VPS providers
    @unittest.skip("Implement get_metadata for VPS providers first")
    def test_execute_vps_list(self):
        command = ["vps", "list"]
        cmdline.execute(command)

    def test_execute_vpn_list(self):
        command = ["vpn", "list"]
        cmdline.execute(command)

    # TODO: Implement get_metadata for VPS providers
    @unittest.skip("Implement get_metadata for VPS providers first")
    def test_execute_vps_options(self):
        mock_method = self._mock_vps_options()
        command = ["vps", "options", "linevast"]
        cmdline.providers["vps"]["linevast"].configurations = []
        cmdline.execute(command)
        mock_method.assert_called_once()

    def test_execute_vpn_options(self):
        mock_method = self._mock_vpn_options()
        command = ["vpn", "options", "azirevpn"]
        cmdline.providers["vpn"]["azirevpn"].configurations = []
        cmdline.execute(command)
        mock_method.assert_called_once()

    # TODO: Implement get_metadata for VPS providers
    @unittest.skip("Implement get_metadata for VPS providers first")
    def test_execute_vps_purchase(self):
        self._mock_vps_options([self._create_option()])
        LineVast.purchase = MagicMock()
        command = ["vps", "purchase", "linevast", "-f", "-c", "resources/test_settings.cfg", "-rp", "asdf", "0"]
        cmdline.execute(command)
        LineVast.purchase.assert_called_once()

    @staticmethod
    def _create_option():
        return VpsOption(
            name="Option name",
            ram="Option ram",
            cpu="Option cpu",
            storage="Option storage",
            bandwidth="Option bandwidth",
            price=12,
            currency="Option currency",
            connection="Option connection",
            purchase_url="Option url"
        )

    # TODO: Implement get_metadata for VPS providers
    @unittest.skip("Implement get_metadata for VPS providers first")
    def test_execute_vps_purchase_verify_options_failure(self):
        command = ["vps", "purchase", "linevast", "-f", "-c", "resources/test_settings.cfg", "1"]
        self._check_exit_code(2, cmdline.execute, command)

    # TODO: Implement get_metadata for VPS providers
    @unittest.skip("Implement get_metadata for VPS providers first")
    def test_execute_vps_purchase_unknown_provider(self):
        command = ["vps", "purchase", "nonode", "-f", "-rp", "asdf", "1"]
        self._check_exit_code(2, cmdline.execute, command)

    # TODO: Implement get_metadata for VPS providers
    @unittest.skip("Implement get_metadata for VPS providers first")
    def test_execute_vps_options_unknown_provider(self):
        command = ["vps", "options", "nonode"]
        self._check_exit_code(2, cmdline.execute, command)

    def _check_exit_code(self, exit_code, method, args):
        try:
            method(args)
        except SystemExit as e:
            self.assertEqual(e.code, exit_code)

    def test_execute_vps_options_no_provider(self):
        command = ["vps", "options"]
        self._check_exit_code(2, cmdline.execute, command)

    def test_purchase_vps_unknown_provider(self):
        args = Namespace()
        args.provider = "sd"
        args.type = 'vpn'
        self._check_exit_code(2, cmdline.purchase, args)

    def test_purchase_no_provider(self):
        args = Namespace()
        self._check_exit_code(2, cmdline.purchase, args)

    # TODO: Implement get_metadata for VPS providers
    @unittest.skip("Implement get_metadata for VPS providers first")
    def test_purchase_vps_bad_provider(self):
        args = Namespace()
        args.provider = False
        args.type = "vps"
        self._check_exit_code(2, cmdline.purchase, args)

    def test_purchase_bad_type(self):
        args = Namespace()
        args.provider = "azirevpn"
        args.type = False
        self._check_exit_code(2, cmdline.purchase, args)

    # TODO: Implement get_metadata for VPS providers
    @unittest.skip("Implement get_metadata for VPS providers first")
    def test_execute_vps_purchase_high_id(self):
        self._mock_vps_options()
        command = ["vps", "purchase", "linevast", "-c", "resources/test_settings.cfg", "-rp", "asdf", "1000"]
        self._check_exit_code(1, cmdline.execute, command)

    # TODO: Implement get_metadata for VPS providers
    @unittest.skip("Implement get_metadata for VPS providers first")
    def test_execute_vps_purchase_low_id(self):
        mock = self._mock_vps_options()
        command = ["vps", "purchase", "linevast", "-c", "resources/test_settings.cfg", "-rp", "asdf", "-1"]
        self._check_exit_code(1, cmdline.execute, command)
        mock.assert_called_once()

    @staticmethod
    def _mock_vps_options(items=None):
        if items is None:
            items = []
        LineVast.options = MagicMock(return_value=items)
        return LineVast.options

    @staticmethod
    def _mock_vpn_options(items=None):
        if items is None:
            items = []
        AzireVpn.get_options = MagicMock(return_value=items)
        return AzireVpn.get_options


if __name__ == '__main__':
    unittest.main(exit=False)
