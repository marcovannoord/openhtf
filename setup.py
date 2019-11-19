import os
import sys
from glob import glob

from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))

sys.path.insert(0, os.path.join(HERE, 'openhtf'))

with open(os.path.join(HERE, 'src', 'spintop_openhtf', 'VERSION')) as version_file:
    VERSION = version_file.read().strip()

if not os.path.exists(os.path.join('openhtf', 'openhtf')):
    raise Exception('Please checkout the openhtf submodule before install.')

compiled_proto_files = glob('openhtf/openhtf/output/proto/*_pb2.py')
if not compiled_proto_files:
    raise Exception('Protobuf files in openhtf where not compiled. Must be done before hand.')

# Find packages under openhtf(git) / openhtf
# Add the package itself

openhtf_packages = ['openhtf'] + ['openhtf.' + pack for pack in find_packages(where='openhtf/openhtf')]
packages =  openhtf_packages + find_packages('src')

setup(
    name='spintop-openhtf',
    version=VERSION,
    description='A complete integration to SpinHub using OpenHTF. OpenHTF is currently vendored-in.',
    author='William Laroche',
    author_email='william.laroche@tackv.ca',
    maintainer='William Laroche',
    maintainer_email='william.laroche@tackv.ca',
    package_dir={
        '': 'src',
        'openhtf': 'openhtf/openhtf',
    },
    packages=packages,
    package_data={
        'openhtf': [
            'output/proto/*.proto',
            'output/web_gui/dist/*',
            'output/web_gui/dist/css/*',
            'output/web_gui/dist/js/*',
            'output/web_gui/dist/img/*',
            'output/web_gui/*'
        ],
        'spintop': ['VERSION']
    },
    install_requires=[
        'oauth2client>=4.1.0',
        'colorama>=0.3.9,<1.0',
        'contextlib2>=0.5.1,<1.0',
        'future>=0.16.0',
        'gspread>=3.1.0',
        'google-api-python-client>=1.7.10',
        'mutablerecords>=0.4.1,<2.0',
        'oauth2client>=4.1.3',
        'protobuf>=3.6.0,<4.0',
        'PyYAML>=3.13,<4.0',
        'pyOpenSSL>=17.1.0,<18.0',
        'SheetFu>=1.4.1',
        'sockjs-tornado>=1.0.3,<2.0',
        'tornado>=4.3,<5.0',
        'pyserial>=3.3.0,<4.0',
        'jsonschema>=3.0.2'
    ],
    extras_require={
    },
    setup_requires=[
        'wheel>=0.29.0,<1.0',
    ],
    tests_require=[
        'mock>=2.0.0',
        'pytest>=2.9.2',
        'pytest-cov>=2.2.1',
    ],
)