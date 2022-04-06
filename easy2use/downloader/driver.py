import abc
from concurrent import futures

from easy2use.cores import log

LOG = log.getLogger(__name__)
DEFAULT_WORKERS = 10


class BaseDownloadDriver(object):

    def __init__(self, download_dir=None, timeout=60, workers=None,
                 progress=False, headers=None, keep_full_path=False):
        self.download_dir = download_dir or './'
        self.workers = workers or DEFAULT_WORKERS
        self.progress = progress
        self.timeout = timeout
        self.headers = headers
        self.keep_full_path = keep_full_path

    def download_urls(self, url_list):
        with futures.ThreadPoolExecutor(self.workers) as executor:
            results = executor.map(self.download_url, url_list)

        for result in results:
            LOG.debug('completed %s', result)

    def download_url(self, url):
        LOG.debug('download %s to %s', url, self.download_dir)
        try:
            return self.download(url)
        except Exception as e:
            LOG.exception(e)

    @abc.abstractmethod
    def download(self, url):
        """Download by specified url

        Args:
            url ([string]): http or https url
        """
        pass
