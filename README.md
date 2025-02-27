# version-manager

The purpose of this tool is to help version management. Be able to get latest version of an app, compared with the ones you use and print if an update is possible.

The files and their roles :
- main.py : the script itself
- versions.yml : the central file to describe which tool has to be managed, what are the sources/repo
- local.cfg : file used as example if you want to use local file to store versions
- requirements.txt : the python libraries mandatory for the app
- Dockerfile : Dockerfile to generate container image of the app (image containing the versions.yml file)
