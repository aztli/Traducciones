from __future__ import absolute_import

import sys
import os

from ninja_ide import gui
from ninja_ide import resources

from ninja_ide.tools import loader

from ninja_ide.core import pluginmanager
from ninja_ide.core.plugin_access import Editor
from ninja_ide.core.plugin_access import Tabs
from ninja_ide.core.plugin_access import Projects

from ninja_ide.extras.plugins import TextLanguage
from ninja_ide.extras.plugins import TextProjectType

plugins = []


def run_ninja():
    gui.setupQt()


def install_functions(plugins):
    for plug in plugins:
        try:
            instance = plug[0]
            lang = plug[1].get('lang', False)
            type_ = plug[1].get('project-type', False)
            connect = plug[1].get('connect', False)
            if connect:
                if 'returnKeyEvent' in connect:
                    pluginmanager.add_return_key(instance)
                if 'anyKeyEvent' in connect:
                    pluginmanager.add_any_key(instance)
                if 'run-code' in connect and lang:
                    pluginmanager.add_run_file(instance, lang)
                if 'run-program' in connect and (lang or type_):
                    pluginmanager.add_run_program(instance, lang, type_)
            if type_:
                pluginmanager.add_project_type(type_, instance)
            if lang and lang not in TextLanguage.langs:
                TextLanguage.langs.append(lang)
            if type_ and type_ not in TextProjectType.types:
                TextProjectType.types.append(type_)
        except Exception, reason:
            print 'install_functions'
            print 'Plugin:', plug[1].get('module', str(instance)), instance._name, 'could not be loaded.'
            print reason


def install_gui(plugins, ide):
    value = False
    for plug in plugins:
        try:
            instance = plug[0]
            lang = plug[1].get('lang', False)
            type_ = plug[1].get('project-type', False)
            if plug[1].get('menu-app', False):
                pluginmanager.add_menu_app(ide, instance)
                value = True
            if plug[1].get('toolbar', False):
                pluginmanager.add_toolbar_item(plug[1]['toolbar'], instance, ide)
                value = True
            if plug[1].get('display', False):
                pluginmanager.add_display(plug[1]['display'], instance, ide)
                value = True
            if plug[1].get('properties', False):
                pluginmanager.add_properties_panel(plug[1]['properties'], instance, ide)
                value = True
            if plug[1].get('menu-project', False) and (lang or type_):
                pluginmanager.add_menu_project(instance, lang, ide, type_)
                value = True
            if plug[1].get('menu-editor', False) and lang:
                pluginmanager.add_menu_editor(instance, lang)
                value = True
        except Exception, reason:
            print 'Plugin:', plug[1].get('module', str(instance)), instance._name, 'could not be loaded.'
            print reason
    return value


def load_plugins(ide):
    TextLanguage.langs = loader.extensions.keys()
    plugins = pluginmanager.load_plugins()
    install_functions(plugins)
    install_gui(plugins, ide)


def load_installed_plugin(ide, plug):
    plugin = pluginmanager.load_installed_plugin(plug)
    install_functions(plugin)
    val = install_gui(plugin, ide)
    return val


def register_plugin_access(get_editor, get_text, editor_path, add_new_editor,
            add_tab, save_file, open_document, open_image, project_path, tree_projects):

    Editor._Editor__get_editor = get_editor
    Editor.get_text = get_text
    Editor.editor_path = editor_path
    Tabs.add_new_editor = add_new_editor
    Tabs.add_tab = add_tab
    Tabs.save_file = save_file
    Tabs.open_document = open_document
    Tabs.open_image = open_image
    Projects.selected_project_path = project_path
    Projects.tree_projects = tree_projects


def available_plugins():
    return pluginmanager.download_descriptor()


def local_plugins():
    return pluginmanager.read_descriptor()


def download_plugin(file_):
    pluginmanager.download_plugin(file_)


def update_local_plugin_descriptor(plugins):
    pluginmanager.update_local_descriptor(plugins)


def uninstall_plugin(plugin):
    pluginmanager.uninstall_plugin(plugin)
