This module scan all the open PR on the repo list in ModuleRepo.
Before launch this cron you have to load the module.information data to populate the repository. 

To prevent github REST API rate limiting, authenticate with a personnal access token.
Set it in config parameter module.info.pull.request.git.token
