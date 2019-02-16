from os import listdir
from os.path import isfile, join, basename, splitext, exists
import argparse
import re

from utility import Utility
import maven as mvn

parser = argparse.ArgumentParser()

parser.add_argument("directory", 
        help="The directory that holds a txt file with the dependency tree for each project") 
args = parser.parse_args()


def get_filelist(root_dir):
    tree_list = []
    for file in listdir(root_dir):
        if file.endswith(".trees"):
            # print(file)
            full_filepath = join(root_dir, file)
            tree_list.append(full_filepath)

    return tree_list


def get_unique_deps_per_project(tree_lines):
    unique_deps = set()

    regex = '(\[INFO\])( *(\+|\-)* )?(.*) '
    for line in tree_lines:
        clean_line = re.sub(regex, '', line)
        if clean_line.endswith(":compile"):
            unique_deps.add(clean_line)
        # print(clean_line)

    # print(unique_deps)
    return unique_deps


root_dir = args.directory
tree_list = get_filelist(root_dir)

frequencies = {}

for tree_file in tree_list:
    tree_lines = Utility.read_file(tree_file)
    unique_deps = get_unique_deps_per_project(tree_lines)

    for dependency in unique_deps:
        frequencies[dependency] = frequencies.get(dependency, 0) + 1
        # if dependency in frequencies:
        #     frequencies[dependency] += 1
        # else:
        #     frequencies[dependency] = 1

sorted_dic = sorted(frequencies.items(), key=lambda x: x[1], reverse=False)
# first10pairs = {k: sorted_dic[k] for k in list(sorted_dic)[:10]}

print(sorted_dic)