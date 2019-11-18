# Spintop Hardware Coverage

References:

- https://blog.asset-intertech.com/test_data_out/2010/12/structural-versus-functional-test.html

This package defines concepts and structures to allow the coverage analysis of the functionnal testing of a physical - usually electronic - system.

## Overview

Using a YAML file, the user defines the list of *nets* and *components* in his system.

- **Nets** are analogous to electrical nets; they represent a channel (such as a PCB trace). They are usually connected to two or more components
- **Components** are the end-points of nets.

Using both of these concepts, a list of *net-component*s can be built. These represent the connection between the component and the net(s). They are the point of failures one is trying to detect.

## Truths

- A net is a connection between components
- A net cannot be tested by itself; a test is done on a source component and (a) target component(s)

## Net

Each net is parsed from a list string: `X1,X2` would represent a single net with two aliases: X1 and X2. Refering to X1 is then equivalent to X2 and vice-versa.

## Coverage analysis

1. The first step is to create a global immutable and flattened list of all the nets in all components. Nets are agnostic to the notion of component.
2. The list of components and their nets is flattened into a list of NetComp - short for Net-Component. Their name is based on the component hierarchy and the net name. A net Z defined in component Y which is inside component X would represent the unique NetComp named `X.Y.Z`. This NetComp would be linked with the global net named `Z`.
3. 

