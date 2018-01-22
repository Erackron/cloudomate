from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
import unittest

from cloudomate.hoster.vps.linevast import LineVast


class TestLinevast(unittest.TestCase):
    def test_check_set_rootpw(self):
        data = '{"success":"1","updtype":"1","apistate":"1"}'
        self.assertTrue(LineVast._check_set_rootpw(data))

    def test_check_set_rootpw_false(self):
        data = '{"success":"1","updtype":"null","apistate":"1"}'
        self.assertFalse(LineVast._check_set_rootpw(data))


if __name__ == '__main__':
    unittest.main(exit=False)
