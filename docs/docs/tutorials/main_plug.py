# main.py
import os

import openhtf as htf
from spintop_openhtf import TestPlan

from openhtf.plugs import BasePlug

""" Plug Definition """

class FileCopier(BasePlug):
    def copy_file(self, source_file, destination_folder):
        shutil.copy(source_file, destination_folder)


""" Test Plan """

# This defines the name of the testbench.
plan = TestPlan('File Copy Test Bench')

@plan.testcase('File Copy Test')
@plan.plug(copy_plug=FileCopier) 
def file_copy_test(test, copy_plug): 
    copy_plug.copy_file(source, destination)
   
    
if __name__ == '__main__':
    plan.no_trigger()
    plan.run()