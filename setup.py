"""
walnut: A minimalistic trading engine middleware
"""

import setuptools

with open('README.md') as f:
    long_description = f.read()

setuptools.setup(
    name='walnut',
    version='0.0.1',
    description=__doc__,
    long_description=long_description,
    author='Lion Ackermann',
    url='https://github.com/liona24/walnut',
    packages=['walnut'],
    package_dir={ '': 'src' },
    package_data={ 'walnut': ['schema_definitions.json'] },
    install_requires=[
        'numpy',
        'pandas',
        'jsonschema',
        'python-dateutil'
    ],
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3'
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
    ]
)
