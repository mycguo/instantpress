#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 Skeleton.
 This is a scattfold web2py application based on getskeleton.
 Layout: www.getskeleton.com
 Copyright (c) 2011 Mulone, Pablo Martin (application not layout)
 https://bitbucket.org/mulonemartin/skeleton/
 License: MIT
"""

if request.is_local:  # this is to reload module - develop mode - remove prod
    from gluon.custom_import import track_changes
    track_changes()

# Read application settings take a look to modules/appsettings.py
from appsettings import app_settings

# Boilerplate a set of tools of web2py logic in a module the only objective
# is to clean up of code the models.
from plugins.boilerplate import BoilerPlate
from plugins.navigation import PluginNavigation, MenuRoot, MenuItem
from plugins.colorbox import PluginColorbox

if not request.env.web2py_runtime_gae:
    db = DAL(app_settings.database_uri)  # Change in uri in 00config.py
else:
    #Intant press doesn't suport GAE google app engine.
    db = DAL('google:datastore')  # connect to Google BigTable

# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []

# main class boilerplate, to manage all
boilerplate = BoilerPlate(app_settings, db, cache=cache)

# comment the service you don't want
mail = boilerplate.init_mail()
auth = boilerplate.init_auth()
crud = boilerplate.init_crud()
service = boilerplate.init_service()

# Menu: Make your own menu here
response.menu = PluginNavigation(_class='topdropdown')
response.menu.root.attributes.update(_id='nav',
                            _class='dropdown dropdown-horizontal')
#Menu item Home
response.menu.appenditem(T('Home'), URL('default', 'index'), name='Home')
response.menu.install()  # install the required js and css

#Here the plugins
# by default we install colorbox
PluginColorbox(boilerplate).install().add("jQuery('a.colorboxgallery').colorbox();")
