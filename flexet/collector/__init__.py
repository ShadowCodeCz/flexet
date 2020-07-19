import jsonmerge
import generic_design_patterns as gdp

from . import pf
from . import plugin


class AbstractCollector:
    parent_class = None

    def __init__(self):
        collectors = [gdp.plugin.SubclassPluginCollector(self.parent_class)]
        self.chain = gdp.chain.build(collectors)

    # TODO: exception
    def collect(self, configurations):
        plugins = {}
        for configuration in configurations:
            plugins = jsonmerge.merge(plugins, self.chain.handle(configuration))
        return plugins


class PluginCollector(AbstractCollector):
    parent_class = plugin.AbstractSubCollector


class ParametricFileCollector(AbstractCollector):
    parent_class = pf.AbstractSubCollector


