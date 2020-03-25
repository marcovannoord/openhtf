# Custom Forms

## Introduction

Customizable forms allows spintop-openhtf developers to include complex form inputs to their tests using simple dictionnary definitions. For example, as shown in the [getting started](./getting-started.md) page, the following form shows two input fields, First Name and Last Name:

```python
FORM_LAYOUT = {
    'schema':{
        'title': "First and Last Name",
        'type': "object",
        'required': ["firstname", "lastname"],
        'properties': {
            'firstname': {
                'type': "string", 
                'title': "First Name"
            },
            'lastname': {
                'type': "string", 
                'title': "Last Name"
            },
        }
    },
    'layout':[
        "firstname",
        "lastname"
    ]
}
```

!!! summary "Output"
    ![Normal Form](img/normal-form.png)


This `FORM_LAYOUT` variable contains two top level attributes which are essential to differentiate: `schema` and `layout`. The schema defines the fields while layout defines the ordering and display of these fields.

## JSON Schema Forms

The schema part is actually a generic JSON schema vocabulary used to validate JSON documents named [*JSON Schema*](https://json-schema.org/).

As quoted from their homepage, 
> JSON Schema is a vocabulary that allows you to annotate and validate JSON documents.

### Example Schema

The format allows you to build the schema of complex JSON structures and afterward validate that a certain JSON document respects or not that structure. Let's take the schema part of our previous example:

```json
{
    "title": "First and Last Name",
    "type": "object",
    "required": ["firstname", "lastname"],
    "properties": {
        "firstname": {
            "type": "string", 
            "title": "First Name"
        },
        "lastname": {
            "type": "string", 
            "title": "Last Name"
        },
    }
}
```

In order, this defines that:

- `"title": "First and Last Name"`: The title of this form is 'First and Last Name'.
- `"type": "object"`: The type of the top level JSON object is object, which means that it contains other properties.
- `"required": ["firstname", "lastname"]`: The properties named `firstname` and `lastname` are required. 
- `"properties": {`: Begins the list of properties in this object. Note that these are *unordered*.
- 
    ```json
    "firstname": {
        "type": "string", 
        "title": "First Name"
    }
    ```
    The property named `firstname` is a string with label 'First Name'
- And so on.

!!! note
    Of all the keys shown here, only `required` is specific to JSON Schema *Forms*. The rest is part of the JSON Schema format. You can use the following playground to experiment with the forms: [JSON Schema Form](https://gcanti.github.io/resources/json-schema-to-tcomb/playground/playground.html). However, the renderer is not the same that spintop-openhtf internally uses and therefore results may vary. You can use the getting started example in the spintop-openhtf repo for a quick demo with forms.

### Example Data

The previous form would then successfully validate the following JSON Data:

```json
{
  "firstname": "foo",
  "lastname": "bar"
}
```

This is the dictionnary that is returned when you call `UserInput.prompt_form(...)`.


## Layout

The layout aspect of our previous example is specific to JSON Schema Forms, and, more specifically, [to the renderer we use.](https://github.com/json-schema-form/angular-schema-form/blob/master/docs/index.md#form-definitions)

### Select Choices (Dropdown)

If we re-use the previous form and wish to limit the values allowed for a specific string field, we can use the layout attribute to impose a select field.

In the following snippet, the simple `lastname` key is replaced by a complex object which identifies the field using the `"key": "lastname"` attribute. By adding the `"type": "select"` with the `titleMap`, we impose specific choices to the user.

This does not make much sense in the case of a last name, but we use the same example for consistency.

```python
FORM_LAYOUT = {
    'schema':{
        'title': "First and Last Name",
        'type': "object",
        'required': ["firstname", "lastname"],
        'properties': {
            'firstname': {
                'type': "string", 
                'title': "First Name"
            },
            'lastname': {
                'type': "string", 
                'title': "Last Name"
            },
        }
    },
    'layout':[
        "firstname",
        {
            "key": "lastname",
            "type": "select",
            "titleMap": [
                { "value": "Andersson", "name": "Andersson" },
                { "value": "Johansson", "name": "Johansson" },
                { "value": "other", "name": "Something else..."}
            ]
        }
    ]
}
```

!!! summary "Output"
    ![Select Form](img/select-form.png)


### Radio Buttons

Same example with lastname:

```python

FORM_LAYOUT = {
    'schema':{
        'title': "First and Last Name",
        'type': "object",
        'required': ["firstname", "lastname"],
        'properties': {
            'firstname': {
                'type': "string", 
                'title': "First Name"
            },
            'lastname': {
                'type': "string", 
                'title': "Last Name"
            },
        }
    },
    'layout':[
        "firstname",
        {
            "key": "lastname",
            "type": "radiobuttons",
            "titleMap": [
                { "value": "one", "name": "One" },
                { "value": "two", "name": "More..." }
            ]
        }
    ]
}

```

!!! summary "Output"
    ![Radiobuttons Form](img/radiobuttons-form.png)

### Text

Adding text within the form is very useful to guide or otherwise give more information to the user. This can be done using the `"type": "help"` layout.

!!! important "v0.5.5"
    The `markdown` function was added in spintop-openhtf version 0.5.5. It transforms the text into HTML, which is the only understood format of the helpvalue.


```python
from spintop_openhtf.util.markdown import markdown

FORM_LAYOUT = {
    'schema':{
        'title': "First and Last Name",
        'type': "object",
        'required': ["firstname", "lastname"],
        'properties': {
            'firstname': {
                'type': "string", 
                'title': "First Name"
            },
            'lastname': {
                'type': "string", 
                'title': "Last Name"
            },
        }
    },
    'layout':[
        "firstname",
        {
            "type": "help",
            "helpvalue": markdown("# Well Hello There!")
        },
        "lastname
    ]
}

```

!!! summary "Output"
    ![Text Form](img/text-form.png)


### Images

To seamlessly serve one or more image in your custom form or prompt message, the test plan `image_url` method needs to be used. This will create a temporary url that points to the local file you are targeting and allow browsers to load this image successfully.

!!! warning
    The url returned by `image_url` is strictly temporary. It represents an in-memory mapping between the url and the filepath you specified. It follows the lifecycle of the TestPlan object, which means that as long as you keep the same test plan object, the url will live. 
    
    There are no cleanup mecanisms. However, each image is a simple key: value entry in a dictionnary, which means that its memory footprint is negligible.

```python
from spintop_openhtf.util.markdown import markdown, image_url

plan = TestPlan('examples.getting_started')

helpvalue = markdown("""

# Well Hello There
<img src="%s" width="200px" />

""" % plan.image_url('spinhub-app-icon.png'))


FORM_LAYOUT = {
    'schema':{
        'title': "First and Last Name",
        'type': "object",
        'required': ["firstname", "lastname"],
        'properties': {
            'firstname': {
                'type': "string", 
                'title': "First Name"
            },
            'lastname': {
                'type': "string", 
                'title': "Last Name"
            },
        }
    },
    'layout':[
        "firstname",
        {
            "type": "help",
            "helpvalue": helpvalue
        },
        {
            "key": "lastname",
            "type": "radiobuttons",
            "titleMap": [
                { "value": "one", "name": "One" },
                { "value": "two", "name": "More..." }
            ]
        }
    ]
}

```

!!! summary "Output"
    ![Image Form](img/image-form.png)

