import argparse
import logging
import os
import sys
import re
from utility import Utility

logging.getLogger().setLevel(logging.INFO)


def parse_mvn_install_output(output):
    lines = output.split("\n")
    rule = re.compile(r'^\[INFO\] (\||\\\-|\+\-| )*([a-zA-Z_$][a-zA-Z\d_\-$]*\.)*[a-zA-Z_$][a-zA-Z\d_\-$]*:.+?:([a-zA-Z]+):.+?(:[a-zA-Z\-]+)?$')

    result=[]
    for l in lines:
        if rule.match(l):
            result.append(l)

    logging.debug("@parse_mvn_install_output -> detected :\n\t{})".format(result))
    return result


def execute_maven_dependency_tree(repository_fullpath, repository_maven_pom):
    logging.debug("@execute_maven_dependency_tree -> pom={}".format(repository_maven_pom))
    last_path_seperator_position = repository_maven_pom.rfind('/')
    repository_maven_root_dir = repository_maven_pom[:last_path_seperator_position]
    logging.debug("@execute_maven_dependency_tree -> root={}".format(repository_maven_root_dir))

    mvn_dependency_tree = "mvn -B dependency:tree -DexcludeTransitive -Dmaven.test.skip=true"
    # mvn_dependency_tree = "mvn -B dependency:tree DexcludeTransitive -Dmaven.test.skip=true"
    if not os.path.isfile(repository_maven_pom):
        logging.warning("\tFailed to find pom :: {}\n Skipping analysis".format(repository_maven_pom))
        return

    os.chdir(repository_maven_root_dir)
    output, error = Utility.execute_process(mvn_dependency_tree)
    result = parse_mvn_install_output(output)

    logging.debug("@execute_maven_dependency_tree -> get dependencies result ::\n{}".format(result))
    return result


# def retrieve_repositoty_directory_paths(root_directory):
#     repo_list = []
#     github_userlist = os.listdir(root_directory)
#     # traverse through github users' directories
#     for github_user in github_userlist:
#         github_user_fullpath = os.path.join(root_directory,github_user)
#         # print(github_user_fullpath)
#         repositorylist = os.listdir(github_user_fullpath)
#         # traverse through github users repositories
#         for repository in repositorylist:
#             repository_fullpath = os.path.join(github_user_fullpath,repository)
#             if not os.path.isdir(repository_fullpath): # skip files
#                 continue
#             else: # work only on directories, a.k.a repositories
#                 # print("Adding repo to list : {}".format(repository_fullpath))
#                 repo_list.append(repository_fullpath)

#     return repo_list


def retrieve_repositoty_maven_root_paths(repos_with_paths):
    maven_root_paths_list = {}
    with open(repos_with_paths) as f:
        lines = f.read().splitlines()

    for line in lines:
        fields = line.split(';')
        maven_root_paths_list[fields[0]] = fields[1]

    return maven_root_paths_list


def execute(root_directory, output_directory, project_list_path, maven_root_paths):
    project_list = Utility.read_file(project_list_path)
    maven_root_paths_list = retrieve_repositoty_maven_root_paths(maven_root_paths)
    logging.debug("maven_root_paths_list ::\n{}".format(maven_root_paths_list))
    logging.info("Detected {} sucessfully built repositories.".format(len(project_list)))
    for index, repository in enumerate(project_list):
        logging.info("{}/{}. Scanning repository :: {}".format((index+1), len(project_list),repository))
        if repository not in maven_root_paths_list:
            logging.warning("## Repository not in project list. SKIPPING")
            continue
            
        output_file = os.path.join(output_directory, "{}.trees".format(repository.replace('/','.')))
        if os.path.exists(output_file):
            logging.info("Analysis already exists. skipping..")
            continue

        result = execute_maven_dependency_tree(repository, maven_root_paths_list[repository])
        # Cases that mvn fails to execute 
        if not result:
            logging.warning("Failed to extract dependencies -> {}".format(repository))
            continue

        repository = repository.replace(root_directory,'')
        output_file = os.path.join(output_directory, "{}.trees".format(repository.replace('/','.')))
        logging.info("Writting file :: {}".format(output_file))
        Utility.write_to_file(output_file,'\n'.join(result))



# def execute(root_directory, output_directory, project_list_path, maven_root_paths):

#     project_list = Utility.read_file(project_list_path)
#     repo_list = retrieve_repositoty_directory_paths(root_directory)
#     # print(repo_list) # DEBUG
#     print("Detected {} repositories in root directory {}".format(len(repo_list), root_directory))
#     for index, repository in enumerate(repo_list):
#         print("{}/{}. Scanning repository :: {}".format((index+1), len(repo_list),repository))
#         sys.stdout.flush()
#         if repository not in project_list:
#             print("## Repository not in project list. SKIPPING")
#             return
            
#         result = execute_maven_dependency_tree(repository)
#         # Cases that mvn fails to execute 
#         # print(len(result))
#         if not result:
#             continue

#         repository = repository.replace(root_directory,'')
#         # print(repository)
#         output_file = os.path.join(output_directory, "{}.trees".format(repository.replace('/','.')[1:]))
#         print("\tWritting file :: {}".format(output_file))
#         sys.stdout.flush()
#         Utility.write_to_file(output_file,'\n'.join(result))
#         # print("===============================================")
#         # sys.stdout.flush()


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    logging.info("Executing script as stand-alone.")

    parser = argparse.ArgumentParser()
    parser.add_argument("root_directory", 
        help="The directory that holds the github users' subdirectories")
    parser.add_argument("list_of_projects_to_analyze", 
        help="The file that holds the projects to analyze")
    parser.add_argument("maven_root_paths", 
        help="The file that holds the maven root paths as created by repository_path_retriever.py")
    parser.add_argument("output_directory", 
        help="The directory that holds a txt file with the dependency tree for each project")    
    args = parser.parse_args()

    output_directory = args.output_directory
    root_directory = args.root_directory
    project_list_path = args.list_of_projects_to_analyze
    maven_root_paths = args.maven_root_paths


    # execute(root_directory, output_directory, project_list_path, maven_root_paths)
    execute(root_directory, output_directory, project_list_path, maven_root_paths)
