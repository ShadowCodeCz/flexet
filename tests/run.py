import flexet
import pprint


data = {}
fn = flexet.build_by_cfg("run_net.json")
r = fn.run(data)
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(r)
