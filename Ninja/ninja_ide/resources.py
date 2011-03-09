#-*-coding:utf-8-*-

import os
import sys

#===============================================================================
# OS DETECTOR
#===============================================================================

OS_VERSION = sys.version
OS_KEY = "Cmd" if "Apple" in OS_VERSION else "Ctrl"


#===============================================================================
# PATHS
#===============================================================================

try:
    # ...works on at least windows and linux.
    # In windows it points to the user"s folder
    #  (the one directly under Documents and Settings, not My Documents)


    # In windows, you can choose to care about local versus roaming profiles.
    # You can fetch the current user"s through PyWin32.
    #
    # For example, to ask for the roaming "Application Data" directory:
    #  (CSIDL_APPDATA asks for the roaming, CSIDL_LOCAL_APPDATA for the local one)
    from win32com.shell import shellcon, shell
    HOME_PATH = shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0)

except ImportError:
   # quick semi-nasty fallback for non-windows/win32com case
    HOME_PATH = os.path.expanduser("~")

PRJ_PATH = os.path.abspath(os.path.dirname(__file__))

HOME_NINJA_PATH = os.path.join(HOME_PATH, ".ninja_ide")

python_path = "python"

syntax_files = os.path.join(PRJ_PATH, "extras", "syntax")

plugins = os.path.join(HOME_NINJA_PATH, "extras", "plugins")

editor_skins = os.path.join(HOME_NINJA_PATH, "extras", "skins", "editor")

gui_skins = os.path.join(HOME_NINJA_PATH, "extras", "skins", "gui")

start_page_url = os.path.join(PRJ_PATH, "doc", "startPage.html")

start_page_url_win = os.path.join(PRJ_PATH, "doc", "startPageWin.html")

descriptor = os.path.join(HOME_NINJA_PATH, "extras", "plugins", "descriptor.json")

extras = os.path.join(HOME_NINJA_PATH, "extras")

extras_skins = os.path.join(extras, "skins")


#===============================================================================
# URLS
#===============================================================================

bugs_page = "http://code.google.com/p/ninja-ide/issues/list"

plugins_doc = "http://code.google.com/p/ninja-ide/wiki/CrearPlugins"


#===============================================================================
# IMAGES
#===============================================================================

images = {
    "splash": os.path.join(PRJ_PATH, "img", "splash.png"),
    "icon": os.path.join(PRJ_PATH, "img", "icon.png"),
    "iconUpdate": os.path.join(PRJ_PATH, "img", "icon-update.png"),
    "new": os.path.join(PRJ_PATH, "img", "document-new.png"),
    "newProj": os.path.join(PRJ_PATH, "img", "project-new.png"),
    "open": os.path.join(PRJ_PATH, "img", "document-open.png"),
    "openProj": os.path.join(PRJ_PATH, "img", "project-open.png"),
    "openFolder": os.path.join(PRJ_PATH, "img", "folder-open.png"),
    "save": os.path.join(PRJ_PATH, "img", "document-save.png"),
    "saveAs": os.path.join(PRJ_PATH, "img", "document-save-as.png"),
    "saveAll": os.path.join(PRJ_PATH, "img", "document-save-all.png"),
    "copy": os.path.join(PRJ_PATH, "img", "edit-copy.png"),
    "cut": os.path.join(PRJ_PATH, "img", "edit-cut.png"),
    "paste": os.path.join(PRJ_PATH, "img", "edit-paste.png"),
    "redo": os.path.join(PRJ_PATH, "img", "edit-redo.png"),
    "undo": os.path.join(PRJ_PATH, "img", "edit-undo.png"),
    "find": os.path.join(PRJ_PATH, "img", "find.png"),
    "findReplace": os.path.join(PRJ_PATH, "img", "find-replace.png"),
    "play": os.path.join(PRJ_PATH, "img", "play.png"),
    "stop": os.path.join(PRJ_PATH, "img", "stop.png"),
    "file-run": os.path.join(PRJ_PATH, "img", "file-run.png"),
    "debug": os.path.join(PRJ_PATH, "img", "debug.png"),
    "designer": os.path.join(PRJ_PATH, "img", "qtdesigner.png"),
    "bug": os.path.join(PRJ_PATH, "img", "bug.png"),
    "function": os.path.join(PRJ_PATH, "img", "function.png"),
    "module": os.path.join(PRJ_PATH, "img", "module.png"),
    "class": os.path.join(PRJ_PATH, "img", "class.png"),
    "attribute": os.path.join(PRJ_PATH, "img", "attribute.png"),
    "web": os.path.join(PRJ_PATH, "img", "web.png"),
    "follow": os.path.join(PRJ_PATH, "img", "follow.png"),
    "splitH": os.path.join(PRJ_PATH, "img", "split-horizontal.png"),
    "splitV": os.path.join(PRJ_PATH, "img", "split-vertical.png"),
    "splitCPosition": os.path.join(PRJ_PATH, "img", "panels-change-position.png"),
    "splitMPosition": os.path.join(PRJ_PATH, "img", "panels-change-vertical-position.png"),
    "splitCRotate": os.path.join(PRJ_PATH, "img", "panels-change-orientation.png"),
    "indent-less": os.path.join(PRJ_PATH, "img", "indent-less.png"),
    "indent-more": os.path.join(PRJ_PATH, "img", "indent-more.png"),
    "console": os.path.join(PRJ_PATH, "img", "console.png"),
    "pref": os.path.join(PRJ_PATH, "img", "preferences-system.png"),
    "tree-app": os.path.join(PRJ_PATH, "img", "tree", "project", "tree-app.png"),
    "tree-code": os.path.join(PRJ_PATH, "img", "tree", "project", "tree-code.png"),
    "tree-folder": os.path.join(PRJ_PATH, "img", "tree", "project", "tree-folder.png"),
    "tree-html": os.path.join(PRJ_PATH, "img", "tree", "project", "tree-html.png"),
    "tree-generic": os.path.join(PRJ_PATH, "img", "tree", "project", "tree-generic.png"),
    "tree-css": os.path.join(PRJ_PATH, "img", "tree", "project", "tree-CSS.png"),
    "tree-java": os.path.join(PRJ_PATH, "img", "tree", "project", "tree-java.png"),
    "tree-python": os.path.join(PRJ_PATH, "img", "tree", "project", "tree-python.png"),
    "tree-image": os.path.join(PRJ_PATH, "img", "tree", "project", "tree-image.png"),
    "comment-code": os.path.join(PRJ_PATH, "img", "comment-code.png"),
    "uncomment-code": os.path.join(PRJ_PATH, "img", "uncomment-code.png"),
    "reload-file": os.path.join(PRJ_PATH, "img", "reload-file.png"),
    "print": os.path.join(PRJ_PATH, "img", "document-print.png")
}


#===============================================================================
# COLOR SCHEMES
#===============================================================================

color_scheme = {
    "keyword": "darkMagenta",
    "operator": "darkRed",
    "brace": "#858585",
    "definition": "black",
    "string": "green",
    "string2": "darkGreen",
    "comment": "gray",
    "properObject": "darkBlue",
    "numbers": "brown",
    "spaces": "#BFBFBF",
    "extras": "orange",
    "editor-background": "white",
    "editor-selection-color": "white",
    "editor-selection-background": "#437DCD",
    "editor-text": "black",
    "current-line": "darkCyan",
    "selected-word": "yellow",
    "fold-area": "lightGray",
    "fold-arrow": "gray"
}

custom_scheme = {}

#===============================================================================
# WORKSPACE
#===============================================================================

workspace = ""


#===============================================================================
# FUNCTIONS
#===============================================================================

createpath = os.path.join


def create_home_dir_structure():
    for d in (HOME_NINJA_PATH, extras, plugins, extras_skins, gui_skins, editor_skins):
        if not os.path.isdir(d):
            os.mkdir(d)


