import argparse
import yaml
import requests
from semver import Version, compare
import re
import os
import logging

def main() -> None:

# utiliser argparse pour show_ok and show_current
    parser = argparse.ArgumentParser(
                        prog='version monitoring tool',
                        description='Check if new version of your tools are available')

    parser.add_argument('-o', '--output_file', type=bool, default="available_versions.yml", help='File to store versions infos [str]')
    parser.add_argument('-i', '--input_file', type=str, default="versions.yml", help='File that contains app versions [str]')
    parser.add_argument('-c', '--hide_curr', type=bool, default=False, help='Hide current version of apps [bool]')

    args = parser.parse_args()
    output_file = args.output_file
    input_file = args.input_file
    hide_curr = args.hide_curr

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    with open(input_file, "r") as versions:
        try:
            versions_yml = yaml.load(versions, Loader=yaml.FullLoader)
            for item in versions_yml:
                current_conf = versions_yml[item]['config']
                current_version = get_current_version(current_conf)
                # current_conf = versions_yml[item]['config']
                # current_version = versions_yml[item]['version']
                source_conf = versions_yml[item]['source']
                # sourcing_with_creds(source_conf)
                available_version = get_latest_tag(source_conf)
                format_result(item, current_version, available_version, hide_curr)
        except yaml.YAMLError as exc:
            print(exc)


def get_latest_tag(source_config, full = False):
    """Return the latest tag available

    Parameters:
    source_config: Configuration to retrieve tag

    Returns:
    str:Return one tag
    """
    list_tags = []
    try:
        x = requests_function(source_config)
    except:
        logging.error("http requests")
        return "ERROR"

    for item in x.json():
        if not any(c.isalpha() for c in item['name']):
            list_tags.append(item['name'])
        elif item['name'][0] == 'v':
            if not any(c.isalpha() for c in item['name'][1:]):
                list_tags.append(item['name'])

    if full == False:
        if not any(not Version.is_valid(c) for c in list_tags):
            latest_version = max(list_tags, key=Version.parse)
        else:
            latest_version = 'v' + max([s.replace('v','') for s in list_tags], key=Version.parse)
    return latest_version

def newer_version(current, available):
    """Check if a version is greater than an other

    Parameters:
    current: current tag
    available: target tag

    Returns:
    bool:true if available tag is greater than the current one
    """
    try:
        if compare(str(current).replace('v',''), str(available).replace('v','')) == -1:
            return True
    except ValueError:
        logging.error("Version doivent être au format X.X.X")
    except:
        logging.error('LOL, cpt')

def format_result(app, curr, avail, hide_curr = False):
    """Print function

    Parameters:
    app:name of the application
    curr:current tag of the application
    avail:latest available tag of the application
    hide_curr:
    """
    if newer_version(curr, avail):
        status = "OUTDATED"
    else:
        status = "ok"

    if not (status == "ok"):
        if hide_curr:
            print('{"app": "%s", "latest": "%s", "status": "%s"}' % (app, avail, status))
        else:
            print('{"app": "%s", "current": "%s", "latest": "%s", "status": "%s"}' % (app, curr, avail, status))

def requests_function(app_source):
    """Function to requests http pages

    Parameters:
    app_source: configuration to get the information
    """
    if "username" in app_source and "password" in app_source:
        password = get_creds_from_config(app_source['password'])
        username = get_creds_from_config(app_source['username'])
        x = requests.get(app_source['url'], auth=(username, password))
    elif not "username" in app_source and not "password" in app_source:
        x = requests.get(app_source['url'])
    else:
        logging.info("Can get both username and password variable, shift to anonmyous mode")
    return x

def get_creds_from_config(source_pass):
    """Get variables as username or password

    Parameters:
    source_pass: able to get variable from direct or env var (string)
    """
    if source_pass.startswith("env:"):
        env_var_pass = source_pass.split("env:")[1].rstrip()
        if env_var_pass in os.environ:
            return os.environ[env_var_pass]
        else:
            logging.error(env_var_pass, " does not exist")
    return source_pass

def get_current_version(app_config):
    logging.debug('function: get_current_version, status: start')
    # Either version, url or file
    if ("version" in app_config and "url" in app_config) or (
        "version" in app_config and "file" in app_config) or (
        "url" in app_config and "file" in app_config):

        logging.error("parameters incompatible")
    elif "version" not in app_config and "url" not in app_config and "file" not in app_config:
        logging.error("missing parameters, required version/app/url")

    if "version" in app_config:
        return app_config.version
    # version : this file serves as version control
    if "url" in app_config:
        try:
            x = requests.get(app_config['url'])
            config_version = version_from_pattern(app_config['pattern'], x.text.splitlines())
            return config_version
        except KeyError:
            logging.error("pattern param is mandatory with url")
        except:
            logging.error('LOL, cpt dans url')

    # url : file within git
    if "file" in app_config:
        try:
            with open(app_config['file'], "r") as file:
                config_version = version_from_pattern(app_config['pattern'], file)
                return config_version
        except KeyError:
            logging.error("pattern param is mandatory with file")
        except:
            logging.error('LOL, cpt dans file')


def version_from_pattern(pattern, lines):
    for line in lines:
        if re.search(pattern, line):
            return line.split(pattern)[1].rstrip()

if __name__ == "__main__":
    main()



