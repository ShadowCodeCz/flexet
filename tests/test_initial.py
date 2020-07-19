import pytest
import flexet

# TODO: without inline paramert
# TODO: without cfg
# TODO: add two nets
# TODO: override parameter (parametric file, inline parameter)

# TODO: Error net json does not exists
# TODO: Error in net JSON: missing plugin_collector
# TODO: Error in net JSON: error in plugin collector definition
# TODO: Missing parametric collector
# TODO: Error in net JSON: error in parametric collector definition
# TODO: Error in net JSON: Missing layer
# TODO: Error in node cfg: without plugin
# TODO: Error in node cfg: missing plugin
# TODO: Error in node cfg: missing parametric file
# TODO: Error in node: raise exception


class TI:
    def __init__(self):
        self.id = None
        self.data = None
        self.cfg_path = None
        self.expected_result = None


tis = []
t1 = TI()

t1.id = "simple"
t1.data = {}
t1.cfg_path = "./tests/net_1.json"
t1.expected_result = {
    'AAA_in_content': True,
    'BBB_in_content': True,
    'aaa_in_content': False,
    'not_res_in_content': {'LLL': False, 'QQQ': False, 'TTT': True},
    'not_zzz_in_content': True,
    'res_in_content': {'LLL': True, 'QQQ': True, 'TTT': False},
    'test_content': 'AAA\nBBB\nCCC\n\nLLL\nQQQ\n\nWWW',
    'test_variable': 'ddd',
    'zzz_in_content': False
}

tis.append(t1)

ids = [ti.id for ti in tis]


@pytest.mark.parametrize("ti", tis, ids=ids)
def test_valid_input(ti):
    fn = flexet.build_by_cfg(ti.cfg_path)
    result = fn.run(ti.data)

    assert result == ti.expected_result


