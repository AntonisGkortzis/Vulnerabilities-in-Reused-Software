import os
import subprocess
import config
import logging
import xmltodict

def analyze_project(pkgs, output_file=None, overwrite=False):
    logger = logging.getLogger(__name__)

    if not output_file:
        output_file = f'{os.path.splitext(pkgs[0])[0]}.xml'
    log_file = f'{os.path.splitext(output_file)[0]}.log'
    
    if os.path.exists(output_file) and not overwrite:
        logger.info(f'Already analyzed. Skipping {output_file}.')
        return

    sp_cmd = [config.Spotbugs.BIN,
             '-maxHeap', config.Spotbugs.MAX_HEAP, 
             '-textui', 
             '-effort:max', 
             '-low', 
             '-exclude', config.Spotbugs.EXCL_FILTER, 
             '-xml', 
             '-output', output_file]

    sp_cmd.extend(pkgs)
    
    logger.debug(sp_cmd)
    logger.info(f'Analyzing {output_file}')

    lf = open(log_file,"wb")
    p = subprocess.run(sp_cmd, stdout=lf, stderr=lf, timeout=None)

    if p.returncode:
        logger.error(f'Failed analysis of {output_file}')

    logger.info(f"Saving output to {output_file}")
    logger.info(f"Saving log to {log_file}")

    
def collect_vulnerabilities(xmlfile, class_dict):
    logger = logging.getLogger(__name__)
    bug_count = {}
    
    for k in class_dict.keys():
        bug_count[k] = _get_empty_structure()
    try:
        with open(xmlfile) as fd:
            doc = xmltodict.parse(fd.read())
    except Exception as e:
        logger.error("Failed to parse xml :: {}".format(xmlfile))
        raise e
    
    
    blst = doc['BugCollection'].get('BugInstance')
    
    # No BugInstances
    if not doc['BugCollection'].get('BugInstance'):
        return bug_count
    
    # Has only one BugInstance
    if '@type' in doc['BugCollection']['BugInstance']:
        blst = [doc['BugCollection']['BugInstance']]
    
    for b in blst:
        confidence_idx = int(b['@priority']) - 1
        rank_idx = min(int(int(b['@rank'])/5), 3) # 1-4, 5-9, 10-14, 15-20
        main_class = get_main_classname(b)
        
        for k in class_dict.keys():
            if main_class in class_dict[k]:
                bug_count[k][confidence_idx][rank_idx].append(b)
                break
    
    return bug_count


def get_main_classname(bug_instance):
    if isinstance(bug_instance['Class'], list):
        return bug_instance['Class'][0]['@classname'] 
    else:
        return bug_instance['Class']['@classname']
        

def _get_empty_structure():
    return [
        [ [], [], [], [] ],
        [ [], [], [], [] ],
        [ [], [], [], [] ]
    ]