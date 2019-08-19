""" Components are hardware-defined components where a stimulus can be
applied or an input can be read. Defining components is the basis of
automated test coverage calculation.
"""

import collections
from .nets import first_alias

def define_component(name, description="", scopes=()):
    return Component()

QUALIFIED_NAME_SEPARATOR = '.'

def qualified_name_join(*strings):
    return QUALIFIED_NAME_SEPARATOR.join(strings)

def net_to_fully_qualified_name(prefix, net):
    return qualified_name_join(prefix, first_alias(net))
    
class Component(object):
    def __init__(self, name, description="", components=[], nets=[], refdes=[]):
        self._parent = None
        self.name = name
        self.description = description
        
        self.components = [None]*len(components)
        for i, component in enumerate(components):
            if isinstance(component, collections.Mapping):
                component = self.__class__(**component)
            
            component.attach_to(self)
            self.components[i] = component
        
        self.nets = nets
        self.refdes = refdes
        
        self._nets_parsed = False
        
    def attach_to(self, parent):
        self._parent = parent
        self.prefix = self.fully_qualified_prefix()
        
    def fully_qualified_prefix(self):
        if self._parent:
            return qualified_name_join(self._parent.fully_qualified_prefix(), self.name)
        else:
            return self.name
        
    def fully_qualified_nets(self, prefix=None):
        if prefix is None:
            prefix = self.fully_qualified_prefix()
        return [net_to_fully_qualified_name(prefix, net) for net in self.nets]
        
    def iter_all(self, include_self=True):
        if include_self:
            yield self
        
        for top_component in self:
            for component in top_component.iter_all(include_self=True):
                yield component
    
    def iter_fully_qualified_nets(self):
        nets = []
        for component in self.iter_all():
            nets += component.fully_qualified_nets()
        return nets
        
    def __iter__(self):
        for component in self.components:
            yield component
    
    