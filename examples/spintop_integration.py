import os

from spintop_openhtf import TestPlan

from openhtf.plugs.user_input import UserInput

""" Test Plan """

plan = TestPlan('examples.hello_world')

@plan.testcase('Hello-World')
@plan.plug(prompts=UserInput)
def hello_world(test, prompts):
    """Says Hello World!"""
    test.logger.info('Hello World')

def create_spintop_callback():
    from spintop import Spintop
    from spintop.persistence.mongo import MongoPersistenceFacade
    from spintop_openhtf.transforms.openhtf_fmt import OpenHTFTestRecordTransformer
    
    # Cloud connection. Need to login using python -m spintop.cli login
    # spintop_client = Spintop()
    # facade = spintop_client.spinhub.tests
    
    # Local DB connection
    facade = MongoPersistenceFacade.from_mongo_uri('mongodb://localhost', database_name='main-data')
    
    transformer = OpenHTFTestRecordTransformer()
    
    def callback(htf_record):
        facade.create([transformer(htf_record)])
        
    return callback

if __name__ == '__main__':
    plan.add_callbacks(create_spintop_callback())
    plan.run()




