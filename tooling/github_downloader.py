import argparse
from github import Github
import os
import random
from subprocess import call
import sys
import time
from utility import Utility


def checkIfRepoExistsOnline(githubUser, repoName, logFile, credentials):
    command = "curl -u {} https://api.github.com/repos/{}/{}".format(credentials, githubUser, repoName)
    # print("Checking if repo {}/{} exists".format(githubUser,repoName))
    result = Utility.execute_process(command)
    # print(result)
    if result is None or "Not Found" in result or "API rate limit exceeded" in result:
        # print("Not found or Limit exceeded")
        return False
    else:
        return True


def downloadRepo(githubUser, repoName, repoStoreRoot, logFile, update_existing):
    repoDirPath = os.path.join(repoStoreRoot,repoName)
    command = None
    download = False
    # Check and skip if the repository already exists
    if os.path.exists(repoDirPath):
        if update_existing:
            log_message = " -> updating (pull).."
        #    print(log_message, flush=True) # DEBUG console
            command = "git pull"
            download = True
        else:
            log_message = " --> skipping.."
    else:
        fullRepoName = "https://github.com/" + githubUser + "/" + repoName + ".git"
        command = "git clone --depth 1 {} {}".format(fullRepoName,repoName)
        log_message = " -> downloading.."
        download = True
        # print(log_message, flush=True) # DEBUG console
    
    Utility.log(log_message)
    # print(log_message.ljust(60), end='\r', flush=True)
    print(log_message,end='', flush=True)
    if command is not None:
        os.chdir(repoStoreRoot)
        Utility.execute_process(command)
    # sys.stdout.write("\033[F") # Cursor up one line
    # print("",flush=True)
    return download


def execute_downloader(credentials, repoInputFile, repoStoreRoot, update_existing=False): 

    repoTempStoreRoot = repoStoreRoot
    logFile = repoStoreRoot + "log.txt"

    # read the csv that contains the list of the github repositories 
    lines = Utility.read_file(repoInputFile)
    log_message = "GitHub repo downloader will process {} repositories.".format(len(lines))
    print(log_message, flush=True) # Do not delete!
    Utility.log(log_message)    

    for index, line in enumerate(lines):
        # the case that the input list contains also a second field and not just the username/repository
        if ',' in line:
            line = line.split(',')[0]
        repoInfo = line.strip('\n').split("/")
        githubUser = repoInfo[0]
        repoName = repoInfo[1]
        if repoName == "":
            # Skip empty lines
            continue
        log_message = "{}/{} :: {}/{}".format((index+1),len(lines),githubUser,repoName)
        Utility.log(log_message)   
        print(log_message, end='', flush=True) # DEBUG console

        # Check if repo exists online 

        repoExists = checkIfRepoExistsOnline(githubUser,repoName,logFile,credentials)
        if not repoExists:
            log_message = " -> skipped. [not available on GitHub]".format(githubUser,repoName)
            Utility.log(log_message)
            print(log_message.ljust(60), flush=True)
            sys.stdout.write("\033[F")
            # print(log_message, end='\r', flush=True)
            continue

        userDirPath = os.path.join(repoStoreRoot, githubUser)

        # Check and create the User's directory if it does not exist 
        if not os.path.exists(userDirPath):
            try:
                log_message = "User's {} directory does not exist in {}. Creating directory..".format(githubUser, userDirPath)
                Utility.log(log_message)
                # print("log_message, flush=True) # DEBUG console
                os.makedirs(userDirPath)
            except Exception as exc: 
                error_message = "Error while creating User directory {}\nException:{}".format(userDirPath, exc)
                Utility.log(error_message)
                # print(error_message, flush=True) # DEBUG console

        # Download the repository and take some rest... 
        download = downloadRepo(githubUser, repoName, userDirPath, logFile, update_existing)
        n = random.randint(5,30)
        if not download:
            n = 1
        log_message = " [sleep for " + str(n) + " secs]"
        Utility.log(log_message)
        print(log_message.ljust(60), flush=True) # DEBUG console
        sys.stdout.write("\033[F")
        time.sleep(n)


if __name__ == '__main__':
    print("Executing script as stand-alone.")

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

    repoInputFile = args.github_repository_list
    repoStoreRoot = args.output_directory_path
    update_existing = args.update_existing
    credentials = args.credentials

    execute_downloader(credentials, repoInputFile, repoStoreRoot, update_existing)