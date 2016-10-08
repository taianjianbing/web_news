# from scrapy import log
import logging as log


def warn(msg):
    # log.msg(str(msg), level=log.WARNING)
    log.warning(str(msg))


def info(msg):
    # log.msg(str(msg), level=log.INFO)
    log.info(str(msg))


def debug(msg):
    # log.msg(str(msg), level=log.DEBUG)
    log.debug(str(msg))
