import os
import itertools
import logging
import datetime

import '../maven' as mvn
import '../spotbugs' as sb
import '../sloc'


logging.basicConfig(level=logging.INFO)

currentDT = datetime.datetime.now()
print ("Started at :: {}".format(str(currentDT)))


def project_level_metrics(trees, spotbugs_xml):
    modules = [m.artifact for m in trees]
    dep_modules = [m.artifact for t in trees for m in t.deps if m.artifact not in modules]
    dep_modules = list(set(dep_modules)) # remove duplicates
    
    # Collect classes from user code
    project_classes = [c for m in modules for c in m.get_class_list()]
    
    # Collect classes from dependencies
    dep_classes = [c for m in dep_modules for c in m.get_class_list()]
    
    # Collect SLOC info
    classes_sloc = {}
    for m in (modules + dep_modules):
        classes_sloc.update(sloc.retrieve_SLOC(m.get_m2_path())[0])
            
    vdict = sb.collect_vulnerabilities(spotbugs_xml, {'uv': project_classes, 'dv': dep_classes})
    
    uv_classes = [sb.get_main_classname(b) for c in vdict['uv'] for r in c for b in r]
    uv_classes = list(set(uv_classes))
    
    dv_classes = [sb.get_main_classname(b) for c in vdict['dv'] for r in c for b in r]
    dv_classes = list(set(dv_classes))
    
    uv_count = [len(r) for c in vdict['uv'] for r in c]
    dv_count = [len(r) for c in vdict['dv'] for r in c]
    
    u_sloc = sum([int(classes_sloc[c]) for c in sloc.get_roots(project_classes)])
    d_sloc = sum([int(classes_sloc[c]) for c in sloc.get_roots(dep_classes)])
    
    uv_classes_sloc = sum([int(classes_sloc[c]) for c in sloc.get_roots(uv_classes)])
    dv_classes_sloc = sum([int(classes_sloc[c]) for c in sloc.get_roots(dv_classes)])
    
    return [
        len(project_classes),  # #u_classes   
        len(dep_classes),      # #d_classes 
        len(uv_classes),       # #uv_classes 
        len(dv_classes),       # #dv_classes 
        u_sloc,                # #u_sloc 
        d_sloc,                # #d_sloc  
        uv_classes_sloc ,      # #uv_classes_sloc 
        dv_classes_sloc        # #dv_classes_sloc 
    ] + uv_count + dv_count    # #uv_p1_r1 | #uv_p1_r2 ... | #dv_p3_r3 | #dv_p3_r4

    
def collect_sp_metrics(file_project_trees, output_file, append_to_file=True):

    trees = mvn.get_compiled_modules(file_project_trees)
    spotbugs_xml = f'{os.path.splitext(file_project_trees)[0]}.xml'
    proj_name = os.path.basename(os.path.splitext(file_project_trees)[0])
    
    if not trees:
        logging.warning(f'No modules to analyze: {file_project_trees}.')
        return
    
    if not os.path.exists(spotbugs_xml):
        logging.warning(f'SpotBugs XML not found: {spotbugs_xml}.')
        return
    
    metrics = project_level_metrics(trees, spotbugs_xml)
    
    if append_to_file:
        with open(output_file, 'a') as f:
            f.write(','.join([proj_name] + [str(m) for m in metrics]) + os.linesep)
    else:
        with open(output_file, 'w') as f:
            f.write(','.join([proj_name] + [str(m) for m in metrics]) + os.linesep)
            
    logging.debug(','.join([proj_name] + [str(m) for m in metrics]) + os.linesep)

            
path_to_data = os.path.abspath('../../data')
projects_dataset = os.path.abspath('../../projects-dataset.csv')
metrics_header = ['#u_classes', '#d_classes', '#uv_classes', '#dv_classes', 
           '#u_sloc', '#d_sloc', '#uv_classes_sloc', '#dv_classes_sloc', 
           '#uv_p1_r1', '#uv_p1_r2', '#uv_p1_r3', '#uv_p1_r4', 
           '#uv_p2_r1', '#uv_p2_r2', '#uv_p2_r3', '#uv_p2_r4', 
           '#uv_p3_r1', '#uv_p3_r2', '#uv_p3_r3', '#uv_p3_r4', 
           '#dv_p1_r1', '#dv_p1_r2', '#dv_p1_r3', '#dv_p1_r4', 
           '#dv_p2_r1', '#dv_p2_r2', '#dv_p2_r3', '#dv_p2_r4', 
           '#dv_p3_r1', '#dv_p3_r2', '#dv_p3_r3', '#dv_p3_r4', ]

with open(projects_dataset, 'w') as f:
    f.write(','.join((['project'] + metrics_header)) + os.linesep)
    
for f in projects_tress:
    filepath = path_to_data + os.path.sep + f
    collect_sp_metrics(filepath, projects_dataset)


currentDT = datetime.datetime.now()
print ("Finished at :: {}".format(str(currentDT)))