import mock
import unittest
import ddt

from easy2use.common import pkg


@ddt.ddt
class PackageVersionTestCases(unittest.TestCase):

    def setUp(self) -> None:
        self.version_002 = pkg.PackageVersion('0.0.2')
        return super().setUp()

    @ddt.data(('0.0.2', '0.0.1', 1), ('0.0.2', '0.0.2', 0),
              ('0.0.2', '0.0.3', -1), ('0.0.2', '0.0.2.dev1', 1),
              ('0.0.2', '0.0.3.dev1', -1),
              ('0.0.2.dev1', '0.0.2.dev2', -1),
              ('0.0.1.dev1', '0.0.2', -1),
              ('0.0.1.dev1', '0.0.1.dev1', 0),
              )
    def test_compare(self, version):
        version1, version2 = version[0], version[1]
        package_version1 = pkg.PackageVersion(version1)
        package_version2 = pkg.PackageVersion(version2)

        if version[2] > 0:
            self.assertGreater(package_version1, package_version2)
        elif version[2] == 0:
            self.assertEqual(package_version1, package_version2)
        elif version[2] < 0:
            self.assertLess(package_version1, package_version2)
