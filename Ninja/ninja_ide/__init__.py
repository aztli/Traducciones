from __future__ import absolute_import

#===============================================================================
# METADATA
#===============================================================================

__prj__ = "ninja-ide"
__author__ = "The Ninja-IDE Team"
__mail__ = "ninja-ide at googlegroups dot com"
__url__ = "http://www.ninja-ide.org.ar"
__version__ = "1.0"
__licence__ = "GPL3"
__date__ = "30/01/2011"
__since__ = "2010/12/28"

VERSION = __version__

#===============================================================================
# DOC
#===============================================================================

"""NINJA-IDE is a cross-platform integrated development environment (IDE).
NINJA-IDE runs on Linux/X11, Mac OS X and Windows desktop operating systems, and
allows developers to create applications for several purposes using all the
tools and utilities of NINJA-IDE, making the task of writing software easier and
more enjoyable.

"""

#===============================================================================
# FUNCTIONS
#===============================================================================

def setup_and_run():
    
    # import only on run
    # si se importa siempre el setup.py va a tratar de importar este modulo
    # para leer la metadata y al importar las demas cosas empieza a fallar todo
    # y todo EXPLOTA!!!!!
    from ninja_ide import core, resources
    
    # Creamos la estructura para guardar nuestros datos
    resources.create_home_dir_structure()
    
    # Arrancamos ninja
    core.run_ninja()
