#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 Plugin Markitup
 version: 2.0
 Copyright (c) 2011 Mulone, Pablo Martin (http://martin.tecnodoc.com.ar/)
 License: MIT

 This is the editor www.markitup.com
"""

from gluon import *
from gluon.contrib.markdown import *


class PluginMarkitup(object):
    """ ABOUT Markitup: This is the editor www.markitup.com """

    def __init__(self, boilerplate):
        """ Init """

        self.boilerplate = boilerplate
        self.defaultlang = 'markmin'

        self.css_skin = URL('static', 'plugins/markitup/js/markitup/skins/simple/style.css')
        self.css_set = URL('static', 'plugins/markitup/js/markitup/sets/markmin/style.css')
        self.js_set = URL('static', 'plugins/markitup/js/markitup/sets/markmin/set.js')

    def install(self):
        """ Install the plugin """

        response = current.response
        response.files.append(self.css_skin)
        response.files.append(URL('static', 'plugins/markitup/js/markitup/jquery.markitup.js'))

        response.files.append(self.css_set)
        response.files.append(self.js_set)

    def _render_editor(self, divelement, markup='markmin', onready=True):
        """ Render the editor in a divelement """

        response = current.response

        if not markup or markup == "":
            markup = self.defaultlang

        if markup in ['markmin']:
            self.css_set = URL('static',
                        'plugins/markitup/js/markitup/sets/markmin/style.css')
            self.js_set = URL('static',
                        'plugins/markitup/js/markitup/sets/markmin/set.js')
        elif markup in ['xml']:
            self.css_set = URL('static',
                        'plugins/markitup/js/markitup/sets/html/style.css')
            self.js_set = URL('static', 'plugins/markitup/js/markitup/sets/html/set.js')
        elif markup in ['markdown']:
            self.css_set = URL('static', 'plugins/markitup/js/markitup/sets/markdown/style.css')
            self.js_set = URL('static', 'plugins/markitup/js/markitup/sets/markdown/set.js')
        elif markup in ['textile']:
            self.css_set = URL('static', 'plugins/markitup/js/markitup/sets/textile/style.css')
            self.js_set = URL('static', 'plugins/markitup/js/markitup/sets/textile/set.js')

        script = 'jQuery("%s").markItUp(mySettings);' % divelement
        if onready:
            response.scripts_ready.append(script)

        self.install()

        return script

    def render_editor(self, widgets_list, markup='markmin', onready=True):
        """ This render the editor """

        script = ""
        if isinstance(widgets_list, list):
            for widget in widgets_list:
                script = self._render_editor(widget, markup, onready)
        else:
            script = self._render_editor(widgets_list, markup, onready)

        return script

    def render_content(self, content, markup='markmin'):
        """ Render the content content """

        if markup in ['markmin']:
            return MARKMIN(content)
        elif markup in ['xml']:
            return XML(content)
        elif markup in ['markdown']:
            return markdown(content)
        elif markup in ['textile']:
            return textile(content)
        else:
            return ""
