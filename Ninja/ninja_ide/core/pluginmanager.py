from __future__ import absolute_import

import os
import sys
import urllib
import zipfile
from copy import copy
try:
    import json
except ImportError:
    import simplejson as json

from ninja_ide import resources

from ninja_ide.core.plugin_access import PluginAccess

from ninja_ide.gui.generic.main_panel import EditorGeneric
from ninja_ide.gui.generic import MainWindowGeneric
from ninja_ide.gui.generic.wizards import ProjectWizard


def load_module(plug, folder):
    old_syspath = copy(sys.path)
    try:
        sys.path += [folder]
        module = __import__(plug, globals(), locals(), ['plugin'])
        access = PluginAccess()
        instance = module.Plugin(access)
        return instance
    except(ImportError, AttributeError), reason:
        print 'error loading "%s": %s' % (plug, reason)
    finally:
        sys.path = old_syspath
    return None


def load_plugins():
    if not os.path.isdir(resources.plugins):
        os.makedirs(resources.plugins)
    plugins = []
    plugs = os.listdir(resources.plugins)
    plugs = [p for p in plugs if p.endswith('.json')]

    for plug in plugs:
        structure = None
        fileName = os.path.join(resources.plugins, plug)
        read = open(fileName, 'r')
        structure = json.load(read)
        read.close()
        module = structure.get('module', None)
        if module is not None:
            instance = load_module(module, resources.plugins)
            plugins.append([instance, structure])
    return plugins


def load_installed_plugin(plug):
    fileName = resources.createpath(resources.plugins, plug[0] + '.json')
    read = open(fileName, 'r')
    structure = json.load(read)
    read.close()
    module = structure.get('module', None)
    if module is not None:
        instance = load_module(module, resources.plugins)
        return [[instance, structure]]
    else:
        return []


def add_return_key(instance):
    EditorGeneric.returnKeyEvent += [instance]


def add_any_key(instance):
    EditorGeneric.anyKeyEvent += [instance]


def add_run_file(instance, lang):
    MainWindowGeneric.runFile[lang] = instance


def add_run_program(instance, lang, type_):
    if lang:
        MainWindowGeneric.runProgram[lang] = instance
    if type_:
        MainWindowGeneric.runProgram[type_] = instance


def add_project_type(type_, instance):
    ProjectWizard.types[type_] = instance


def add_menu_app(ide, instance):
    newMenu = instance.addMenuApp()
    ide.pluginsMenu.addMenu(newMenu)


def add_toolbar_item(plug, instance, ide):
    icon = resources.createpath(resources.plugins, plug.get('icon', ''))
    ide.add_toolbar_item(instance, plug.get('name', ''), icon)


def add_display(plug, instance, ide):
    icon = resources.createpath(resources.plugins, plug)
    ide.main.container.add_to_stack(instance.stackWidget(), icon)


def add_properties_panel(plug, instance, ide):
    icon = resources.createpath(resources.plugins, plug.get('icon', ''))
    name = plug.get('name', '')
    widget = instance.propertiesWidget()
    ide.main._properties.add_tab(widget, name, icon)


def add_menu_project(instance, lang, ide, type_):
    menu = instance.menuProject()
    if type_:
        ide.main._properties.install_project_menu(menu, type_)
    elif lang:
        ide.main._properties.install_project_menu(menu, lang)


def add_menu_editor(instance, lang):
    menu = instance.menuEditor()
    if lang not in EditorGeneric.extraMenus:
        EditorGeneric.extraMenus[lang] = [menu]
    else:
        EditorGeneric.extraMenus[lang] += [menu]


def download_descriptor():
    descriptor = urllib.urlopen('http://plugins.ninja-ide.googlecode.com/hg/descriptor.json')
    plugins = json.load(descriptor)
    return plugins


def read_descriptor():
    if not os.path.isfile(resources.descriptor):
        return {}
    descriptor = open(resources.descriptor, 'r')
    plugins = json.load(descriptor)
    descriptor.close()
    return plugins


def download_plugin(file_):
    fileName = resources.createpath(resources.plugins, os.path.basename(file_))
    content = urllib.urlopen(file_)
    f = open(fileName, 'wb')
    f.write(content.read())
    f.close()
    zipFile = zipfile.ZipFile(fileName, 'r')
    zipFile.extractall(resources.plugins)
    zipFile.close()
    os.remove(fileName)


def update_local_descriptor(plugins):
    structure = {}
    if os.path.isfile(resources.descriptor):
        read = open(resources.descriptor, 'r')
        structure = json.load(read)
        read.close()
    for plug in plugins:
        structure[plug[0]] = [plug[1], plug[2], plug[3]]
    descriptor = open(resources.descriptor, 'w')
    json.dump(structure, descriptor, indent=2)


def uninstall_plugin(plug):
    fileName = os.path.basename(plug[3])
    fileName = os.path.splitext(fileName)[0]
    fileName = resources.createpath(resources.plugins, fileName + '.json')
    descriptor = open(fileName, 'r')
    plugin = json.load(descriptor)
    descriptor.close()
    module = plugin.get('module', False)
    if module:
        pluginDir = resources.createpath(resources.plugins, module)
        folders = [pluginDir]
        for root, dirs, files in os.walk(pluginDir):
            pluginFiles = [resources.createpath(root, f) for f in files]
            map(os.remove, pluginFiles)
            folders += [resources.createpath(root, d) for d in dirs]
        folders.reverse()
        for f in folders:
            if os.path.isdir(f):
                os.removedirs(f)
        os.remove(fileName)
    structure = {}
    if os.path.isfile(resources.descriptor):
        read = open(resources.descriptor, 'r')
        structure = json.load(read)
        read.close()
    structure.pop(module)
    descriptor = open(resources.descriptor, 'w')
    json.dump(structure, descriptor, indent=2)
