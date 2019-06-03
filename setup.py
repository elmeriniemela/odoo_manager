
from setuptools import setup

setup(
    name='odoo_manager',
    packages=['odoo_manager'],
    include_package_data=True,
    install_requires=[
        'prompt_toolkit', 'jinja2',
    ],
)
