class CollectorConfiguration:
    def __init__(self):
        self.type = ""


class FileCollectorConfiguration(CollectorConfiguration):
    def __init__(self):
        super().__init__()
        self.directories = []
        self.templates = []


class SubclassCollectorConfiguration(CollectorConfiguration):
    def __init__(self):
        super().__init__()
        self.classes = None


class NetConfiguration:
    def __init__(self):
        self.plugin_collectors = []
        self.parametric_file_collectors = []
        self.layers = []


class NodeRawConfiguration:
    def __init__(self):
        self.alias = None
        self.plugin_name = None
        self.parametric_file = None
        self.inline_parameters = {}


class NodeConfiguration:
    def __init__(self):
        self.alias = None
        self.plugin = None
        self.parameters = None
