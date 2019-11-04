import argparse
import os
import logging

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


def detect_build_files(repository_path):
    """
    Detects and stores all build automation configuration files
    i.e., pom.xml, build.gradle for a given repository

    Parameters
    ----------
    repository_path : str
        The path of the directory of the given repository

    Returns
    -------
    dictionary
        a dictionary of java build automation configuration files and the depth of their path
    """
    logging.info("Scanning repo :: {}".format(repository_path))
    buildAutomationConfigFiles = {}

    for root, dirs, files in os.walk(repository_path):
        for file in files:
            if file.endswith("pom.xml") or file.endswith("build.gradle"):
                fullFilePath = os.path.join(root,file)
                depthInTree = fullFilePath.count('/')
                if depthInTree in buildAutomationConfigFiles:
                    buildAutomationConfigFiles[depthInTree].append(fullFilePath)
                else:
                    buildAutomationConfigFiles[depthInTree] = [fullFilePath]

    if len(buildAutomationConfigFiles) == 0:
        logging.warning("Error detecting build files for project {}".format(repository_path))

    return buildAutomationConfigFiles



def detect_repository_root_directory(buildAutomationConfigFiles):
    """
    Detects the root directory of a repository. (where the 
    main pom.xml or/and build.gradle file is defined)
    """
    # print(buildAutomationConfigFiles)

    outputMessage = ""

    if len(buildAutomationConfigFiles) < 1:
        return "FailedToDetect"

    root_candidates = buildAutomationConfigFiles[min(buildAutomationConfigFiles)]
    if len(root_candidates) > 1:
        outputMessage = "RequiresManualResolution"
        print("candidates :: {}".format(root_candidates))
    else:
        outputMessage = root_candidates[0]

    return outputMessage
    # TODO: write the result in a file 

def detect_configuration_file(root_directory, output_file):
    """
    This executes the steps for:
    1. Identifying repositories
    2. Detecting all build automation cofiguration files
    3. Identifying the main build automation cofiguration file
    4. Writting the result
    """
    # step 1
    repository_list = retrieve_repositoty_directory_paths(root_directory)
    print("Detected {} repositories".format(len(repository_list)))

    # step 2
    for index, repository in enumerate(repository_list):
        logging.info("{}/{}".format(++index, len(repository_list)))
        print(repository)
        buildAutomationConfigFiles = detect_build_files(repository)

        # step 3
        mainBuildAutomationConfigFile = detect_repository_root_directory(buildAutomationConfigFiles)
        outputMessage="{};{}".format(repository, mainBuildAutomationConfigFile)
        with open(output_file, "a") as myfile:
            myfile.write("{}\n".format(outputMessage))


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    logging.info("Executing script as stand-alone.")

    parser = argparse.ArgumentParser()
    parser.add_argument("root_directory", 
        help="The directory that holds the github users' subdirectories")
    parser.add_argument("output_file", 
        help="The file that stores the final information")
    args = parser.parse_args()

    root_directory = args.root_directory
    output_file = args.output_file
    # print(repo_list)
    detect_configuration_file(root_directory, output_file)
