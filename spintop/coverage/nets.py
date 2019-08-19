from collections import namedtuple
from spintop.util import yaml_loader

Net = namedtuple('Net', 'refs')
    

def load_nets(nets_array, nets=None):
    if nets is None:
        nets = {}
    
    for net_str in nets_array:
        refs = _get_net_refs(net_str)

        net = None
        for ref in refs:
            net = nets.get(ref, net)
       
        if net:
            net.refs.update(refs)
        else:
            net = Net(set(refs))
       
        for ref in refs:
            nets[ref] = net

    return nets

ALIAS_SEPARATOR = ','


def _get_net_refs(net):
    if isinstance(net, str):
        refered_nets = net.split(ALIAS_SEPARATOR)
        return [ref.strip() for ref in refered_nets] # Strip removes white space around separators
    else:
        return net.refs
    
def first_alias(net):
    refs = _get_net_refs(net)
    return refs[0]

def load_nets_yml_file(filename):
    return load_nets_dict(yaml_loader.load_yml_file(filename))

def load_nets_yml(yml_string):
    return load_nets_dict(yaml_loader.load_yml(yml_string))

def load_nets_dict(content):
    return load_nets(content['nets'])