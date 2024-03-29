import abc
import os
import shutil
import site
import subprocess

from easy2use import system


class MsgFmtDriver(object):

    def __init__(self, domain, i18n_dir) -> None:
        self.domain = domain
        self.i18n_dir = i18n_dir
        self.msgfmt = None

    @staticmethod
    def _run_cmd(cmd: list):
        print(f'INFO: Run cmd {cmd}')
        return subprocess.getstatusoutput(' '.join(cmd))

    @abc.abstractmethod
    def get_msgfmt(self):
        pass

    @abc.abstractmethod
    def parse_po_file(self, po_path) -> str:
        """Parse po file and return mo file path"""
        pass

    def _check_msgfmt_or_raise(self):
        self.msgfmt = self.get_msgfmt()
        if not self.msgfmt:
            raise RuntimeError('msgfmt is not found!')

    def parse(self):
        self._check_msgfmt_or_raise()

        for po_file in os.listdir(self.i18n_dir):
            if not po_file.endswith('.po'):
                continue

            po_path = os.path.join(self.i18n_dir, po_file)

            print(f'INFO: start to parse po file: {po_path}')
            mo_file = self.parse_po_file(po_path)
            if not os.path.isfile(mo_file):
                raise RuntimeError(f'mo file {mo_file} not found')

            language, _ = os.path.splitext(po_file)
            locale_path = os.path.join(self.i18n_dir, 'locale', language,
                                       'LC_MESSAGES', f'{self.domain}.mo')
            if not os.path.exists(os.path.dirname(locale_path)):
                os.makedirs(os.path.dirname(locale_path))
            shutil.move(mo_file, locale_path)

        if os.path.exists(os.path.join(self.domain, 'locale')):
            shutil.rmtree(os.path.join(self.domain, 'locale'))
        shutil.move(os.path.join(self.i18n_dir, 'locale'), self.domain)


class LinuxMsgfmtDriver(MsgFmtDriver):

    def get_msgfmt(self):
        status, output = self._run_cmd(['which', 'msgfmt'])
        if status == 0:
            return output

    def parse_po_file(self, po_path) -> str:
        output = os.path.basename(po_path)
        name, _ = os.path.splitext(output)
        mo_file = os.path.join(os.path.dirname(po_path), f'{name}.mo')
        cmd = [self.msgfmt, po_path, '-o', mo_file]
        status, output = self._run_cmd(cmd)
        if status != 0 or not mo_file:
            raise RuntimeError(f'run msgfmt failed, {output}')
        return mo_file

    def _check_msgfmt_or_raise(self):
        self.msgfmt = self.get_msgfmt()
        if not self.msgfmt:
            raise RuntimeError('msgfmt is not found!')


class WindowsMsgfmtDriver(MsgFmtDriver):

    def get_msgfmt(self):
        for path in site.getsitepackages():
            msgfmt_path = os.path.join(path, 'Tools', 'i18n', 'msgfmt.py')
            if os.path.isfile(msgfmt_path):
                return msgfmt_path
        raise RuntimeError('msgfmt is not found')

    def parse_po_file(self, po_path) -> str:
        msgfmt_cmd = ['python', self.msgfmt, po_path]
        status, output = subprocess.getstatusoutput(' '.join(msgfmt_cmd))
        if status != 0:
            raise RuntimeError(f'msgfmt faild, {output}')
        name, _ = os.path.splitext(os.path.basename(po_path))
        return os.path.join(self.i18n_dir, f'{name}.mo')


def make_i18n(domain, i18n_dir):
    driver = system.OS.is_windows() and WindowsMsgfmtDriver(domain, i18n_dir) \
        or LinuxMsgfmtDriver(domain, i18n_dir)
    driver.parse()
