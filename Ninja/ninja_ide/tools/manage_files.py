import os
import re

import loader

supported_extensions = ('.py', '.html', '.jpg', '.png', '.ui', '.css', '.json')


def create_folder(folderName):
    os.mkdir(folderName)
    create_init_file(folderName)


def create_init_file(folderName):
    name = os.path.join(folderName, '__init__.py')
    f = open(name, 'w')
    f.flush()
    f.close()


def create_init_file_complete(folderName):
    patDef = re.compile('^def .+')
    patClass = re.compile('^class .+')
    patExt = re.compile('.+\\.py')
    files = os.listdir(folderName)
    files = filter(patExt.match, files)
    files.sort()
    imports = []
    for f in files:
        read = open(os.path.join(folderName, f), 'r')
        imp = [re.split('\\s|\\(', x)[1] for x in read.readlines() if patDef.match(x) or patClass.match(x)]
        imports += ['from ' + f[:-3] + ' import ' + i for i in imp]
    name = os.path.join(folderName, '__init__.py')
    fi = open(name, 'w')
    for impo in imports:
        fi.write(impo + '\n')
    fi.flush()
    fi.close()


def folder_exists(folderName):
    return os.path.isdir(folderName)


def file_exists(path, fileName=''):
    if fileName != '':
        path = os.path.join(path, fileName)
    return os.path.isfile(path)


def read_file_content(fileName):
    f = open(fileName, 'rU')
    content = f.readlines()
    f.close()
    content = ''.join(content)
    return content


def get_basename(fileName):
    return os.path.basename(fileName)


def get_folder(fileName):
    return os.path.dirname(fileName)


def store_file_content(fileName, content):
    if fileName == '':
        raise Exception()
    ext = (os.path.splitext(fileName)[-1])[1:]
    exts = loader.extensions.keys()
    if ext == '':
        fileName += '.py'
    f = open(fileName, 'w')
    f.write(content)
    f.flush()
    f.close()
    return fileName


def open_project(path):
    d = {}
    for root, dirs, files in os.walk(path):
        d[root] = [[f for f in files
                if (os.path.splitext(f.lower())[-1]) in supported_extensions],
                dirs]
    return d


def open_project_with_extensions(path, extensions):
    d = {}
    for root, dirs, files in os.walk(path):
        d[root] = [[f for f in files
                if (os.path.splitext(f.lower())[-1]) in extensions],
                dirs]
    return d


def delete_file(path, fileName):
    os.remove(os.path.join(path, fileName))


def get_file_extension(fileName):
    return (os.path.splitext(fileName.lower())[-1])


def get_module_name(fileName):
    module = os.path.basename(fileName)
    return (os.path.splitext(module)[0])


def convert_to_relative(basePath, fileName):
    if fileName.startswith(basePath):
        fileName = fileName.replace(basePath, '')
        if fileName.startswith(os.path.sep):
            fileName = fileName[1:]
        return fileName


def create_abs_path(basePath, fileName):
    return os.path.join(basePath, fileName)


def belongs_to_folder(path, fileName):
    return fileName.startswith(path)


def get_last_modification(fileName):
    return os.path.getmtime(fileName)


def has_write_prmission(fileName):
    return os.access(fileName, os.W_OK)


def check_for_external_modification(fileName, old_mtime):
    new_modification_time = get_last_modification(fileName)
    #check the file mtime attribute calling os.stat()
    if new_modification_time > old_mtime:
        return True
    return  False
