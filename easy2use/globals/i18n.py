# -*- coding: UTF-8 -*-
import gettext
import locale
import logging

LOG = logging.getLogger(__name__)

_ = gettext.gettext


def init(domain, locale_dir):
    global _

    locale_language = locale.getdefaultlocale()[0]
    LOG.debug('locale language: %s', locale_language)

    try:
        _ = gettext.translation(domain, locale_dir,
                                [locale_language, "en_US"]).gettext
    except FileNotFoundError:
        LOG.warning('init i18n failed')
