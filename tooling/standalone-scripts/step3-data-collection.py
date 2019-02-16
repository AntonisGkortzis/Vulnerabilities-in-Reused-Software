import os
import logging
import datetime

import '../maven'
import '../spotbugs'


logging.basicConfig(level=logging.INFO)

currentDT = datetime.datetime.now()
print ("Started at :: {}".format(str(currentDT)))


def run_spotbugs(file_project_trees, output_file):

    trees = maven.get_compiled_modules(file_project_trees)
    
    if not trees:
        logging.info(f'Not modules to analyze: {file_project_trees}.')
        return

    pkg_paths = []
    for t in trees:
        pkg_paths.extend([a.artifact.get_m2_path() for a in t])
        
    pkg_paths = list(set(pkg_paths))
    spotbugs.analyze_project(pkg_paths, output_file)


path_to_data = os.path.abspath('../../data')

projects_tress = [f for f in os.listdir(path_to_data) if f.endswith('.trees')]

for f in projects_tress:
    filepath = path_to_data + os.path.sep + f
    output_file = f'{os.path.splitext(filepath)[0]}.xml'
    run_spotbugs(filepath, output_file)

    
currentDT = datetime.datetime.now()
print ("Finished at :: {}".format(str(currentDT)))