
.. _test-case-label:

## Test Case Declaration

The different test cases are defined and declared one by one in in the test plan. Let's review the test case declared in the :ref:`first-testbench-label` tutorial.

The test case is declared as:

```python
@plan.testcase('Hello-Test')
@plan.plug(prompts=UserInput)
def hello_world(test, prompts):
    prompts.prompt('Hello Operator!')
    test.dut_id = 'hello' # Manually set the DUT Id to same value every test
```

spintop-openhtf uses the name "test phase" to refer to the different test cases in the test bench.




