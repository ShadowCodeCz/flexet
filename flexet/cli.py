import os
import json


#
# class DefaultDirectory:
#     @staticmethod
#     def package():
#         return os.path.abspath(os.path.dirname(__file__))
#
#     @staticmethod
#     def plugin():
#         return os.path.join(DefaultDirectory.package(), "node_plugin")
#

def generate_initial_cfg():
    empty_cfg = {
        "collectors": [
            {
                "type": "plugin.re",
                "directories": [],
                "template": [r".+\.py$"]
            },
            {
                "type": "pf.json",
                "directories": [],
                "templates": []
            }
        ],

        "layers": ["ALIAS@NODE-PLUGIN:PARAMETRIC-FILE/PARAMETER_1=VALUE;PARAMETER_2=VALUE"]
    }

    with open('net.flexet.json', 'w') as outfile:
        json.dump(empty_cfg, outfile)
