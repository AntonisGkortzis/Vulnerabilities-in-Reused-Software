import argparse
import os
import sys
import re
from utility import Utility


def parse_mvn_install_output(output):
    lines = output.split("\n")
    rule = re.compile(r'^\[INFO\] (\||\\\-|\+\-| )*([a-zA-Z_$][a-zA-Z\d_\-$]*\.)*[a-zA-Z_$][a-zA-Z\d_\-$]*:.+?:([a-zA-Z]+):.+?(:[a-zA-Z\-]+)?$')

    result=[]
    for l in lines:
        if rule.match(l):
            # print(l)
            # sys.stdout.flush()
            result.append(l)
    # print(result)
    # sys.stdout.flush()
    return result


def execute_maven_dependency_tree(repository_fullpath):
    pom_path = "{}/pom.xml".format(repository_fullpath)
    mvn_dependency_tree = "mvn -B dependency:tree -DexcludeTransitive -Dmaven.test.skip=true"
    # mvn_dependency_tree = "mvn -B dependency:tree DexcludeTransitive -Dmaven.test.skip=true"
    # print("Looking for pom :: {}".format(pom_path))
    if not os.path.isfile(pom_path):
        print("\tFailed to find pom :: {}\n Skipping analysis".format(pom_path))
        return

    os.chdir(repository_fullpath)
    output, error = Utility.execute_process(mvn_dependency_tree)
    result = parse_mvn_install_output(output)

    return result


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


def execute(root_directory, output_directory, project_list_path):

    project_list = Utility.read_file(project_list_path)
    repo_list = retrieve_repositoty_directory_paths(root_directory)
    # print(repo_list) # DEBUG
    print("Detected {} repositories in root directory {}".format(len(repo_list), root_directory))
    for index, repository in enumerate(repo_list):
        print("{}/{}. Scanning repository :: {}".format((index+1), len(repo_list),repository))
        sys.stdout.flush()
        if repository not in project_list:
            print("## Repository not in project list. SKIPPING")
            return
            
        result = execute_maven_dependency_tree(repository)
        # Cases that mvn fails to execute 
        # print(len(result))
        if not result:
            continue

        repository = repository.replace(root_directory,'')
        # print(repository)
        output_file = os.path.join(output_directory, "{}.trees".format(repository.replace('/','.')[1:]))
        print("\tWritting file :: {}".format(output_file))
        sys.stdout.flush()
        Utility.write_to_file(output_file,'\n'.join(result))
        # print("===============================================")
        # sys.stdout.flush()


if __name__ == '__main__':
    print("Executing script as stand-alone.")

    parser = argparse.ArgumentParser()
    parser.add_argument("root_directory", 
        help="The directory that holds the github users' subdirectories")
    parser.add_argument("output_directory", 
        help="The directory that holds a txt file with the dependency tree for each project")    
    parser.add_argument("list_of_projects_to_analyze", 
        help="The file that holds the projects to analyze")
    args = parser.parse_args()

    output_directory = args.output_directory
    root_directory = args.root_directory
    project_list_path = args.list_of_projects_to_analyze


    execute(root_directory, output_directory, project_list_path)


