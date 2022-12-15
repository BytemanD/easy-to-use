import logging
import sys

try:
    import subprocess
except ImportError:
    import commands as subprocess                     # noqa

LOG = logging.getLogger(__name__)

DOCKER = 'docker'
PODMAN = 'podman'


def run_popen(cmd):
    LOG.debug('Run: %s', ' '.join(cmd))
    popen = subprocess.Popen(cmd, stdout=sys.stdout)
    popen.wait()
    LOG.debug('Return: %s', popen.returncode)
    return popen.returncode


class DockerCmd(object):
    cmd = DOCKER

    @classmethod
    def build(cls, path='./', network=None, build_args=None, target=None,
              no_cache=False):
        cmd = [cls.cmd, 'build']
        if network:
            cmd.extend(['--network', network])
        if no_cache:
            cmd.append('--no-cache')
        if build_args:
            for arg in build_args:
                cmd.extend(['--build-arg', arg])
        if target:
            cmd.extend(['-t', target])
        cmd.append(path)
        status = run_popen(cmd)
        if status != 0:
            raise RuntimeError(f'docker build return {status}')

    @classmethod
    def tag(cls, image, tag):
        status = run_popen([cls.cmd, 'tag', image, tag])
        if status != 0:
            raise RuntimeError(f'docker tag return {status}')

    @classmethod
    def push(cls, image):
        LOG.info('try to push: %s', image)
        status = run_popen([cls.cmd, 'push', image])
        if status != 0:
            raise RuntimeError(f'docker push return {status}')

    @classmethod
    def tag_and_push(cls, image, tag):
        cls.tag(image, tag)
        cls.push(tag)


class PodmanCmd(DockerCmd):
    cmd = PODMAN


def get_container_impl(impl=None):
    return PodmanCmd if impl == PODMAN else DockerCmd
