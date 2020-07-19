import flexet


class SetVariable(flexet.node.Plugin):
    names = ["SetVariable", "sv"]

    def _run(self, data, cfg):
        return {cfg.alias: cfg.parameters["value"]}


