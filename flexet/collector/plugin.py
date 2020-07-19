import generic_design_patterns as gdp


class AbstractSubCollector(gdp.chain.ChainNodePlugin):
    @staticmethod
    def _build_plugins_dict(plugins):
        d = {}
        for plugin in plugins:
            for name in plugin.names:
                d[name] = plugin
        return d


class RePluginSubCollector(AbstractSubCollector):
    def check(self, plugin_collector_cfg):
        return plugin_collector_cfg.type == "plugin.re"

    def handle(self, plugin_collector_cfg):
        plugins = []
        for template in plugin_collector_cfg.templates:
            collector = gdp.plugin.YapsyRegExPluginCollector(plugin_collector_cfg.directories, template)
            plugins += collector.collect()
        return self._build_plugins_dict(plugins)


class SubclassPluginSubCollector(AbstractSubCollector):
    def check(self, plugin_collector_cfg):
        return plugin_collector_cfg.type == "plugin.subclass"

    def handle(self, plugin_collector_cfg):
        plugins = []
        # https://stackoverflow.com/questions/3862310/how-to-find-all-the-subclasses-of-a-class-given-its-name

        for c in plugin_collector_cfg.classes:
            collector = gdp.plugin.SubclassPluginCollector(c)
            plugins += collector.collect()
        return self._build_plugins_dict(plugins)

