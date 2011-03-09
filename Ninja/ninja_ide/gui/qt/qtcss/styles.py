from __future__ import absolute_import

from ninja_ide.resources import color_scheme
from ninja_ide.gui.generic.main_panel import EditorGeneric

css_styles = {
    'editor':'''
        QPlainTextEdit {
          font-family: monospace;
          font-size: 10;
          color: black;
          background-color: white;
          selection-color: white;
          selection-background-color: #437DCD;
        }''',

    'toolbar-default':"""
        QToolBar::separator {
         border-radius: 10px;
         background: gray;
         width: 2px; /* when vertical */
         height: 2px; /* when horizontal */
         }
        """
}


def set_style(widget, sty):
    css = css_styles.get(sty, '')
    widget.setStyleSheet(css)


def set_custom_style(widget, style):
    widget.setStyleSheet(style)


def set_editor_style(widget, scheme):
    css = 'QPlainTextEdit {font-family: %s;font-size: %s;color: %s;background-color: '\
        '%s;selection-color: %s;selection-background-color: %s;}' \
        % (EditorGeneric.font_family, str(EditorGeneric.font_size),
            scheme.get('editor-text', color_scheme['editor-text']),
            scheme.get('editor-background', color_scheme['editor-background']),
            scheme.get('editor-selection-color', color_scheme['editor-selection-color']),
            scheme.get('editor-selection-background', color_scheme['editor-selection-background']))
    widget.setStyleSheet(css)
