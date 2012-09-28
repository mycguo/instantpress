#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 Plugin Navigation
 version: 2.0
 Copyright (c) 2011 Mulone, Pablo Martin (http://martin.tecnodoc.com.ar/)
 License: MIT

 Plugin navigation is based on:
     http://lwis.net/free-css-drop-down-menu/
     was adapted to used with web2py and helper MenuPlugin by Martin Mulone
"""

from gluon.html import DIV, LI, UL, A, URL, XML
from gluon.globals import current


class NAV(DIV):
    """NAV html5 """

    tag = 'nav'


class MenuRoot(object):
    """ Menu root """

    def __init__(self, fatheritem=None, **attributes):
        """ Init """

        self.items = []
        self.fatheritem = fatheritem
        self.attributes = attributes

    def append(self, item):
        """ Append item object """

        self.items.append(item)

    def appenditem(self, label, action, name='', **attributes):
        """ Append single items """

        self.append(MenuItem(label, action, name, **attributes))

    def render(self):
        """ Render Menu Root """

        render = []
        for item in self.items:
            render.append(item.render())

        if self.attributes:
            renderul = UL(render, **dict(self.attributes))
        else:
            renderul = UL(render)

        if self.fatheritem:
            return self.fatheritem.render(renderul)
        else:
            return renderul


class MenuItem(object):
    """ Menu item """

    def __init__(self, label, action, name='', **attributes):
        """ Item """

        self.label = label
        self.action = action
        self.name = name
        self.attributes = attributes

    def render(self, elements=''):
        """ Render """

        if not self.action:
            if self.attributes:
                return LI(A(self.label,
                            _href='#',
                            _onclick='javascript:void(0);return false;'),
                            elements, **dict(self.attributes))
            else:
                return LI(A(self.label,
                            _href='#',
                            _onclick='javascript:void(0);return false;'),
                        elements)
        elif isinstance(self.action, basestring):
            if self.attributes:
                return LI(A(self.label, _href=self.action),
                                    elements, **dict(self.attributes))
            else:
                return LI(A(self.label, _href=self.action), elements)
        elif isinstance(self.action, DIV):
            if self.attributes:
                return LI(self.action, elements, **dict(self.attributes))
            else:
                return LI(self.action, elements)
        else:
            if self.attributes:
                return LI(self.label, elements, **dict(self.attributes))
            else:
                return LI(self.label, elements)


class PluginNavigation(DIV):
    """ Plugin menu """

    def __init__(self, **attributes):
        """ Init """

        self.components = []
        self.attributes = attributes
        self.cssbase = URL('static', 'plugins/dropdown/dropdown.css')
        self.csstheme = URL('static',
                            'plugins/dropdown/themes/skeleton.css')

        self.root = MenuRoot()

    def install(self):
        """ Install required css or js """

        response = current.response
        response.files.append(self.cssbase)
        response.files.append(self.csstheme)

    def searchitem(self, name, items, historyitems=None):
        encontrado = False
        if not historyitems:
            historyitems = []

        for item in items:
            if isinstance(item, MenuRoot):
                historyitems.append(item.fatheritem)
                encontrado, historyitems = self.searchitem(name,
                                                item.items,
                                                historyitems)
            elif item.name == name:
                encontrado = True

            if encontrado:
                historyitems.append(item)
                break

        if not encontrado:
            historyitems = []  # descartamos la rama

        return encontrado, historyitems

    def navigationbar(self, name):
        """Render navigation bar item, search by name"""

        navigation = ''
        found, historyitems = self.searchitem(name, self.root.items)
        if found:
            for item in historyitems:
                if isinstance(item, MenuItem):
                    navigation += " &raquo; %s " % \
                                              A(item.label, _href=item.action)
        return XML("<div class='navigationbar'>%s</div>" % navigation)

    def appenditem(self, label, action, name='', **attributes):
        """ Append single items """

        self.root.appenditem(label, action, name, **attributes)

    def append(self, itemobject):
        """ Append item object """

        self.root.append(itemobject)

    def xml(self):
        """ XML """

        self.components = []
        self.components.append(self.root.render())

        return DIV.xml(self)
