import re
import json

from . import configuration
from . import exception


class CfgKey:
    collectors = "collectors"
    collector_type = "type"
    directories = "directories"
    templates = "templates"
    classes = "classes"
    layers = "layers"


class CollectorType:
    plugin = "plugin"
    pf = "pf"


class ExceptionMessage:
    component = "[CFG Parser]"

    @classmethod
    def incorrect_collector_type(cls, _, raw_collector_cfg):
        return f"{cls.component} Missing or incorrect collector type: {raw_collector_cfg}"

    @classmethod
    def incorrect_collector_cfg(cls, _, raw_collector_cfg):
        return f"{cls.component} Incorrect collector configuration: {raw_collector_cfg}"

    @classmethod
    def incorrect_node_cfg(cls, _, raw_node_configuration):
        return f"{cls.component} Incorrect node configuration: {raw_node_configuration}"

    @classmethod
    def reading_cfg_file_fail(cls, _, cfg_path):
        return f"{cls.component} Reading CFG file '{cfg_path}' failed."


# TODO: Parallel network: add protection. ParaNet can use only dict CFG and subclass collector.


class NetConfigurationParser:
    def __init__(self):
        self.cfg = None
        self.node_parser = NodeConfigurationParser()
        self.collector_parser_map = {
            "plugin.re": self._parse_file_collector,
            "plugin.subclass": self._parse_plugin_subclass_collector,
            "pf.json": self._parse_file_collector
        }
        self._source = "dict"

    def parse_file(self, cfg_path):
        self._source = "file"
        cfg = self.parse_dict(self._read_cfg(cfg_path))
        self._source = "dict"
        return cfg

    @exception.handle(ExceptionMessage.reading_cfg_file_fail)
    def _read_cfg(self, cfg_path):
        with open(cfg_path) as cfg_file:
            return json.load(cfg_file)

    def parse_dict(self, raw_cfg):
        self.cfg = configuration.NetConfiguration()

        self._parse_collectors(raw_cfg)
        self._parse_layers(raw_cfg)

        return self.cfg

    def _parse_collectors(self, raw_cfg):
        if CfgKey.collectors in raw_cfg:
            for raw_collector_cfg in raw_cfg[CfgKey.collectors]:
                self._parse_collector(raw_collector_cfg)

    def _parse_collector(self, raw_collector_cfg):
        collector_parser = self._collector_parser(raw_collector_cfg)
        collector = collector_parser(raw_collector_cfg)
        self._append_collector_to_cfg(collector)

    def _append_collector_to_cfg(self, collector):
        if CollectorType.plugin in collector.type:
            self.cfg.plugin_collectors.append(collector)
        if CollectorType.pf in collector.type:
            self.cfg.parametric_file_collectors.append(collector)

    @exception.handle(ExceptionMessage.incorrect_collector_type)
    def _collector_parser(self, raw_collector_cfg):
        raw_type = raw_collector_cfg[CfgKey.collector_type]
        return self.collector_parser_map[raw_type]

    @exception.handle(ExceptionMessage.incorrect_collector_cfg)
    def _parse_file_collector(self, raw_collector_cfg):
        collector = configuration.FileCollectorConfiguration()
        collector.type = raw_collector_cfg[CfgKey.collector_type].strip()
        collector.directories = raw_collector_cfg[CfgKey.directories]
        collector.templates = raw_collector_cfg[CfgKey.templates]
        return collector

    @exception.handle(ExceptionMessage.incorrect_collector_cfg)
    def _parse_plugin_subclass_collector(self, raw_collector_cfg):
        self._protect_parsing_by_source()
        collector = configuration.SubclassCollectorConfiguration()
        collector.type = raw_collector_cfg[CfgKey.collector_type]
        collector.classes = raw_collector_cfg[CfgKey.classes]
        return collector

    def _protect_parsing_by_source(self):
        if self._source == "file":
            raise exception.FlexetException("File CFG cannot use subclass plugin collector. "
                                            "Only python dict CFG can use it.")

    def _parse_layers(self, raw_cfg):
        if CfgKey.layers in raw_cfg:
            for raw_layer in raw_cfg[CfgKey.layers]:
                self._parse_layer(raw_layer)

    def _parse_layer(self, raw_layer):
        layer = []
        for raw_node in raw_layer:
            node = self.node_parser.parse(raw_node)
            layer.append(node)
        self.cfg.layers.append(layer)


class NodeConfigurationParser:
    def __init__(self):
        re_node = "(((?P<alias>[^@]+)@)?((?P<plugin_name>[^:/@]+))(:(?P<parametric_file>[^/]+)?)?(/(?P<inline_parameters>.+)?)?)"
        self.node_pattern = re.compile(re_node, re.DOTALL)

        self.re_inline_parameters = "[^;=]+=[^;]+"
        re_inline_parameter = "((?P<parameter_name>[^=;]+)=(?P<parameter_value>[^=;]+))"
        self.inline_parameter_pattern = re.compile(re_inline_parameter, re.DOTALL)

    @exception.handle(ExceptionMessage.incorrect_node_cfg)
    def parse(self, raw_node_configuration):
        matches = self.node_pattern.match(raw_node_configuration)
        node_cfg = configuration.NodeRawConfiguration()
        node_cfg.alias = matches.group("alias")
        node_cfg.plugin_name = matches.group("plugin_name")

        node_cfg.parametric_file = matches.group("parametric_file")
        node_cfg.inline_parameters = self._parse_inline_parameters(matches.group("inline_parameters"))

        return node_cfg

    def _parse_inline_parameters(self, raw_inline_parameters):
        if raw_inline_parameters is None:
            return {}

        parameters_definitions = re.findall(self.re_inline_parameters, raw_inline_parameters)
        d = {}
        for parameter_definition in parameters_definitions:
            matches = self.inline_parameter_pattern.match(parameter_definition)
            d[matches.group("parameter_name")] = matches.group("parameter_value")
        return d


