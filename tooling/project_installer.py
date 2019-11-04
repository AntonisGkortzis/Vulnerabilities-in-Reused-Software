import argparse
import logging
import os
import sys

from utility import Utility


def parse_maven_build_output(output):
    if "BUILD SUCCESS" in output:
        return True
    else:
        return False


def parse_gradle_build_output(output):
    if "BUILD SUCCESSFUL" in output:
        return True
    else:
        return False


def get_repositories(repository_list):
    with open(repository_list) as f:
        lines = f.read().splitlines()

    repositories = {}
    for line in lines:
        fields = line.split(';')
        repositories[fields[0]] = fields[1]

    logging.info("Found {} repositories in list {}".format(len(repositories), repository_list))
    logging.debug("@get_repositories: repository list with root paths: \n{}".format(repositories))
    return repositories


def has_build_path(path):
    if path in ['FailedToDetect','RequiresManualResolution']:
        logging.debug("@has_build_path: Cannot build repository with reason = {}".format(has_build_path))
        return False
    else:
        return True


def get_maven_command(repository_root_path):
    if os.path.isfile(os.path.join(repository_root_path, 'mvnw')):
        command = os.path.join(repository_root_path, 'mvnw')
    else:
        command = 'mvn'

    return command


def build_maven_project(build_configuration_file_path, clean_repository_before_install, force_version=False):
    logging.debug("\tBuilding Maven project")

    repository_root_path = get_root_directory(build_configuration_file_path)
    
    command = get_maven_command(repository_root_path) # check for maven wrapper 
    if clean_repository_before_install: # clean before installing?
        command += ' clean'
    command += ' install -B -T 6 -Dmaven.test.skip=true -Dmaven.javadoc.skip=true -Dgpg.skip -Dcheckstyle.skip -Dfindbugs.skip=true -Dspotbugs.skip=true -Dpmd.skip=true'
    if force_version:
        command += " -Dmaven.compiler.source=1.6 -Dmaven.compiler.target=1.6"

    logging.debug("@build_maven_project: build command = {}".format(command))

    os.chdir(repository_root_path)
    output, error = Utility.execute_process(command)
    logging.debug(error)
    build_result = parse_maven_build_output(output)

    return build_result


def get_gradle_command(repository_root_path):
    if os.path.isfile(os.path.join(repository_root_path, 'gradlew')):
        command = os.path.join(repository_root_path, 'gradlew')
    else:
        command = 'gradle'

    return command


def get_root_directory(build_configuration_file_path):
    root_directory = os.path.dirname(os.path.abspath(build_configuration_file_path))
    logging.debug("@get_root_directory: root directory = {}".format(root_directory))

    return root_directory


def build_gradle_project(build_configuration_file_path, clean_repository_before_install):
    logging.debug("\tBuilding Gradle project")
    repository_root_path = get_root_directory(build_configuration_file_path)
    
    command = get_gradle_command(repository_root_path) # check for maven wrapper 
    if clean_repository_before_install: # clean before installing?
        command += ' clean'
    # command += ' build install --no-daemon -x test -x javadoc' # TODO: skip gpg signing 
    command += ' build install --no-daemon -x test' # TODO: skip gpg signing 
    logging.debug("@build_gradle_project: build command = {}".format(command))

    os.chdir(repository_root_path)
    output, error = Utility.execute_process(command)
    # logging.debug(error)

    write_error_log(build_configuration_file_path, output, error) # DEBUG
    build_result = parse_maven_build_output(output)

    return build_result


def write_error_log(repository_path, output, error):
    error_log = os.path.join(os.path.expanduser('~'), "error_log.log")
    logging.debug("@write_error_log: error logged at {}".format(error_log))
    with open(error_log, "a") as myfile:
        output_message = '''
        =================================
        Repository :: {}
        =================================
        ##### output #####:
        {}

        ##### error #####:
        {}

        '''.format(repository_path, output, error)
        myfile.write(output_message)


def get_build_type(build_configuration_file_path):
    if build_configuration_file_path.endswith("/pom.xml"):
        return "maven"
    elif build_configuration_file_path.endswith("/build.gradle"):
        return "gradle"
    else:
        return "unknown"


def build_repository(build_configuration_file_path, clean_repository_before_install, skip_maven, skip_gradle, force_version=False):
    build_type = get_build_type(build_configuration_file_path)
    build_result = False
    # FIXME: simplify the following statement
    if build_type is "maven":
        if not skip_maven:
            build_result = build_maven_project(build_configuration_file_path, clean_repository_before_install, force_version)
            logging.info("\tBuild status: {}".format(build_result))
        else:
            logging.info("\tSkipping Maven analysis.")
    elif build_type is "gradle":
        if not skip_gradle:
            build_result = build_gradle_project(build_configuration_file_path, clean_repository_before_install)
            logging.info("\tBuild status: {}".format(build_result))
        else:
            logging.info("\tSkipping Gradle analysis.")
    else:
        logging.warning("Invalid or unknown build file :: {}".format(build_configuration_file_path))

    return build_result


def write_result_to_file(build_list_file, build_result, repository):
    if not build_result:
        logging.debug("@write_result_to_file: repository [{}] failed to build with result [{}]. Not added to output file.".format(build_result, repository))
        return

    with open(build_list_file, "a") as myfile:
        myfile.write("{}\n".format(repository))


def get_built_repositories(build_list_file):
    with open(build_list_file) as f:
        lines = f.read().splitlines()

    logging.info("Found {} already built repositories.".format(len(lines)))
    return lines


def install_all_repositories(root_directory, repository_list, build_list_file, clean_repository_before_install=False, skip_maven=False, skip_gradle=False, force_version=False):
    # 1. get repositories and root paths
    repositories_with_paths = get_repositories(repository_list)
    built_repositories = get_built_repositories(build_list_file)
    # 2. for each legit execute Maven OR Gradle install
    for index, repository in enumerate(repositories_with_paths):
        logging.info("{}/{}. Analysing {}:{}".format(index+1, len(repositories_with_paths), repository, repositories_with_paths[repository]))
        if not has_build_path(repositories_with_paths[repository]): # skip those without path
            continue

        if repository in built_repositories: # skip already built
            logging.info("\tRepository exists in already built repositories. Skipping analysis")
            continue

        build_configuration_file_path = os.path.join(root_directory, repositories_with_paths[repository])
        logging.debug("@install_all_repositories: created build configuration file = {}".format(build_configuration_file_path))

        build_result = build_repository(build_configuration_file_path, clean_repository_before_install, skip_maven, skip_gradle, force_version)
        
        write_result_to_file(build_list_file, build_result, repository)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    logging.info("Executing script as stand-alone.")

    parser = argparse.ArgumentParser()
    parser.add_argument("root_directory", 
        help="The directory that holds the github users' subdirectories")
    parser.add_argument("repository_list", 
        help="The file that holds the repositories and their root paths")
    parser.add_argument("build_list", 
        help="A file that holds the list of the succesfully built repositories")
    parser.add_argument('--clean','-c', 
        help='Clean a maven repository before building it',
        action='store_true')
    parser.add_argument('--skip_maven','-sm', 
        help='Skips Maven repositories from the analysis',
        action='store_true')
    parser.add_argument('--skip_gradle','-sg', 
        help='Skips Gradle repositories from the analysis',
        action='store_true')
    parser.add_argument('--force_version','-f', 
        help='Forces build command to run with version 1.6',
        action='store_true')
    args = parser.parse_args()

    root_directory = args.root_directory
    repository_list = args.repository_list
    build_list_file = args.build_list
    clean_repository_before_install = args.clean
    skip_maven = args.skip_maven
    skip_gradle = args.skip_gradle
    force_version = args.force_version


    logging.info("Skipping Maven repositories set to: {}".format(skip_maven))
    logging.info("Skipping Gradle repositories set to: {}".format(skip_gradle))
    install_all_repositories(root_directory, repository_list, build_list_file, clean_repository_before_install, skip_maven, skip_gradle, force_version)
