import sys
from time import sleep
import mTest
from mTest import Hide, GoTo
from pyMusk import Data

log = Data.logger

class Common_Setup(mTest.TestCase):

    def init(self, test_args):

        log.info(__name__, "Test Log")
        log.info(__name__, "Test Log")
        sleep(2)
        if False:
            GoTo('Common_Cleanup')

        return True

    def setup(self, test_args):

        log.info("This is sample test log. test_args {}".format(test_args))
        Data.args['Hello'] = 'Some Data'

        return True

    @Hide(True)
    def Hidden_Func(self, test_args):

        print("This is Hidden Func")
        return True

class My_Test(mTest.TestCase):

    def my_test(self, test_args):

        log.info(__name__, "my_test")
        log.info("my_test 2")
        log.info("This is sample Info log. test_args {}".format(test_args))
        log.warning("This is sample Warning log. test_args {}".format(test_args))
        log.error("This is sample Error log. test_args {}".format(test_args))
        for i in range(100):
            log.info("This is sample info log: {}".format(i), __name__, To_Screen = False)
        return True

    def my_failed_test(self, test_args):

        log.error(__name__, "This is sample Error log. This is sample Error log. This is sample Error log. This is sample Error log. This is sample Error log. This is sample Error log. This is sample Error log. This is sample Error log. This is sample Error log. This is sample Error log ")
        return False

class My_Test_2(mTest.TestCase):

    def my_test(self, test_args):

        log.info("my_test 3.1. Data.args: {}".format(Data.args))
        log.info("my_test 3.2. test_args {}".format(test_args))

        return True
        
class Common_Cleanup(mTest.TestCase):

    def init(self, test_args):

        log.info(__name__, "Cleanup")
        return True

class Dont_Call:

    def __init__(self, test_args):

        print ("How come, I executed?")
        return True
       
@Hide(True)
class hide_me(mTest.TestCase):

    def __init__(self, test_args):

        print ("Hide me please!!!")
        return True

