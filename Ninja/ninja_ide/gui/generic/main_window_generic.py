from __future__ import absolute_import

import os

from ninja_ide.tools import manage_files

class MainWindowGeneric(object):

    runFile = {}
    runProgram = {}

    def __init__(self):
        self.containerIsVisible = True

    def read_file_content(self, fileName):
        return manage_files.read_file_content(fileName)

    def get_file_name(self, fileName):
        return os.path.basename(fileName)

    def get_file_extension(self, fileName):
        return manage_files.get_file_extension(fileName)[1:]

    def store_file_content(self, fileName, content):
        return manage_files.store_file_content(fileName, content)

    def open_project(self, path):
        return manage_files.open_project(path)

    def open_project_with_extensions(self, path, extensions):
        return manage_files.open_project_with_extensions(path, extensions)

    def execute_program(self, path, ext, type_):
        if self.runProgram.get(type_, False):
            instance = self.runProgram[type_]
            instance.executeProgram()
        elif self.runProgram.get(ext, False):
            instance = self.runProgram[ext]
            instance.executeProgram()

    def execute_file(self, path, ext):
        if self.runFile.get(ext, False):
            instance = self.runFile[ext]
            instance.executeFile()
