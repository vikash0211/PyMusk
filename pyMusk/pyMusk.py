'''
Framework mMusk.py
Takes the test cases names and test file to trigger the test.
'''

import importlib
import datetime
import os
import sys
import traceback
import time
import re
import yaml
import mTest
from mTest import get_duration
from mLogging import logging

config_file = 'config.yaml'

class Data:

    path = os.path.dirname(os.path.abspath(__file__))
    config = None
    job_dict = {}
    logger = None
    goto = None
    args = {}

class Task:

    def __init__(self):

        Data.logger = None
        Data.goto = None
        Data.job_dict['user'] = os.getlogin()
        Data.job_dict['taskCount'] = 0
        Data.job_dict['testCount'] = 0
        Data.job_dict['passCount'] = 0
        Data.job_dict['failCount'] = 0
        Data.job_dict['otherCount'] = 0
        Data.job_dict['startTime'] = datetime.datetime.now()
        Data.job_dict['endTime'] = None
        with open(os.path.join(Data.path, config_file), 'r') as fh:
            Data.config = yaml.safe_load(fh)

        if not Data.config:
            raise Exception('ConfigData not specified in Job File')

        Data.config['sender_email'] = '{}@{}'.format(os.getlogin(), Data.config['smtp']['domain'])
        Data.config['receipients'] = [Data.config['sender_email']]

    def set_sender(self, email):

        Data.config['sender_email'] = email

    def set_receipients(self, emails):

        if type(emails) == str:
            emails = [emails]

        if type(emails) != list:
            raise Exception('list or string allowed for receipients')

        Data.config['receipients'] = emails

    @classmethod
    def run(cls, scriptpath, test_list=(), test_args = {}, name = ''):

        taskStartAt = datetime.datetime.now()
        path = os.path.split(scriptpath)[0]
        script = os.path.split(scriptpath)[-1]

        if not Data.logger:
            Data.logger = logging(Data.config['logs_dir'])
        log = Data.logger

        # Add Task run tag to logs
        timeStamp = (str(taskStartAt))[:-7]
        Data.job_dict['taskCount'] += 1
        log.fh.write('<Start Task id=%s name=%s time=%s>\n'%(Data.job_dict['taskCount'], name, timeStamp))
        log.fh.flush()

        # Extract module to be Imported
        module = ''
        for syspath in sys.path:
            syspath = repr(syspath)[1:-1]
            pattern = r'%s(.+)'%syspath
            matest_listh = re.search(pattern, scriptpath)
            if matest_listh:
                module = matest_listh.group(1)
                break

        if not module:
            if path not in sys.path:
                sys.path.append(path)
                module = script.split('.')[0]

        module = module.replace('\\', '.')
        module = module.replace('/', '.')
        module = '.'.join(module.split('.')[:-1]) if '.py' in module else module
        module = module[1:] if module.startswith('.') else module
        print ('module: ', module)

        # Import test script
        object = importlib.import_module(module)
        if sys.version_info[0] == 3:
            object = importlib.reload(object)   #Reload required in case test is rerun, Not available in Python 2.7

        # Extract test cases list from test script
        if not test_list:
            if sys.version_info[0] < 3:
                test_dict = {k:v for k,v in object.__dict__.items() if ('classobj' in str(type(object.__dict__[k])) and '%s.%s'%(module, k) in str(object.__dict__[k]))}
                test_list = sorted(test_dict.items(), key = lambda x:id(x[1]))
                test_list = [k[0] for k in test_list]
            else:
                test_list = [k for k in object.__dict__ if ("class" in str(object.__dict__[k]) and module in str(object.__dict__[k]))]

        test_list = [k for k in test_list if issubclass(object.__dict__[k], mTest.TestCase)]
        print(test_list)

        taskResult = 'PASS'
        for test in test_list:
            testResult = 'PASS'
            testStartAt = datetime.datetime.now()

            # Add Test tag to logs
            print('<Start Test name=%s>\n'%test)
            log.fh.write('<Start Test name=%s>\n'%test)
            log.fh.flush()

            test_class = object.__dict__[test]

            # Get functions from test class
            test_defs = [test_class.__dict__[k] for k in test_class.__dict__ if ('__' not in k and 'function' in str(type(test_class.__dict__[k])))]
            if sys.version_info[0] < 3:
                test_defs = sorted(test_defs, key = lambda x:id(x))

            # Create object of test class
            test_obj = test_class()

            # Execute Functions
            for func in test_defs:
                subtestStartAt = datetime.datetime.now()
                # Add SubTest tag to logs
                print('<Start Subtest name=%s>\n'%func.__name__)
                log.fh.write('<Start Subtest name=%s>\n'%func.__name__)
                log.fh.flush()

                # Run Function
                if (not Data.goto) or (Data.goto == test):

                    res = None
                    try:
                        res = func(test_obj, test_args)
                    except Exception as e:
                        log.fh.write('ERROR: Exception: %s\n'%e)
                        print('ERROR: Exception: %s'%e)
                        traceback.print_exc(file = log.fh)
                        traceback.print_exc(file = sys.stdout)
                        log.fh.flush()
                    except KeyboardInterrupt:
                        log.fh.write('ERROR: KeyboardInterrupt\n')
                        print('ERROR: KeyboardInterrupt')
                        log.fh.flush()

                    if res == None:
                        log.fh.write('ERROR: No return value from Test case, Probably Exception in Test Case\n')
                        print('ERROR: No return value from Test case, Probably Exception in Test Case')
                        log.fh.flush()
                    
                    if not res:
                        testResult = False
                    if not testResult:
                        taskResult = False

                    res = 'PASS' if res else 'FAIL'
                else:
                    res = 'BLOCKED'
                    testResult = 'BLOCKED' if testResult else testResult
                    taskResult = 'BLOCKED' if taskResult else taskResult

                subtestEndAt = datetime.datetime.now()
                subtestDuration = get_duration(subtestStartAt, subtestEndAt)

                log.fh.write('Result: %s\n'%res)
                log.fh.write('<End Subtest name=%s result=%s runtime=%s>\n'%(func.__name__, res, subtestDuration))
                print('<End Subtest name=%s result=%s runtime=%s>\n'%(func.__name__, res, subtestDuration))
                log.fh.flush()

            testEndAt = datetime.datetime.now()
            testDuration = get_duration(testStartAt, testEndAt)
            Data.job_dict['testCount'] += 1
            if not testResult:
                Data.job_dict['failCount'] += 1
                testResult = 'FAIL'
            elif testResult == 'BLOCKED':
                Data.job_dict['otherCount'] += 1
            else:
                Data.job_dict['passCount'] += 1
                testResult = 'PASS'

            log.fh.write('<End Test name=%s result=%s runtime=%s>\n'%(test, testResult, testDuration))
            print('<End Test name=%s result=%s runtime=%s>\n'%(test, testResult, testDuration))
            log.fh.flush()

        taskEndAt = datetime.datetime.now()
        Data.job_dict['endTime'] = taskEndAt
        taskDuration = get_duration(taskStartAt, taskEndAt)
        if not taskResult:
            taskResult = 'FAIL'
        elif taskResult == 'BLOCKED':
            pass
        else:
            taskResult = 'PASS'
        log.fh.write('<End Task id=%s result=%s runtime=%s>\n'%(Data.job_dict['taskCount'], taskResult, taskDuration))
        print('<End Task id=%s result=%s runtime=%s>\n'%(Data.job_dict['taskCount'], taskResult, taskDuration))
        log.fh.flush()

