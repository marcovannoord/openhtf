import yaml
from collections import namedtuple

from jinja2 import Template

Net = namedtuple('Net', 'refs')

def load_nets(nets_array):
    nets = {}

    for net_str in nets_array:
        refs = _parse_net_string(net_str)

        net = None
        for ref in refs:
            if ref in nets:
                net = nets[ref]
        
        if net:
            net.refs.update(refs)
        else:
            net = Net(set(refs))
        
        for ref in refs:
            nets[ref] = net

    return nets

def _parse_net_string(net):
    refered_nets = net.split(',')
    return refered_nets

def load_nets_yml_file(filename):
    with open(filename) as f:
        return load_nets_yml(f.read())

def load_nets_yml(yml_string):
    rendered = render_jinja2_template(yml_string)
    content = yaml.load(rendered)
    return load_nets(content['nets'])

def render_jinja2_template(content, data={}):
    template = Template(content)
    return template.render(**data)