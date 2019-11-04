import argparse
from github import Github
import logging
import os
import random
from subprocess import call
import sys
import time
from utility import Utility


def checkIfRepoExistsOnline(githubUser, repoName, credentials):
    command = "curl -u {} https://api.github.com/repos/{}/{}".format(credentials, githubUser, repoName)
    logging.debug("@@checkIfRepoExistsOnline --> command={}".format(command))
    command_output = Utility.execute_process(command)

    logging.debug("@@checkIfRepoExistsOnline --> command_output=\n{}".format(command_output))
    if command_output is None:
        logging.debug("@@checkIfRepoExistsOnline --> command output is None")
        return False
    elif "Not Found" in command_output:
        logging.info("@@checkIfRepoExistsOnline --> url not found for repo={}/{}".format(githubUser, repoName))
        return False
    elif "API rate limit exceeded" in command_output:
        logging.debug("@@checkIfRepoExistsOnline --> API rate limit exceeded")
        return False
    else:
        return True


def downloadRepo(githubUser, repoName, repoStoreRoot, update_existing):
    repoDirPath = os.path.join(repoStoreRoot,repoName)
    command = None
    download = False
    # Check and skip if the repository already exists
    if os.path.exists(repoDirPath):
        if update_existing:
            log_message = "-> updating (pull).."
        #    print(log_message, flush=True) # DEBUG console
            command = "git pull"
            download = True
        else:
            log_message = "-> skipping.."
    else:
        fullRepoName = "https://github.com/" + githubUser + "/" + repoName + ".git"
        command = "git clone --depth 1 {} {}".format(fullRepoName,repoName)
        log_message = "-> downloading.."
        download = True
    
    logging.info("Action for {}/{} {}".format(githubUser,repoName,log_message))
    if command is not None:
        logging.debug("@@downloadRepo --> command={}".format(command))
        os.chdir(repoStoreRoot)
        Utility.execute_process(command)

    return download


def execute_downloader(credentials, repoInputFile, repoStoreRoot, update_existing=False): 
    repoTempStoreRoot = repoStoreRoot

    # read the csv that contains the list of the github repositories 
    lines = Utility.read_file(repoInputFile)
    logging.info("GitHub downloader will process {} repositories.".format(len(lines)))

    for index, line in enumerate(lines):
        # the case that the input list contains also a second field and not just the username/repository
        if ',' in line:
            line = line.split(',')[0]
        repoInfo = line.strip('\n').split("/")
        githubUser = repoInfo[0]
        repoName = repoInfo[1]
        if repoName == "":
            logging.debug("@@execute_downloader --> Skipping empty line")
            # Skip empty lines
            continue
        log_message = "{}/{} :: {}/{}".format((index+1),len(lines),githubUser,repoName)
        logging.info(log_message)
        
        # Check if repo exists online 
        repoExists = checkIfRepoExistsOnline(githubUser,repoName,credentials)
        if not repoExists:
            logging.info("\n\t -> skipped. [not available on GitHub]")
            continue

        userDirPath = os.path.join(repoStoreRoot, githubUser)

        # Check and create the User's directory if it does not exist 
        if not os.path.exists(userDirPath):
            try:
                logging.debug("@@execute_downloader --> User's {} directory does not exist in {}. Creating directory..".format(githubUser, userDirPath))
                os.makedirs(userDirPath)
            except Exception as exc: 
                logging.warning("@@execute_downloader --> Error while creating User directory {}\nException:{}".format(userDirPath, exc))

        # Download the repository and take some rest... 
        download = downloadRepo(githubUser, repoName, userDirPath, update_existing)
        n = random.randint(5,30)
        if not download:
            n = 1
        else:
            logging.info("Sleep for {} secs".format(str(n)))

        time.sleep(n)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    logging.info("Executing script as stand-alone.")

    parser = argparse.ArgumentParser()
    parser.add_argument("credentials", 
        help="The Github username and token like username:token")
    parser.add_argument("github_repository_list", 
        help="The CSV file that contains the github projects that will be downloaded")
    parser.add_argument("output_directory_path", 
        help="The directory in which the github projects will be downloaded. Note that you need to provide a full path!")
    parser.add_argument("-u", "--update_existing", action='store_true',
        help="Updates (pull) an existing local repository. NOT FULLY TESTED")
    args = parser.parse_args()

    credentials = args.credentials
    repoInputFile = args.github_repository_list
    repoStoreRoot = args.output_directory_path
    update_existing = args.update_existing

    execute_downloader(credentials, repoInputFile, repoStoreRoot, update_existing)