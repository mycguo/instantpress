#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 Plugin Admin
 version: 2.0
 Copyright (c) 2011 Mulone, Pablo Martin (http://martin.tecnodoc.com.ar/)
 License: MIT
"""

from gluon import *
from plugins.navigation import PluginNavigation, MenuRoot, MenuItem


class PluginAdmin(object):
    """ All admin  """

    def __init__(self, boilerplate):
        """Init"""

        self.boilerplate = boilerplate

    def install(self):
        """ Install default """

        response = current.response
        T = current.T

        #Menu
        response.menu = PluginNavigation(_class='topdropdown')
        response.menu.root.attributes.update(_id='nav',
                            _class='dropdown dropdown-horizontal')

        response.menu.appenditem(T('Back'), URL('default', 'index'))
        response.menu.appenditem('Panel', URL('instantpress', 'index'))

        menuchild = MenuRoot(MenuItem(SPAN('Instant Press', _class='dir'), None))
        menuchild.appenditem(T('Pages'), URL('instantpress', 'pages'))
        menuchild.appenditem(T('Articles'), URL('instantpress', 'posts'))
        menuchild.appenditem(T('Categories'), URL('instantpress', 'categories'))
        menuchild.appenditem(T('Uploads'), URL('instantpress', 'uploads'))
        response.menu.append(menuchild)

        menuchild = MenuRoot(MenuItem(SPAN(T('Users'), _class='dir'), None))
        menuchild.appenditem(T('Users'), URL('users', 'users'))
        menuchild.appenditem(T('Groups'), URL('users', 'groups'))
        response.menu.append(menuchild)

        response.menu.cssbase = URL('static',
                            'plugins/admin/css/dropdown/dropdown.css')
        response.menu.csstheme = URL('static',
                            'plugins/admin/css/dropdown/themes/skeleton.css')

        response.menu.install()  # install the required js and css

        #Plugins
        #Layout.
        #I made this to not mix with modified layout.

        def admin_style():
            response.files.insert(0, URL('static', 'plugins/admin/css/base.css'))
            response.files.insert(1, URL('static', 'plugins/admin/css/skeleton.css'))
            response.files.insert(2, URL('static', 'plugins/admin/css/layout.css'))
            response.files.insert(2, URL('static', 'plugins/admin/css/admin.css'))

        self.boilerplate.render_style = lambda: admin_style()


def admin_ui():
    return dict(widget='',
              header='',
              content='',
              default='',
              cornerall='',
              cornertop='',
              cornerbottom='',
              button='button16',
              buttontext='',
              buttonadd='icon add',
              buttonback='icon back',
              buttonexport='icon csv',
              buttondelete='icon remove',
              buttonedit='icon edit',
              buttontable='icon table',
              buttonview='icon view',
              )
