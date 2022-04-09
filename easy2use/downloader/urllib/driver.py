import io
import os
import re
import urllib3
from urllib import parse as urllib_parse

import bs4

from easy2use.cores import log
from easy2use.common import progressbar
from easy2use.common import exceptions
from easy2use.downloader import driver

LOG = log.getLogger(__name__)

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

    def __init__(self, headers=None, **kwargs):
        super(Urllib3Driver, self).__init__(**kwargs)
        self.headers = headers
        self.filename_length = 1
        self.http = urllib3.PoolManager(num_pools=self.workers,
                                        headers=self.headers,
                                        timeout=self.timeout)

    def download_urls(self, url_list):
        self.filename_length = 1
        for url in url_list:
            file_name = os.path.basename(url)
            if len(file_name) > self.filename_length:
                self.filename_length = len(file_name)
        self.filename_length = min(self.filename_length, FILE_NAME_MAX_SIZE)
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
        super(Urllib3Driver, self).download_urls(url_list)

    def download(self, url):
        file_name = os.path.basename(url)
        resp = self.http.request('GET', url, preload_content=False)
        LOG.debug('get resp for url %s', url)
        if self.progress:
            size = resp.headers.get('Content-Length')
            pbar = size and progressbar.factory(int(size)) or \
                progressbar.ProgressNoop(0)
            desc_template = f'{{:{self.filename_length}}}'
            pbar.set_description(desc_template.format(file_name))
        else:
            pbar = progressbar.ProgressNoop(0)

        if not self.keep_full_path:
            save_path = os.path.join(self.download_dir, file_name)
        else:
            # TODO Need to be rigorously tested.
            splited = urllib_parse.urlsplit(url).path.split('/')
            save_dir = os.path.join(self.download_dir,
                                    os.path.join(*splited[1:-1]))
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            save_path = os.path.join(save_dir, file_name)
        try:
            with open(save_path, 'wb') as f:
                for data in resp.stream(io.DEFAULT_BUFFER_SIZE):
                    f.write(data)
                    pbar.update(len(data))
        except Exception as e:
            LOG.error('download %s failed %s', file_name, e)
            if os.path.exists(save_path):
                os.remove(save_path)
        finally:
            pbar.close()
            return file_name
