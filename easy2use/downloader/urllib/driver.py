import io
import logging
import os
import re
import urllib3
from urllib import parse as urllib_parse

import bs4

from easy2use.component import pbr
from easy2use.common import exceptions
from easy2use.downloader import driver

LOG = logging.getLogger(__name__)

FILE_NAME_MAX_SIZE = 50


class GetPageFailed(exceptions.BaseException):
    _msg = 'get web page failed, {error}'


def find_links(url, link_regex=None, headers=None):
    """
    >>> links = find_links('http://www.baidu.com',
    ...                    link_regex=r'.*.(jpg|png)$')
    """
    httpclient = urllib3.PoolManager(headers=headers)
    resp = httpclient.request('GET', url)
    if resp.status != 200:
        raise GetPageFailed(error=resp.data)
    html = bs4.BeautifulSoup(resp.data, features="html.parser")
    img_links = []
    regex_obj = re.compile(link_regex) if link_regex else None
    for link in html.find_all(name='a'):
        if not link.get('href'):
            continue
        if regex_obj and not regex_obj.match(link.get('href')):
            continue
        img_links.append(link.get('href'))
    return img_links


class Urllib3Driver(driver.BaseDownloadDriver):

    def __init__(self, headers=None, pool_maxsize: int = None,
                 buffer_size: int = None,
                 **kwargs):
        """URLlib3 downlad driver

        Args:
            headers (dict, optional): request headers. Defaults to None.
            pool_maxsize (int, optional): Request pool size. Defaults to None.
            buffer_size (int, optional): Buffer size. Defaults to None.
        """
        super(Urllib3Driver, self).__init__(**kwargs)
        self.headers = headers
        self.buffer_size = buffer_size or io.DEFAULT_BUFFER_SIZE
        self.filename_length = 1
        self._mid_index = 1
        self.http = urllib3.PoolManager(num_pools=self.workers,
                                        maxsize=pool_maxsize or self.workers,
                                        headers=self.headers,
                                        timeout=self.timeout)

    def download_urls(self, url_list):
        self.filename_length = min(
            *[len(os.path.basename(url)) for url in url_list],
            FILE_NAME_MAX_SIZE)
        self._mid_index = max(int(self.filename_length / 2) - 2, 1)
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
        super(Urllib3Driver, self).download_urls(url_list)

    def _format_description(self, message):
        return f'{message[:self._mid_index]}****{message[-self._mid_index:]}'

    def download(self, url):
        file_name = os.path.basename(url)
        resp = self.http.request('GET', url, preload_content=False)
        LOG.debug('get resp for url %s', url)
        size = 'Content-Length' in resp.headers and \
            int(resp.headers.get('Content-Length')) or None

        if self.progress and size:
            pbar = pbr.factory(size)
            desc_template = f'{{:{self.filename_length}}}'
            pbar.set_description(
                desc_template.format(self._format_description(file_name)))
        else:
            pbar = pbr.NopProgressBar(size)

        if not self.keep_full_path:
            save_path = os.path.join(self.download_dir, file_name)
        else:
            # TODO: Need to be rigorously tested.
            splited = urllib_parse.urlsplit(url).path.split('/')
            save_dir = os.path.join(self.download_dir,
                                    os.path.join(*splited[1:-1]))
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            save_path = os.path.join(save_dir, file_name)
        try:
            with open(save_path, 'wb') as f:
                for data in resp.stream(self.buffer_size):
                    f.write(data)
                    pbar.update(len(data))
        except Exception as e:
            LOG.error('download %s failed %s', file_name, e)
            if os.path.exists(save_path):
                os.remove(save_path)
        finally:
            pbar.close()
            return file_name
