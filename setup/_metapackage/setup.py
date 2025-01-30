import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-akretion-partner-module-information",
    description="Meta package for akretion-partner-module-information Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-module_info_push',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 8.0',
    ]
)
