"""
Module collect is a script to collect test cases for before/after states.

Usage:
    ```sh
    TEST_NAME=example
    poetry run collect --test-name $TEST_NAME --utils cAdvisor,ftw,locust
    ```
"""
import argparse
import os
import time
import subprocess
import shutil
from typing import List
import docker
from ping3 import ping
from src.model import CollectCommandArg, UtilMapper
from src.type import State, UtilType
from src.utils import logger


class _ChangedRule:
    """
    _ChangedRule represents a changed rule identified from comparing before/after states.
    @TODO: impl id
    """
    req: str

    def __init__(self, req: str):
        self.req = req

def get_test_command_arg() -> CollectCommandArg:
    """
    get test command arg from STDIN

    Returns:
        CollectCommandArg: collect command arg
    """
    parser = argparse.ArgumentParser(description='Collect Command Parser')
    parser.add_argument('--test-name', type=str, help='test name', required=True)
    parser.add_argument('--utils', type=str, help='utils')
    parser.add_argument('--before', type=str, help='before test command')
    parser.add_argument('--after', type=str, help='after test command')
    parser.add_argument('--raw-output', type=str, help='raw output')
    parser.add_argument('--output', type=str, help='output')
    parser.add_argument('--waf-endpoint', type=str, help='waf endpoint')
    parser.add_argument('--mode', type=str, help='mode')

    parsed_args = parser.parse_args()

    return CollectCommandArg(
        test_name=parsed_args.test_name,
        before=parsed_args.before,
        after=parsed_args.after,
        utils=None if parsed_args.utils is None else parsed_args.utils.split(","),
        raw_output=parsed_args.raw_output,
        output=parsed_args.output,
        waf_endpoint=parsed_args.waf_endpoint,
        mode=parsed_args.mode
    )

def init(arg: CollectCommandArg):
    """
    initialize corresponding directory, service, etc.

    Args:
        arg (CollectCommandArg): collect command arg
    """

    # create folder for raw_output
    os.makedirs(arg.raw_output, exist_ok=True)

    # create folder for output
    os.makedirs(arg.output, exist_ok=True)

    # create folder for tmp
    os.makedirs(arg.tmp_dir, exist_ok=True)

    # create folder for test case
    os.makedirs(arg.before_rules_dir, exist_ok=True)
    os.makedirs(arg.after_rules_dir, exist_ok=True)
    os.makedirs(arg.test_cases_dir, exist_ok=True)

def get_changed_rules(arg: CollectCommandArg) -> List[_ChangedRule]:
    """
    get changed rules from git diff between before/after states.

    Args:
        arg (CollectCommandArg): collect command arg

    Returns:
        List[_ChangedRule]: a list of changed rules
    """
    exec_cmd = f"git diff --name-only {arg.before} {arg.after} | grep -E \'rules/.*.conf$\'"

    out = subprocess.run(exec_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)

    if out.returncode != 0:
        logger.info("No rule is changed")
        exit(0)

    output = subprocess.check_output(exec_cmd, shell=True).decode()

    changed_rules: List[_ChangedRule] = []

    for line in output.splitlines():
        logger.info(f"Changed rule: {line}")
        changed_rules.append(_ChangedRule(line.replace("rules/", "").replace(".conf", "")))

    return changed_rules

def init_tmp_file(arg: CollectCommandArg, changed_rules: List[_ChangedRule]):
    """
    init tmp file for testing. Including copying before/after rules and test cases.

    Args:
        arg (CollectCommandArg): collect command arg
        changed_rules (List[_ChangedRule]): a list of changed rules
    """

    # copy before-rules
    for changed_rule in changed_rules:
        cmd = f"git show {arg.before}:rules/{changed_rule.req}.conf > {arg.before_rules_dir}/{changed_rule.req}.conf"
        subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # copy after-rules
    for changed_rule in changed_rules:
        cmd: str

        if arg.after.startswith("--"):
            cmd = f"cp {arg.after}/rules/{changed_rule.req}.conf {arg.after_rules_dir}/{changed_rule.req}.conf"
        else:
            cmd = f"git show {arg.after}:rules/{changed_rule.req}.conf > {arg.after_rules_dir}/{changed_rule.req}.conf"

        subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.check_output(cmd, shell=True).decode()

    # copy regression files for changed_rules to tmp folder
    for changed_rule in changed_rules:
        try:
            shutil.copytree(f"./tests/regression/tests/{changed_rule.req}/", f"{arg.test_cases_dir}/{changed_rule.req}/")
        except OSError as e:
            logger.warning(f"Test case for {changed_rule.req} does not have test case")

def init_docker_compose_file(arg: CollectCommandArg, state: State):
    """
    init before/after docker-compose file.
    
    Args:
        arg (CollectCommandArg): collect command arg
        state (State): state
    """

    shutil.copyfile("./tests/docker-compose.yml", f"./tests/docker-compose-{state.value}.yml")
    processed_path = (arg.before_rules_dir if state == State.BEFORE.value else arg.after_rules_dir).replace("/", "\\/")
    cmd = f"""sed -i -e "s/- ..\\/rules/- ..\\/{processed_path}/g" .\\/tests\\/docker-compose-{state.value}.yml"""
    subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # @TODO: this is a temporary fix for extra files created from sed
    try:
        os.remove(f"./tests/docker-compose-{state.value}.yml-e")
    except OSError:
        pass

def runner(args: CollectCommandArg, state: State):
    """
    run test cases for before/after states.
    
    Args:
        args (CollectCommandArg): collect command arg
        state (State): state
    """

    # start service with docker-compose
    cmd = f"docker-compose -f ./tests/docker-compose-{state.value}.yml up -d {args.modsec_version}"

    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, capture_output=False)

    # check it's up and running
    if not waf_server_is_up(args.waf_endpoint):
        logger.critical("WAF server is not up")
        exit(1)

    # run test cases
    for util in args.utils:
        logger.info(f"Running Test case: {args.test_name} using {util}, State = {state.value}")
        # @TODO: temp fix
        UtilMapper.get(UtilType(UtilType[util.upper()]))().collect(args, state)

    # stop service with docker-compose
    cmd = f"""
    docker-compose -f ./tests/docker-compose-{state.value}.yml stop &&
    docker-compose -f ./tests/docker-compose-{state.value}.yml down
    """
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, capture_output=False)

def waf_server_is_up(waf_endpoint: str) -> bool:
    """
    check if waf server is up

    Args:
        waf_endpoint (str): waf endpoint

    Returns:
        bool: True if waf server is up, False otherwise
    """
    timeout, retry = 5, 0

    while retry < 3:
        if docker.from_env().api.inspect_container("modsec2-apache")["State"]["Status"] == 'running':
            return True
        retry += 1
        time.sleep(timeout)

    retry = 0

    while retry < 3:
        result = ping(waf_endpoint, timeout=timeout)
        if result is None or not result:
            retry += 1
            time.sleep(timeout)
            continue
        else:
            return True

    return False

def main():
    """
    script entrypoint of collect.py
    """

    # check the inputs
    args = get_test_command_arg()

    # create folder
    init(args)

    # get corresponding test files
    changed_rules = get_changed_rules(args)

    # if there's no changed rule, exit
    if len(changed_rules) == 0:
        logger.info("No rule is changed")
        exit(0)

    # init temp file for testing
    init_tmp_file(args, changed_rules)

    init_docker_compose_file(args, State.BEFORE)
    runner(args, State.BEFORE)

    init_docker_compose_file(args, State.AFTER)
    runner(args, State.AFTER)
