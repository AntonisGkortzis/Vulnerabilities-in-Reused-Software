import argparse
import os

from utility import Utility


def revert_repository(checkout_date):
    checkout_command = "git checkout `git rev-list -n 1 --first-parent --before={} master`".format(checkout_date)
    print("\t{}".format(checkout_command))
    Utility.execute_process(checkout_command)


def clean_repository():
    print("\tmvn clean..")
    mvn_clean_command = "mvn clean"
    Utility.execute_process(mvn_clean_command)


def parse_mvn_install_output(output):
    if "BUILD SUCCESS" in output:
        # print("BUILD SUCCESS")
        return True
    elif "BUILD FAILURE" in output:
        # print("FAILURE")
        return False
    else:
        # print("no result was detected during build")
        return False
    # return False


def execute_maven_install(repository_fullpath, clean_repository_before_install, checkout_repository):
    pom_path = "{}/pom.xml".format(repository_fullpath)
    mvn_install_command = "mvn install -Dmaven.test.skip=true -Dmaven.javadoc.skip=true -Dgpg.skip"
    # print("Looking for pom :: {}".format(pom_path))
    if not os.path.isfile(pom_path):
        print("\tFailed to find pom :: {}".format(pom_path))
        return
    
    os.chdir(repository_fullpath)
    # Clean the repo before building if user set the flag
    if clean_repository_before_install:
        clean_repository()

    # Checkout an older version of the repository if user set the flag
    if checkout_repository:
        revert_repository(checkout_repository)

    output, error = Utility.execute_process(mvn_install_command)
    successful_run = parse_mvn_install_output(output)

    if successful_run:
        print("Success :: {}".format(repository_fullpath))
    else:
        print("Failed :: {}".format(repository_fullpath))
        


def retrieve_repositoty_directory_paths(root_directory):
    repo_list = []
    github_userlist = os.listdir(root_directory)
    # traverse through github users' directories
    for github_user in github_userlist:
        github_user_fullpath = os.path.join(root_directory,github_user)
        # print(github_user_fullpath)
        repositorylist = os.listdir(github_user_fullpath)
        # traverse through github users repositories
        for repository in repositorylist:
            repository_fullpath = os.path.join(github_user_fullpath,repository)
            if not os.path.isdir(repository_fullpath): # skip files
                continue
            else: # work only on directories, a.k.a repositories
                # print("Adding repo to list : {}".format(repository_fullpath))
                repo_list.append(repository_fullpath)

    return repo_list


def execute_mvn_install(root_directory, clean_repository_before_install=False, checkout_repository=None):
    repo_list = retrieve_repositoty_directory_paths(root_directory)
    # print(repo_list) # DEBUG
    print("Detected {} repositories in root directory {}".format(len(repo_list), root_directory))
    for index, repository in enumerate(repo_list):
        # print("{}/{}. Building project :: {}".format((index+1), len(repo_list),repository), flush=True)
        execute_maven_install(repository, clean_repository_before_install, checkout_repository)


if __name__ == '__main__':
    print("Executing script as stand-alone.")

    parser = argparse.ArgumentParser()
    parser.add_argument("root_directory", 
        help="The directory that holds the github users' subdirectories")
    parser.add_argument('--revert','-r', 
        help='Checkout each repository to an older date. The given date should be 2018-01-01')
    parser.add_argument('--clean','-c', 
        help='Clean a maven repository before building it',
        action='store_true')
    args = parser.parse_args()

    root_directory = args.root_directory
    clean_repository_before_install = args.clean
    checkout_repository = args.revert
    execute_mvn_install(root_directory, clean_repository_before_install, checkout_repository)
