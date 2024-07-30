
<!-- /!\ Non OCA Context : Set here the badge of your runbot / runboat instance. -->
[![Pre-commit Status](https://github.com/akretion/partner-module-information/actions/workflows/pre-commit.yml/badge.svg?branch=16.0)](https://github.com/akretion/partner-module-information/actions/workflows/pre-commit.yml?query=branch%3A16.0)
[![Build Status](https://github.com/akretion/partner-module-information/actions/workflows/test.yml/badge.svg?branch=16.0)](https://github.com/akretion/partner-module-information/actions/workflows/test.yml?query=branch%3A16.0)
[![codecov](https://codecov.io/gh/akretion/partner-module-information/branch/16.0/graph/badge.svg)](https://codecov.io/gh/akretion/partner-module-information)
<!-- /!\ Non OCA Context : Set here the badge of your translation instance. -->

<!-- /!\ do not modify above this line -->

# Partner Module Information

Repo for managing odoo modules and follow migration by project

This repo allow you to :

- Synchronise module information with a list of community module https://github.com/akretion/odoo-module-tracker/blob/gh-pages/
- Synchronise the PR state with github api
- Push module's informations from remote Odoo
- See in one kanban the PRs in current and higher version who can impact your projects
- Attach a timesheet to a PR review to report your reviewer time
- Follow migration goal for partner project (in progress)

![partner_module](docs/images/partner_module.png)


<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

This part will be replaced when running the oca-gen-addons-table script from OCA/maintainer-tools.

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to Akretion
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----
<!-- /!\ Non OCA Context : Set here the full description of your organization. -->
