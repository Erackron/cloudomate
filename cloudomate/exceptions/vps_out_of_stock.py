from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import super
from future import standard_library
standard_library.install_aliases()
class VPSOutOfStockException(Exception):
    """Exception raised when trying to purchase a VPS that is out of stock."""

    def __init__(self, vps_option, msg=None):
        if msg is None:
            msg = "VPS Option '{}' is out of stock".format(vps_option.name)
        super(Exception, self).__init__(msg)
        self.vps_option = vps_option
