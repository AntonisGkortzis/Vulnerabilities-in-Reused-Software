import os
import re
import csv
import subprocess
import logging

logger = logging.getLogger(__name__)


def execute_process(command):
    command = command.replace("\\","/")
    
    try:
        process = subprocess.Popen(
            command, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        (out, err) = [x.decode() for x in process.communicate()]

    except Exception as e:
        logger.error('''## ERROR while executing process {}
            Check log file for further details'''
            .format(command))
    # print(err) # DEBUG
    return out, err


def retrieve_SLOC(jar_path, csv_path=None, overwrite=False):
    if not csv_path:
        csv_path = f'{os.path.splitext(jar_path)[0]}.sloc.csv'
    
    command = "java -jar metrics_calculator.jar {} {}".format(jar_path, csv_path)

    if not os.path.exists(csv_path) or overwrite:
        logger.info(f'Extracting sloc: {jar_path}')
        result = execute_process(command)
        logger.debug(result)

    if not os.path.exists(csv_path):
        logger.error(f'SLOC file not found: {csv_path}')
        return None
    
    logger.info(f'Reading sloc information: {csv_path}')
    
    sloc_per_class = {}
    sloc_sum = 0
    with open(csv_path, newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=';')
        for row in csv_reader:
            # row = row.split(';')
            logger.debug(f'{row[15]} :: {row[0]}')
            sloc_per_class[row[0]] = row[15]
            sloc_sum = sloc_sum + int(row[15])

    return sloc_per_class, sloc_sum


def get_roots(classes):
    main_class_re = r'(.+?)\$.+$'
    if isinstance(classes, str):
       classes = [classes]
    return list(set([re.sub(main_class_re, r'\1', c) for c in classes]))


def _test():
    jar_path = "./metrics_calculator.jar"
    # jar_path = "/home/agkortzis/.m2/repository/asm/asm/.33.1/asm-3.3.1.jar"
    sloc_per_class, sloc = retrieve_SLOC(jar_path)
    print(sloc_per_class)
    print("Total sloc :: {}".format(sloc))

if __name__== "__main__":
    _test()