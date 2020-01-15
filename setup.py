
from setuptools import setup

setup(
    name='odoo_manager',
    packages=['odoo_manager'],
    description='Wrapper to start odoo development and create new modules',
    license='GNU GPLv3',
    author='Elmeri Niemela',
    version='1.0',
    include_package_data=True,
    install_requires=[
        'prompt_toolkit', 'jinja2',
    ],
    entry_points={'console_scripts': ['odoo_manager = odoo_manager.manager:main',],},
)
