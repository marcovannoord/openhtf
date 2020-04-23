
.. _forms-label:

## Using Custom Forms

### Introduction

Customizable forms allows spintop-openhtf developers to include complex form inputs in their test plans in order to interact with the test operators using simple dictionnary definitions. For example, the following form shows an input field, allowing the tester to enter the measured impedance.

```python
FORM_LAYOUT = {
    'schema':{
        'title': "Impedance",
        'type': "object",
        'required': ["impedance"],
        'properties': {
            'impedance': {
                'type': "string", 
                'title': "Measure Impedance on test point X\nEnter value in Ohms"
            },
        }
    },
    'layout':[
        "impedance"
    ]
}
	
```

When executed the above form entry will result in the following being displayed on the web interface.

![Normal Form](img/normal-form.png)


This `FORM_LAYOUT` variable contains two top level attributes which are essential to differentiate: `schema` and `layout`. The schema defines the fields while layout defines the ordering and display of these fields.

### JSON Schema Forms

The schema part is actually a generic JSON schema vocabulary used to validate JSON documents named [*JSON Schema*](https://json-schema.org/).

As quoted from their homepage, 
> JSON Schema is a vocabulary that allows you to annotate and validate JSON documents.

#### Example Schema

The format allows you to build the schema of complex JSON structures and afterward validate that a certain JSON document respects or not that structure. Let's take the schema part of our previous example:

```json
{
    'title': "Impedance",
    'type': "object",
    'required': ["impedance"],
    'properties': {
        'impedance': {
            'type': "string", 
            'title': "Measure Impedance on test point X\nEnter value in Ohms"
        },
    }
}
```

In order, this defines that:

- `"title": "Impedance"`: The title of this form is 'Impedance'.
- `"type": "object"`: The type of the top level JSON object is object, which means that it contains other properties.
- `"required": ["impedance]`: The property named ``impedance` is required. 
- `"properties": {`: Begins the list of properties in this object. Note that these are *unordered*.
- `"impedance": { "type": "string",  "title": "Measure Impedance on test point X\nEnter value in Ohms"     }`

    The property named `impedance` is a string with as label the instructions passed to the operator : 'Measure Impedance on test point X\nEnter value in Ohms'

- And so on.

.. note::
    Of all the keys shown here, only `required` is specific to JSON Schema *Forms*. The rest is part of the JSON Schema format. You can use the following playground to experiment with the forms: `JSON Schema Form <https://gcanti.github.io/resources/json-schema-to-tcomb/playground/playground.html>`_. However, the renderer is not the same that spintop-openhtf internally uses and therefore results may vary. You can use the getting started example in the spintop-openhtf repo for a quick demo with forms.

To add the custom form to the test bench defined previously in the :ref:`first-testbench-label` tutorial, first insert the FORM_LAYOUT definition at the top of the main.py file, then modify the test case definition to use the new custom form prompts as shown below.

```python
@plan.testcase('Hello-Test')
@plan.plug(prompts=UserInput)
def hello_world(test, prompts):
    """Displays the custom from defined above"""
    prompts.prompt_form(FORM_LAYOUT)
```

Run the testbench again to see the new form appear.

:download:`Tutorial source <../tutorials/main_custom_form.py>`

