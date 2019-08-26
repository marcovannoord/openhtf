import itertools
from collections import Sequence
from spintop.util.compat import isstr

def flatten_string_list(array):
    new_array = []
    for item in array:
        if isinstance(item, Sequence) and not isinstance(item, str):
            new_array += item
        else:
            new_array.append(item)
            
    return new_array

class DomainNodeInterface(object):
    def __init__(self, obj):
        self._dict = obj
    
    @property
    def name(self):
        return self._dict.get('name', '')
    
    @property
    def description(self):
        return self._dict.get('description', '')
    
    @property
    def nodes(self):
        return self._dict.get('nodes', [])
    
    @property
    def edges(self):
        return self._dict.get('edges', [])
    
    @property
    def required(self):
        return self._dict.get('required', False)
    
    @property
    def implies(self):
        return self._dict.get('implies', [])
    
    @property
    def testable(self):
        return self._dict.get('testable', False)

    @property
    def data(self):
        """ Domain specific data. """
        return {}
    
    def as_node(self, context):
        
        node_objects = [context.to_node(child_node) for child_node in self.nodes]
        
        edges = flatten_string_list(self.edges)
        
        node = Node(
            name=self.name,
            description=self.description,
            nodes=node_objects,
            edges=edges,
            required=self.required,
            implies=self.implies,
            testable=self.testable,
            data=self.data
        )
        
        return node
    
class ElectricalDomainInterface(DomainNodeInterface):
    
    @property
    def nodes(self):
        return self._dict.get('components', [])
    
    @property
    def edges(self):
        return self._dict.get('testpoints', [])
    
    @property
    def testable(self):
        return False

class NodeTreeContext(object):
    def __init__(self, domain_interface=ElectricalDomainInterface):
        self.domain_interface = domain_interface
        self.root = None
        self.graph = None
        
    def parse(self, node_dict):
        if not node_dict.get('name', None):
            node_dict['name'] = 'root'
        self.root = self.to_node(node_dict)
        return self.root
    
    def to_node(self, node_dict):
        return self.domain_interface(node_dict).as_node(self)
    
    def build_graph(self):
        """ Builds the dependency graph.
        
        The build is separated into two steps:
        1. Implied dependencies.
            These are dependencies specified by the shape of the tree and the parent/child
            relationships. When the 'required' node property is false, a compliant child
            adds an inbound test edge. When required is true, the the relationship is 
            inversed and the test coverage flows from the parent to the child.
        2. Direct dependencies.
            These are dependencies linked accross the tree using the defined edges.
        """
        import networkx as nx
        
        self.graph = nx.DiGraph()
        edges_map = {}
        self.nodes_map = {}
        
        if self.root is None:
            raise RuntimeError('self.parse must be called before build_connectivity_graph')
        
        # Step 1: Link nodes implied dependencies
        for node in self.root.iter_children():
            qualname = self.add_node(node)
            
            # Add nodes and edges to temporary maps
            for edge in node.edges:
                linked_nodes = edges_map.get(edge, set())
                linked_nodes.add(qualname)
                edges_map[edge] = linked_nodes
                
            # Create the implied dependencies
            if node.parent:
                if node.required:
                    self.add_edge(node.parent.qualname, qualname)
                else:
                    self.add_edge(qualname, node.parent.qualname)
            elif node.required:
                raise RuntimeError('Cannot have required property without a parent node.')
            
            for implied_qualname in node.implies:
                self.add_edge(qualname, implied_qualname)
        
        # Step 2
        for linkname, nodes in edges_map.items():
            for u,v in itertools.combinations(nodes, 2):
                self.add_testable_edge(linkname, u, v)
        
        return self.graph
    
    def add_testable_edge(self, linkname, qualname_u, qualname_v):
        new_node = Node(
            name=qualname_u + '/' + linkname + '/' + qualname_v,
            testable=True
        )
        self.add_node(new_node)
        
        source = new_node.qualname
        self.add_edge(source, qualname_u)
        self.add_edge(source, qualname_v)
        
    
    def add_node(self, node):
        qualname = node.qualname
        print('Add node %s' % qualname)
        self.graph.add_node(qualname, qualname=qualname, node=node)
        self.nodes_map[qualname] = node
        return qualname
        
    def add_edge(self, u, v):
        print('Add edge %s to %s' % (u, v))
        self.graph.add_edge(u, v)
        
                
        
    

class Node(object):
    def __init__(self, name="", description="", nodes=[], edges=[], required=False, implies=[], testable=False, data={}):
        self._parent = None
        self.name = name
        self.description = description
        self.nodes = nodes
        self.edges = edges
        self.required = required
        self.implies = implies
        self.testable = testable
        
        self.data = data
        
        for node in nodes:
            node.attach_to(self)
            
    @property
    def parent(self):
        return self._parent
            
    def __contains__(self, name_or_node):
        
        if isstr(name_or_node):
            for node in self.nodes:
                if name_or_node == node.name:
                    return True
            else:
                return False
        else:
            return name_or_node in self.nodes
    
    @property
    def qualname(self):
        if self._parent:
            return self._parent.qualname + '.' + self.name
        else:
            return self.name
        
    def attach_to(self, parent):
        self._parent = parent
        
    def iter_children(self):
        yield self
        for topnode in self.nodes:
            for subnode in topnode.iter_children():
                yield subnode
         
