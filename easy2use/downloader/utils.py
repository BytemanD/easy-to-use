import argparse
from urllib import parse as urllib_parse
from easy2use.downloader.urllib import driver as urllib_driver
from easy2use.downloader.wget import driver as wget_driver


def get_download_driver(use_wget=False, workers=None):
    cls = use_wget and wget_driver.WgetDriver or urllib_driver.Urllib3Driver
    return cls(progress=True, workers=workers)


def get_urls(url: str, direct=False, regex=None):
    if url.startswith('http://') or url.startswith('https://'):
        if direct:
            urls = [url]
        else:
            links = urllib_driver.find_links(url, link_regex=regex)
            urls = [urllib_parse.urljoin(url, link) for link in links]
    else:
        with open(url) as f:
            urls = [line.strip() for line in f.readlines()]
    return urls


def download(urls, use_wget=False, workers=None):
    downloader = get_download_driver(use_wget=use_wget, workers=workers)
    downloader.download_urls(urls)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='Download path, url or file'),
    parser.add_argument('-r', '--regex', help='Url regex'),
    parser.add_argument('-w', '--workers', type=int, help='Download workers'),
    parser.add_argument('--direct', action='store_true',
                        help='Download url direct')
    parser.add_argument('--wget', action='store_true', help='Use wget driver')
    args = parser.parse_args()

    urls = get_urls(args.url, direct=args.direct, regex=args.regex)
    if not urls:
        print('Nothing to do')
        return

    download(urls, use_wget=args.wget, workers=args.workers)
    print(f'Downloaded {len(urls)} link(s)')


if __name__ == '__main__':
    main()
