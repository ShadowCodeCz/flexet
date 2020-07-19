import re
import os
import glob
import json


class AbstractSubCollector:
    def handle(self, configuration):
        files = []
        for directory in configuration.directories:
            all_files = glob.glob(os.path.join(directory, "**"), recursive=True)
            for template in configuration.templates:
                files += self._filter_related_files(all_files, template)

        return {self._file_key(f): self._file_content(f) for f in files}

    def _filter_related_files(self, files, template):
        pattern = re.compile(template, re.DOTALL)
        return [f for f in files if pattern.match(f)]

    def _file_key(self, path):
        file_name = os.path.basename(path)
        return file_name.split(".")[0]

    def _file_content(self, path):
        pass


class JsonPFCollector(AbstractSubCollector):
    def check(self, pf_collector_configuration):
        return pf_collector_configuration.type == "pf.json"

    def _file_content(self, path):
        if path:
            with open(path) as f:
                return json.load(f)
        else:
            return {}
