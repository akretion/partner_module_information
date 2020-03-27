The goal of this module is to expose a rest api on an odoo instance with github_connector_odoo installed.
It will allow another odoo instance, with module module_info_import installed to get the data related to existing odoo modules in all version.
Note that we do this instead of using directly github_connector_odoo on the second odoo instance mainly to avoid this big dependency.
Indeed, the first instance, gathering info about all modules can be in a version unrelated to our second instance and it is not a problem.
