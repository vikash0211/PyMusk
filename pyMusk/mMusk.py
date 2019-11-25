"""
Framework Start.py
Takes the test cases names and test file to trigger the test.
"""

import importlib
import datetime
import os
import sys
import re
from pyMusk import mTest
from pyMusk.mTest import get_duration
from pyMusk.mLogging import logging
import getpass

mTestDict = {}
mTestDict["config"] = None
mTestDict["job"] = {}
mTestDict["job"]["user"] = getpass.getuser()

class mTask:

    def __init__(self):
        global mTestDict
        mTestDict["log"] = None
        mTestDict["goto"] = None
        mTestDict["job"]["taskCount"] = 0
        mTestDict["job"]["testCount"] = 0
        mTestDict["job"]["passCount"] = 0
        mTestDict["job"]["failCount"] = 0
        mTestDict["job"]["otherCount"] = 0
        mTestDict["job"]["startTime"] = datetime.datetime.now()
        mTestDict["job"]["endTime"] = None

    @classmethod
    def run(cls, scriptpath, test_list=(), args={}):

        taskStartAt = datetime.datetime.now()
        path = os.path.split(scriptpath)[0]
        script = os.path.split(scriptpath)[-1]

        # Read test data
        global mTestDict
        mTestDict["test_args"] = args

        if not mTestDict["config"]:
            raise Exception("ConfigData not specified in Job File")

        log = mTestDict.get("log", None)
        if not log:
            if 'logs_dir' not in dir(mTestDict["config"]):
                raise Exception("logs_dir not specified in config File")

            log = logging(mTestDict["config"].logs_dir)
            mTestDict["log"] = log


        # Add Task run tag to logs
        timeStamp = (str(taskStartAt))[:-7]
        mTestDict["job"]["taskCount"] += 1
        log.fh.write("<Start Task %s %s>\n"%(mTestDict["job"]["taskCount"], timeStamp))
        log.fh.flush()

        # Extract module to be Imported
        module = ""
        for syspath in sys.path:
            syspath = repr(syspath)[1:-1]
            pattern = r"%s(.+)"%syspath
            matest_listh = re.search(pattern, scriptpath)
            if matest_listh:
                module = matest_listh.group(1)
                break

        if not module:
            if path not in sys.path:
                sys.path.append(path)
                module = script.split(".")[0]

        module = module.replace("\\", ".")
        module = module.replace("/", ".")
        module = ".".join(module.split(".")[:-1]) if ".py" in module else module
        module = module[1:] if module.startswith(".") else module
        print ("module: ", module)

        # Import test script
        object = importlib.import_module(module)
        object = importlib.reload(object)   #Reload required in case test is rerun

        # Extract test cases list from test script
        if not test_list:
            test_list = [k for k in object.__dict__ if ("class" in str(object.__dict__[k]) and module in str(object.__dict__[k]))]

        test_list = [k for k in test_list if issubclass(object.__dict__[k], mTest.TestCase)]
        print(test_list)

        taskResult = "PASS"
        for test in test_list:
            testResult = "PASS"
            testStartAt = datetime.datetime.now()

            # Add Test tag to logs
            log.fh.write("<Start Test %s>\n"%test)
            log.fh.flush()

            test_class = object.__dict__[test]

            # Get functions from test class
            test_defs = [test_class.__dict__[k] for k in test_class.__dict__ if ("__" not in k and "function" in str(type(test_class.__dict__[k])))]
            #print(test_defs)

            # Create object of test class
            test_obj = test_class()

            # Execute Functions
            for func in test_defs:
                subtestStartAt = datetime.datetime.now()
                # Add SubTest tag to logs
                log.fh.write("<Start Subtest %s>\n"%func.__name__)
                log.fh.flush()

                # Run Function
                if (not mTestDict["goto"]) or (mTestDict["goto"] == test):
                    """
                    res = False
                    try:
                        res = func(test_obj)
                    except Exception as e:
                        log.error(__name__, e)
                    """
                    res = func(test_obj)
                    if not res:
                        testResult = False
                    if not testResult:
                        taskResult = False

                    res = "PASS" if res else "FAIL"
                else:
                    res = "BLOCKED"
                    testResult = "BLOCKED" if testResult else testResult
                    taskResult = "BLOCKED" if taskResult else taskResult

                subtestEndAt = datetime.datetime.now()
                subtestDuration = get_duration(subtestStartAt, subtestEndAt)

                log.fh.write("Result: %s\n"%res)
                log.fh.write("<End Subtest %s %s %s>\n"%(func.__name__, res, subtestDuration))
                log.fh.flush()

            testEndAt = datetime.datetime.now()
            testDuration = get_duration(testStartAt, testEndAt)
            mTestDict["job"]["testCount"] += 1
            if not testResult:
                mTestDict["job"]["failCount"] += 1
                testResult = "FAIL"
            elif testResult == "BLOCKED":
                mTestDict["job"]["otherCount"] += 1
            else:
                mTestDict["job"]["passCount"] += 1
                testResult = "PASS"

            log.fh.write("<End Test %s %s %s>\n"%(test, testResult, testDuration))
            log.fh.flush()

        taskEndAt = datetime.datetime.now()
        mTestDict["job"]["endTime"] = taskEndAt
        taskDuration = get_duration(taskStartAt, taskEndAt)
        if not taskResult:
            taskResult = "FAIL"
        elif taskResult == "BLOCKED":
            pass
        else:
            taskResult = "PASS"
        log.fh.write("<End Task %s %s %s>\n"%(mTestDict["job"]["taskCount"], taskResult, taskDuration))
        log.fh.flush()


