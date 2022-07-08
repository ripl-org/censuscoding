import logging

class Log(object):
    """
    Extends the built-in logging module to support
    """

    def __init__(self, *names):
        self.name = ":".join(names)
        self.log = logging.getLogger(self.name)
        self.prefix = ""

    def set_prefix(self, prefix):
        self.prefix = prefix

    def debug(self, *message, sep=" "):
        if self.prefix:
            self.log.debug(" {} {}".format(self.prefix, sep.join(map(str, message))))
        else:
            self.log.debug(" {}".format(sep.join(map(str, message))))

    def error(self, *message, sep=" "):
        if self.prefix:
            self.log.error(" {} {}".format(self.prefix, sep.join(map(str, message))))
        else:
            self.log.error(" {}".format(sep.join(map(str, message))))

    def info(self, *message, sep=" "):
        if self.prefix:
            self.log.info(" {} {}".format(self.prefix, sep.join(map(str, message))))
        else:
            self.log.info(" {}".format(sep.join(map(str, message))))

    def warn(self, *message, sep=" "):
        if self.prefix:
            self.log.warn(" {} {}".format(self.prefix, sep.join(map(str, message))))
        else:
            self.log.warn(" {}".format(sep.join(map(str, message))))

log = Log("censuscoding")
