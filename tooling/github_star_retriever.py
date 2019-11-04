import argparse
import time
import logging

import requests
from requests.auth import HTTPBasicAuth
from utility import Utility

# This is a sample representation of a repository details in the input 'original_csv'
# 84371488;https://api.github.com/repos/IndustrialGamer/PalaceTags;32498068;2017-12-31 23:52:15;-1;0;1970-01-02 00:00:00
# [0] = id
# [1] = url
# [2] = owner_id
# [3] = date_added
# [4] = forked_id
# [5] = deleted
# [6] = updated_at

def isForked(forked_id):
    return forked_id != -1


def retrieve_stars(credentials, projectList_filePath, output_filepath, skip_forked=False):
    csv_field_separator = ';'
    repository_list = Utility.read_file(projectList_filePath)
    username = credentials.split(':')[0]
    token = credentials.split(':')[1]

    repolist_size = len(repository_list)

    for index, repo in enumerate(repository_list[1:]): # skip the headers
        index += 1
        repo_details = repo.split(';')     
        repo_url = repo_details[1] # the repository's github api url
        forked_id = int(repo_details[4])
        if skip_forked and isForked(forked_id):
            logging.warning(" {}/{}--> FORKED. Skipping :: {}".format(index, repolist_size, repo))
            continue
            
        time.sleep(.2) # sleep for 0.3 seconds to avoid exceeding the limit of 5k requests per hour
        logging.debug(repo_url)
        try:
            http_response = requests.get(repo_url, auth=(username, token))
            json_content = http_response.json()
            stars = json_content['watchers_count'] # retrieve the value of the field 'watchers_count'
            logging.info(" {}/{}--> {} :: {}".format(index, repolist_size, repo, stars))
        except Exception as e:
            stars = '#StarsNotAvailable#'
            logging.warning(" {}/{}--> FAILED :: {}".format(index, repolist_size, repo, stars))
            # logging.error(e)

        output_string = "{}{}{}\n".format(repo, csv_field_separator, stars) # create the output string
        logging.debug("Writting to {} file :: {}".format(output_filepath, output_string))
        Utility.write_to_file(output_filepath, output_string)  # write the output string to a file

        


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    logging.info("Executing script as stand-alone.")

    parser = argparse.ArgumentParser()
    parser.add_argument("credentials", 
        help="Your Github username and token separated by :")
    parser.add_argument("project_list", 
        help="The file that contains a list of Github repositories")
    parser.add_argument("output_file", 
        help="The file that will store the Github repositories with their stars")
    parser.add_argument("--skip_forked",  
        help="The file that will store the Github repositories with their stars",
        action='store_true')
    args = parser.parse_args()

    # logging.info("Skipping ")

    output_file = args.output_file
    project_list = args.project_list
    credentials = args.credentials
    skip_forked=False
    if args.skip_forked:
        skip_forked = True

    logging.info("Skipping forked repositories :: {}".format(skip_forked))


    retrieve_stars(credentials, project_list, output_file, skip_forked)