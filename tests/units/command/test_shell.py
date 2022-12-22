import unittest
import ddt

from easy2use.command import shell


@ddt.ddt
class ShellTestCases(unittest.TestCase):

    def setUp(self) -> None:
        pass

    @ddt.data((None, shell.DockerCmd),
              (shell.DOCKER, shell.DockerCmd),
              (shell.PODMAN, shell.PodmanCmd))
    def test_get_container_impl(self, impl_list):
        cmd = shell.get_container_impl(impl=impl_list[0])
        self.assertEqual(cmd, impl_list[1])
