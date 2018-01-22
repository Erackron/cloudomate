from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import open
from future import standard_library
standard_library.install_aliases()
import os
import unittest

from cloudomate.hoster.vps.crowncloud import CrownCloud


class TestCrownCloud(unittest.TestCase):
    @unittest.skip("Needs updating")
    def test_emails(self):
        html_file = open(os.path.join(os.path.dirname(__file__), 'resources/crowncloud_email.html'), 'r')
        data = html_file.read()
        info = CrownCloud._extract_email_info(data)
        self.assertEqual(info, ('000.000.000.000', 'paneluserxxxx', 'xxxx'))


if __name__ == '__main__':
    unittest.main(exit=False)
