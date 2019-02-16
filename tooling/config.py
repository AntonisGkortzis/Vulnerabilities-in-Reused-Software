import os
import warnings

STUDY_HOME  = '/home/vagrant/root_vm/ICSR19/analysis'

class Spotbugs:
    VERSION  = '3.1.11'
    HOME = os.path.join(STUDY_HOME, 'tooling', 'vendor', f'spotbugs-{VERSION}')
    BIN  = os.path.join(HOME, 'bin', 'spotbugs2')
    MAX_HEAP = '8192'
    EXCL_FILTER = os.path.join(STUDY_HOME, 'tooling', 'spotbugs_filter.xml')

#
# Validation of configs
#

def __validate_config():

    my_env = os.environ.copy()

    if not my_env['JAVA_HOME']:
        warnings.warn('Java was not found. Did you configure your environment properly? Please check the main REAMDE.')
        
    if not my_env['JAVA_HOME']:
        warnings.warn('Maven was not found. Did you configure your environment properly? Please check the main REAMDE.')

    if not os.path.exists(Spotbugs.BIN):
        warnings.warn(f'Spotbugs not found at "{Spotbugs.BIN}". Did you configure your environment properly? Please check the main REAMDE.')


__validate_config()        
