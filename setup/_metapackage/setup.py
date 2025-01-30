import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-akretion-partner-module-information",
    description="Meta package for akretion-partner-module-information Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-github_connector_stat',
        'odoo12-addon-module_info_import',
        'odoo12-addon-module_info_partner',
        'odoo12-addon-module_info_push',
        'odoo12-addon-module_partner_migration',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 12.0',
    ]
)
