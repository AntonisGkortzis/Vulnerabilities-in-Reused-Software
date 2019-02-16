import os
from os import listdir
from os.path import isfile, join
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("repo_list", 
    help="The file the keeps the building repositories")
parser.add_argument("files_to_clean", 
    help="The file the keeps the building repositories")
args = parser.parse_args()


def move_file(filepath):
	exts = ['.xml', '.log', '.trees']
	for extension in exts:
		full_filepath = "{}{}".format(filepath, extension)
		try:
		    new_path = os.path.join("failing_projects",format(full_filepath))
		    print("moving {} to: \n\t{}".format(full_filepath,new_path))
		    os.rename(full_filepath, new_path)
		except IOError as e:
			print("## Error ##\n{}".format(e))



def clean_files(file_list):
	clean_list = set()
	for file in file_list:
		file = file.replace('.xml', '').replace('.log', '').replace('.trees', '')
		# print("Adding {}".format(file))
		clean_list.add(file)

	return clean_list

repos = []
with open(args.repo_list) as file:
    for line in file:
        line = line.strip().replace('/','.') #preprocess line
        repos.append(line)

dir_path = args.files_to_clean
onlyfiles = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
clean_list = clean_files(onlyfiles)

for fileset in clean_list:
	if fileset not in repos:
		# print(fileset)
		move_file(fileset)


# print(repos)
# print(onlyfiles)
# print(clean_list)