import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-akretion-partner-module-information",
    description="Meta package for akretion-partner-module-information Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-module_info_import',
        'odoo14-addon-module_info_migration',
        'odoo14-addon-module_info_partner',
        'odoo14-addon-module_info_pull_request',
        'odoo14-addon-module_info_pull_request_timesheet',
        'odoo14-addon-module_info_push',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
