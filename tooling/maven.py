import os
import re
import logging
import zipfile

logger = logging.getLogger(__name__)

class MvnArtifact:
    """
    Class representing a fully defined maven artifact
    (e.g., <groupId>:<artifactId>:<type>:<version>[:<dep_type>])
    """
    __elem_re = re.compile(r'^(.+?):(.+?):(.+?):(.+?)((:)(.+))?$')
    def __init__(self, artifact_str):
        elems = MvnArtifact.__elem_re.match(artifact_str).groups()
        self.groupId =    elems[0]
        self.artifactId = elems[1]
        self.type =       elems[2]
        self.version =    elems[3]
        self.dep_type =   elems[6] # (e.g., compile, test, provided)
        
    def __str__(self):
        dt = '' if not 'dep_type' in self._dict_ else f':{self.dep_type}'
        return f'{self.groupId}:{self.artifactId}:{self.type}:{self.version}{dt}'
                
    def __eq__(self, other):
        if isinstance(other, MvnArtifact):
            return self.groupId == other.groupId and self.artifactId == other.artifactId \
               and self.type == other.type and self.version == other.version
        return NotImplemented

    def __hash__(self):
        d = self.__dict__
        del d['dep_type']
        return hash(tuple(sorted(d.items())))
    
    def get_class_list(self, m2_home=os.path.expanduser('~/.m2')):
        m2_home="/media/agkortzis/Data/m2"
        art_path = self.get_m2_path(m2_home)
        logger.debug("@@-zip file={}".format(art_path))
        container = zipfile.ZipFile(art_path)
        len_preffix =  len('WEB-INF/classes/') if art_path.endswith('.war') else 0

        if not art_path.endswith('.war') and not art_path.endswith('.jar'):
            logger.warning(f'Unsupported file type: {os.path.splitext(art_path)[1]}')
            return []

        return [i[len_preffix:-6].replace(os.path.sep,'.') for i in container.namelist() if i.endswith('.class')]

    
    def get_m2_path(self, m2_home=os.path.expanduser('~/.m2')):
        m2_home="/media/agkortzis/Data/m2"
        return os.sep.join([m2_home, 'repository', 
                        self.groupId.replace('.', os.sep), 
                        self.artifactId, 
                        self.version, 
                        f"{self.artifactId}-{self.version}.{self.type}"])
        

class ArtifactTree:
    def __init__(self, artifact):
        self.artifact = MvnArtifact(artifact)
        self.deps = []
        
    def __iter__(self):
        yield self
        for d in self.deps:
            for t in d.__iter__():
                yield t
        
    def print_tree(self, indent=0):
        print(' ' * indent, self.artifact)
        for i in self.deps:
            i.print_tree(indent+2)
            
    def filter_deps(self, filter):
        self.deps = [i for i in self.deps if filter(i)]
        for i in self.deps:
            i.filter_deps(filter)
            
    def missing_m2_pkgs(self, m2_home=os.path.expanduser('~/.m2')):
        m2_home="/media/agkortzis/Data/m2"
        return [p for p in self if not os.path.exists(p.artifact.get_m2_path(m2_home))]
        
    
    @staticmethod
    def parse_tree_str(tree_str):
        return ArtifactTree.__parse_tree([l[7:].rstrip() for l in tree_str.split('\n')], 0)
    
    @staticmethod
    def __parse_tree(tree_lst, i):
        root_level, root_artifact = ArtifactTree.__parse_item(tree_lst[i])
        t = ArtifactTree(root_artifact)
        while i+1 < len(tree_lst) and root_level < ArtifactTree.__parse_item(tree_lst[i+1])[0]:
            t.deps.append(ArtifactTree.__parse_tree(tree_lst, i+1))
            tree_lst.pop(i+1)

        return t
    
    @staticmethod
    def __parse_item(item):
        parts = re.match(r'([ \+\-\|\\]*)(.+)', item).groups()
        return int(len(parts[0])/3), parts[1]


    
def get_compiled_modules(project_trees_file):    
    with open(project_trees_file) as f:
        try:
            str_trees = split_trees([l.rstrip() for l in f.readlines()])
        except:
            logger.error(f'File is malformed: {project_trees_file}')
            return []

    trees = []
    for t in str_trees:
        t = ArtifactTree.parse_tree_str('\n'.join(t))
        if t.artifact.type in ['jar', 'war']:
            t.filter_deps(lambda d : d.artifact.dep_type == 'compile' and d.artifact.type in ['jar', 'war'])

            trees.append(t)


    return [t for t in trees if not t.missing_m2_pkgs()]

    
    
def filter_mvn_output(mvn_tree_output):
    re_tree_element = re.compile(r'^\[INFO\] (\||\\\-|\+\-| )*([a-zA-Z_$][a-zA-Z\d_\-$]*\.)*[a-zA-Z_$][a-zA-Z\d_\-$]*:.+?:([a-zA-Z]+?):.+?(:[a-zA-Z\-]+)?$')
                            
    with open(tree_file, 'r') as f:
        lines = f.readlines()
        
    tree_lines = [l.rstrip() for l in lines if re_tree_element.match(l)]
    
    return tree_lines
    
    
    
def split_trees(tree_lines):
    re_artifact = re.compile(r'^\[INFO\] ([a-zA-Z_$][a-zA-Z\d_\-$]*\.)*[a-zA-Z_$][a-zA-Z\d_\-$]*:.+?:([a-zA-Z]+?):.+$')
    
    trees = []
    tree = None
    for l in tree_lines:
        if re_artifact.match(l):
            if tree:
                trees.append([tree['root']] + tree['deps'])
            tree = {'root': l, 'deps': []}
        else:
            tree['deps'].append(l)
    trees.append([tree['root']] + tree['deps'])

    return trees


