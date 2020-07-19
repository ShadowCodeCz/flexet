import copy
import argparse
import jsonmerge

from . import cli
from . import node
from . import parser
from . import collector
from . import configuration

# TODO: Type annotations


# TODO: include layers from other net JSON CFG
def build_by_cfg(cfg_path, default_collectors=True):
    # TODO: rework code is same as for build_by_dict
    net_parser = parser.NetConfigurationParser()
    cfg = net_parser.parse_file(cfg_path)
    return build(cfg, default_collectors)


def build_by_dict(raw_cfg, default_collectors=True):
    # TODO: rework code is same as for build_by_cfg
    net_parser = parser.NetConfigurationParser()
    cfg = net_parser.parse_dict(raw_cfg)
    return build(cfg, default_collectors)


def build(cfg, default_collectors=True):
    builder = Builder()
    return builder.build(cfg, default_collectors)


class Builder:
    def __init__(self):
        self.cfg = None
        self.parametric_files = None
        self.plugins = None
        self.layers = []
        self.default_collectors = None

    def build(self, cfg, default_collectors=True):
        self.cfg = cfg
        self.default_collectors = default_collectors

        self._collect_plugins()
        self._collect_parametric_files()
        self._build_layers()

        return Flexet(copy.deepcopy(self.layers))

    def _collect_plugins(self):
        self._append_default_plugin_collectors()
        plugin_collector = collector.PluginCollector()
        self.plugins = plugin_collector.collect(self.cfg.plugin_collectors)

    def _append_default_plugin_collectors(self):
        if self.default_collectors:
            default_node_collector_cfg = configuration.SubclassCollectorConfiguration()
            # TODO: fix node.type string
            default_node_collector_cfg.type = "plugin.subclass"
            default_node_collector_cfg.classes = [node.DefaultNode]
            self.cfg.plugin_collectors.append(default_node_collector_cfg)

    def _collect_parametric_files(self):
        pf_collector = collector.ParametricFileCollector()
        self.parametric_files = pf_collector.collect(self.cfg.parametric_file_collectors)

    def _build_layers(self):
        # TODO: exception, split it
        self.layers = []
        for raw_layer in self.cfg.layers:
            layer = []
            for raw_node_cfg in raw_layer:
                nc = configuration.NodeConfiguration()
                nc.alias = raw_node_cfg.alias
                self._bind_node_plugin(nc, raw_node_cfg)
                self._build_node_parameters(nc, raw_node_cfg)
                layer.append(Node(nc))
            self.layers.append(layer)

    def _bind_node_plugin(self, nc, raw_node_cfg):
        # TODO: exception
        nc.plugin = self.plugins[raw_node_cfg.plugin_name]

    def _build_node_parameters(self, nc, raw_node_cfg):
        # TODO: exception
        parameters_from_file = self.parametric_files[
            raw_node_cfg.parametric_file] if raw_node_cfg.parametric_file else {}
        nc.parameters = jsonmerge.merge(parameters_from_file,
                                        raw_node_cfg.inline_parameters)


class Node:
    def __init__(self, cfg):
        self.cfg = cfg

    def run(self, data):
        return self.cfg.plugin.run(data, self.cfg)


class Flexet:
    def __init__(self, layers):
        self.layers = layers

    def run(self, data):
        local_data = copy.deepcopy(data)
        for layer in self.layers:
            for node in layer:
                r = node.run(local_data)
                local_data = jsonmerge.merge(local_data, r)

        return local_data

    def __add__(self, other):
        return Flexet(self.layers + other.layers)


def main():
    parser = argparse.ArgumentParser(description="",
                                     formatter_class=argparse.RawTextHelpFormatter)
    subparsers = parser.add_subparsers()

    generator_parser = subparsers.add_parser('gen')
    generator_parser.set_defaults(func=cli.generate_initial_cfg)

    arguments = parser.parse_args()
    arguments.func(arguments)


if __name__ == "__main__":
    main()

