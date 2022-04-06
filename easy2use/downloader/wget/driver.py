import os

from easy2use.cores import log
from easy2use.downloader import driver

LOG = log.getLogger(__name__)


class WgetDriver(driver.BaseDownloadDriver):
    WGET = '/usr/bin/wget'

    def download(self, url):
        cmd = [self.WGET, url, '-P', self.download_dir, '--timeout',
               str(self.timeout)]
        LOG.debug('Run cmd: %s', cmd)
        if not self.progress:
            cmd.append('-q')
        os.system(' '.join(cmd))
