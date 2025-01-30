import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo10-addons-akretion-partner-module-information",
    description="Meta package for akretion-partner-module-information Odoo addons",
    version=version,
    install_requires=[
        'odoo10-addon-module_info_import',
        'odoo10-addon-module_info_partner',
        'odoo10-addon-module_info_push',
        'odoo10-addon-module_partner_migration',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 10.0',
    ]
)
