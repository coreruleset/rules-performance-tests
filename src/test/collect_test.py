import sys
from pathlib import Path
from typing import List
from src.collect import *
from src.type import Mode


GLOBAL_ARGS: CollectCommandArg = CollectCommandArg(
    test_name="mock_test",
    before=None,
    after=None,
    utils=[],
    raw_output="./unittest/raw",
    output="./unittest/output",
    waf_endpoint=None,
    mode=Mode.CLI
)

class _TestCollectCommandArg:
    input: List[str]
    expect_res: CollectCommandArg
    test_name: str
    
    def __init__(self, input: List[str], expect_res: CollectCommandArg, test_name: str):
        self.input = input
        self.expect_res = expect_res
        self.test_name = test_name

def test_get_test_command_arg():
    testcases: List[_TestCollectCommandArg] = [
        _TestCollectCommandArg(
            input=[
                '--test-name', 'mock test',
                '--utils', 'ftw,locust',
                '--before', 'abcdef',
                '--after', '123456',
                '--raw-output', './raw-output',
                '--output', './output',
                '--waf-endpoint', 'waf-endpoint'
            ],
            expect_res=CollectCommandArg(
                test_name='mock test',
                utils=['ftw', 'locust'],
                raw_output='./raw-output',
                output='./output',
                before='abcdef',
                after='123456',
                waf_endpoint='waf-endpoint',
                mode=Mode.CLI
            ),
            test_name='all args should be parsed'
        ),
        # _TestCollectCommandArg(
        #     input=["--test-name", "test-2"],
        #     expect_res=CollectCommandArg("test-2", None, None, None, None, None, None),
        #     test_name="optional args should apply default value"
        # ),
    ]
    
    for testcase in testcases:
        for i in testcase.input:
            sys.argv.append(i)

        args = get_test_command_arg()
        assert args.test_name == testcase.expect_res.test_name, testcase.test_name
        assert args.utils == testcase.expect_res.utils, testcase.test_name
        assert args.raw_output == testcase.expect_res.raw_output, testcase.test_name
        assert args.output == testcase.expect_res.output, testcase.test_name
        assert args.before == testcase.expect_res.before, testcase.test_name
        assert args.after == testcase.expect_res.after, testcase.test_name
        assert args.waf_endpoint == testcase.expect_res.waf_endpoint, testcase.test_name
        sys.argv.clear()

def test_name_is_mandatory():
    pass

def test_init():
    init(GLOBAL_ARGS)
    assert Path(GLOBAL_ARGS.raw_output).exists(), "raw_output folder should be created"
    assert Path(GLOBAL_ARGS.output).exists(), "output folder should be created"
    assert Path(GLOBAL_ARGS.tmp_dir).exists(), "tmp folder should be created"
    assert Path(GLOBAL_ARGS.before_rules_dir).exists(), "before_rules_dir folder should be created"
    assert Path(GLOBAL_ARGS.after_rules_dir).exists(), "after_rules_dir folder should be created"
    assert Path(GLOBAL_ARGS.test_cases_dir).exists(), "test_cases_dir folder should be created"

def test_get_changed_rules():
    # modify a file, and check if diff can be found
    # restore the file, and rerun the function
    pass

def test_init_tmp_file():
    pass

def test_init_docker_compose_file():
    pass

def test_runner():
    pass

def test_waf_server_is_up():
    pass

# integration test for ftw
def test_ftw_util():
    pass

# integration test for cadvisor
def test_cAdvisor_util():
    pass

# integration test for locust
def test_locust_util():
    pass

def test_clean_up():
    pass
