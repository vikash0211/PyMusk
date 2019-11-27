#import basic_test as test
import os
import sys

importPath = []
importPath.append('./lib') # Path to pyMusk Framework Directory
for path in importPath:
    if path not in sys.path:
        sys.path.append(path)

from pyMusk import Task
from pyMusk import Data
from mLogging import getReport

testPath = os.path.dirname(os.path.abspath(__file__))
testScript = os.path.join(testPath, 'sample_test.py')
Data.job_dict["file"] = __file__


def main():
    testDict = {'a': 111}
    task = Task()
    #task.set_sender('vikash0211@gmail.com')
    #task.set_receipients('vikash0211@gmail.com')

    # Run Test
    task.run(testScript, name = 'Sample Test 1', test_list = ("Common_Setup", "My_Test", "Common_Cleanup"), test_args = {'1': 1})
    task.run(testScript, name = 'Sample Test 2', test_list = ("My_Test_2", "Common_Cleanup"), test_args = testDict)

    #Get Test Report in mail
    getReport()


if __name__ == '__main__':
    main()


