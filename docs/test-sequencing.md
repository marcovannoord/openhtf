# Test Sequencing

OpenHTF and Spintop-OpenHTF offers constructs to sequence test cases and control the execution flow. 

## Phase Outcomes

### PhaseOutcome: Test Phase Outcome

The outcome of a test phase can be one of the following values, which is determined by the PhaseResult described below:

- **PhaseOutcome.PASS**: The phase result was CONTINUE and all measurements validators passed.
- **PhaseOutcome.FAIL**:  The phase result was CONTINUE and one or more measurements outcome failed, or the phase result was FAIL_AND_CONTINUE or STOP.
- **PhaseOutcome.SKIP**:  The phase result was SKIP or REPEAT.
- **PhaseOutcome.ERROR**:  An uncatched exception was raised, and that exception is not part of the `failure_exceptions` list. The test will stop in such a case.

Although you should not need to import this enum for test sequencing, you can import it using `from openhtf.core.test_record import PhaseOutcome`. Usage would be to analyze results.

### PhaseResult: Test Phase Flow Control

The result of a test phase is controlled by the value it returns. It can return None (or no return statement) for the standard CONTINUE. If an uncatched exception occurs during the test, the phase will be marked as ERROR. OpenHTF will infer the outcome based on the test phase result.

- **PhaseResult.CONTINUE**:Causes the framework to process the phase measurement outcomes and execute  the next phase.
- **PhaseResult.FAIL_AND_CONTINUE**: Causes the framework to mark the phase with a fail outcome and execute the next phase.
- **PhaseResult.REPEAT**: Causes the framework to execute the same phase again, ignoring the measurement outcomes for this instance. 
    If returned more than the phase's `repeat_limit` option, this will be treated as a STOP.
- **PhaseResult.SKIP**: Causes the framework to ignore the measurement outcomes and execute the next phase.
- **PhaseResult.STOP**: Causes the framework to stop executing, indicating a failure. The next phases will not be executed.

You can import this enum using `from openhtf import PhaseResult`.

!!! note
    To identify certain exceptions as FAIL instead of errors, you can add failure exceptions to the test plan:

    ```python
    
    test_plan = TestPlan()
    test_plan.failure_exceptions += (Exception,)

    @test_plan.testcase('test1')
    def my_test(test):
        raise Exception('!!') # Will mark phase as FAIL instead of ERROR.
    
    ```

#### Example

Let's say you wish to mark a phase as fail but to continue executing the test. You simply need to return the FAIL_AND_CONTINUE phase result:

```python

from openhtf import PhaseResult

test_plan = TestPlan()

@test_plan.testcase('test1')
def my_test(test):
    # (do stuff)
    return PhaseResult.FAIL_AND_CONTINUE

```


## Phase Groups

Phase groups allow to add setup and teardown functions around the test phases. A phase group is a phase in itself, which means that they can be infinitely nested. 

### Setup and Teardown

Setups and teardown functions can be added to a test sequence using the `setup` and `teardown` decorators.

!!! example

    ```python
    plan = TestPlan()
    @plan.teardown('teardown')
    def teardown(test):
        # (teardown stuff)
    ```

#### Setup

A setup function is very similar to a normal test phase except that it's outcome can skip entirely the group it is part of, *including the teardown*. If the setup phase 

### Test Nesting Example

To illustrate how a test can be gradually nested, let's use an incrementally built simple example:

#### (1) One test case

```python
plan = TestPlan()

@plan.testcase('test1')
def test1(test):
    test.logger.info('test1')
```

!!! result
    - `plan`
        - `test1`

#### (2) + An empty sub group

```python
sub_group = plan.sub_sequence('sub-group')

```

!!! result
    - `plan`
        - `test1`
        - `sub-group`, an empty phase group

#### (3) + Sub setup, test case and teardown

```python
@sub_group.setup('sub setup')
def sub_setup(test):
    """Says Sub setup."""
    test.logger.info('Sub setup')

@sub_group.testcase('sub Hello')
def sub_hello(test):
    """Says Sub hello."""
    test.logger.info('Sub hello')

@sub_group.teardown('sub cleanup')
def sub_cleanup(test):
    """Says Sub cleanup."""
    test.logger.info('Sub cleanup')
```


!!! result
    - `plan`
        - `test1`
        - `sub-group`
            - `sub_setup` (setup)
            - `sub_hello`
            - `sub_cleanup` (teardown)

#### (4) + Final teardown

```python
@plan.teardown('cleanup')
def cleanup(test):
    """Says Cleaned up."""
    test.logger.info('Cleaned up.')
```

!!! result
    - `plan`
        - `test1`
        - `sub-group`
            - `sub_setup` (setup)
            - `sub_hello`
            - `sub_cleanup` (teardown)
        - `cleanup` (teardown)

#### Outcome Table

|First noticeable result|test1|sub_setup|sub_hello|sub_cleanup|cleanup
|---|---|---|---|---|---|
|test1: STOP|FAIL|-|-|-|PASS|
|sub_setup: STOP|PASS|FAIL|-|-|PASS|
|sub_hello: STOP|PASS|PASS|FAIL|PASS|PASS|

Things to note:

- Teardown is always executed as soon as one the group test phases is executed. If `test1` is executed, `cleanup` will be. If `sub_hello` is executed, `sub_cleanup` will be.
- Setup failure cancels the execution of the group, including the teardown.
