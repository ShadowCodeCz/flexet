import os
import re
import glob

import yapsy.IPlugin

from . import exception


class ExceptionMessage:
    component = "[Node]"

    @classmethod
    def node_failed(cls, obj, data, cfg):
        return f"{cls.component} Node '{cfg.alias}' failed"


class Plugin(yapsy.IPlugin.IPlugin):
    names = []
    description = ""

    def __init__(self):
        super().__init__()
        self.cfg = None
        self.data = None

    @exception.handle(ExceptionMessage.node_failed)
    def run(self, data, cfg):
        self.data = data
        self.cfg = cfg
        return self._run(data, cfg)

    def _run(self, data, cfg):
        pass


class DefaultNode(Plugin):
    pass


class ReInString(DefaultNode):
    names = ["ReInString", "re"]

    def _run(self, data, cfg):
        pattern = re.compile(cfg.parameters["re"], re.MULTILINE)
        s = data[cfg.parameters["str_key"]]
        return {cfg.alias: True} if pattern.search(s) else {cfg.alias: False}


class NotReInString(DefaultNode):
    names = ["NotReInString", "nre"]

    def run(self, data, cfg):
        n = ReInString()
        d = n.run(data, cfg)
        return {cfg.alias: not d[cfg.alias]}


class ResInString(DefaultNode):
    names = ["ResInString", "res"]

    def _run(self, data, cfg):
        s = data[cfg.parameters["str_key"]]

        results = {}
        for key, regular_expression in cfg.parameters["res"].items():
            pattern = re.compile(regular_expression, re.DOTALL)
            results[key] = True if pattern.search(s) else False

        return {cfg.alias: results}


class NotResInString(DefaultNode):
    names = ["NotResInString", "nres"]

    def run(self, data, cfg):
        n = ResInString()
        d = n.run(data, cfg)
        r = {k: not v for k, v in d[cfg.alias].items()}
        return {cfg.alias: r}


class TextFileReader(DefaultNode):
    names = ["TextFileReader", "tfr"]

    def _run(self, data, cfg):
        with open(cfg.parameters["path"]) as file:
            return {cfg.alias: file.read()}


class FileLocator(DefaultNode):
    names = ["FileLocator", "floc"]

    def _run(self, data, cfg):
        wd = cfg.parameters["working_directory"]
        template = cfg.parameters["template"]

        if "recursive" in cfg.parameters:
            recursive = True if cfg.parameters["recursive"] == "True" else False
        else:
            recursive = False

        pattern = os.path.join(wd, template)

        results = glob.glob(pattern, recursive=recursive)
        try:
            return {cfg.alias: results[0]}
        except Exception as e:
            return {cfg.alias: None}
