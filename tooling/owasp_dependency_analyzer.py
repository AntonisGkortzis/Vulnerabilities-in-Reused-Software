import argparse
import logging
import os

from utility import Utility


def detect_jar_files(directory):
    """
    Detects and stores all jar files
    
    Parameters
    ----------
    directory : str
        The path of the directory where jars are stored

    Returns
    -------
    list
        a list of jar files
    """
    logging.info("Scanning for jar files in {}".format(directory))
    jar_list = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            # if file.endswith("pom.xml") or file.endswith("build.gradle"):
            if file.endswith(".jar"):
                fullFilePath = os.path.join(root,file)
                jar_list.append(fullFilePath)
                logging.debug("@detect_jar_files -> Appenidng to list : {}".format(fullFilePath))


    logging.info("Detected {} jar files".format(len(jar_list)))

    return jar_list


def generate_project_name(jar_path, directory):
    project_name = jar_path[len(directory)+1:] # remove the root path name
    return project_name.replace('/',"_")


def run_owasp_depepndency_checker(directory, owasp_executable, jar_list, output_dir, report_format="JSON"):
    """
    Runs owasp dependency-checker for each jar in the jar_list.
    Stores the report in the defined output directory 
    
    Parameters
    ----------
    directory: str
        The directory that stores the jar files

    owasp_executable : str
        The path of the owasp dependency-checker .sh file

    jar_list : list
        The list that contains the jars to be analysed

    output_dir : str
        The directory where the report will be stored

    report_format : str (optional)
        Defines the output format for the report

    """

    logging.info("Running owasp dependency-checker on jar list")

    index = 1
    jar_list_size = len(jar_list)

    for jar_file in jar_list:
        logging.info("{}/{}. Analyzing {}".format(index, jar_list_size, jar_file))
        index += 1
        project = generate_project_name(jar_file, directory) # get the project name
        output_file_name = os.path.join(output_dir, project)

        if os.path.isdir(output_file_name): 
            logging.info("Skipping analysis, owasp report already exists in {}".format(output_file_name))
            continue

        command = "{} -n --project '{}' --scan '{}' --out '{}' --format '{}'".format(owasp_executable, project, jar_file, output_file_name, report_format)
        logging.debug("@run_owasp_depepndency_checker --> command = \n {}".format(command))
        output, error = Utility.execute_process(command)


def execute(directory, owasp_executable, jar_list_file, output_dir, report_format):
    if not jar_list_file:
        logging.info("Jar list does not exist. Running detection on directory {}....".format(directory))
        jar_list = detect_jar_files(directory)
        logging.info("Detected {} jar files.".format(len(jar_list)))
    else:
        jar_list = Utility.read_file(jar_list_file)
        logging.info("Jar list contains {} jar files.".format(len(jar_list)))
        pass

    run_owasp_depepndency_checker(directory, owasp_executable, jar_list, output_dir, report_format)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    logging.info("Executing script as stand-alone.")

    parser = argparse.ArgumentParser()
    parser.add_argument("root_directory", 
        help="The directory that holds the jar files")
    parser.add_argument("owasp_executable", 
        help="The .sh owasp executable's path")
    parser.add_argument("output_dir", 
        help="The directory that will store the owasp reports")
    parser.add_argument('--jar_list','-l', 
        help='Input jar list.')
    parser.add_argument("-f", "--format", 
        help="The type of the owasp output report (JSON, XML, HTML). The default is JSON.")
    args = parser.parse_args()

    root_directory = args.root_directory
    owasp_executable = args.owasp_executable
    output_dir = args.output_dir
    if args.format:
        report_format = args.format
    else:
        report_format = "JSON"
    jar_list = args.jar_list
    
    execute(root_directory, owasp_executable, jar_list, output_dir, report_format)