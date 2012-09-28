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

from plugins.admin import PluginAdmin

# Read application settings take a look to modules/appsettings.py
from appsettings import app_settings

# Boilerplate a set of tools of web2py logic in a module the only objective
# is to clean up of code the models.
from plugins.boilerplate import BoilerPlate

if not request.env.web2py_runtime_gae:
    db = DAL(app_settings.database_uri)  # Change in uri in 00config.py
else:
    db = DAL('google:datastore')  # connect to Google BigTable

# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []

# main class boilerplate, to manage all
boilerplate = BoilerPlate(app_settings, db)

# comment the service you don't want
mail = boilerplate.init_mail()
auth = boilerplate.init_auth()

PluginAdmin(boilerplate).install()
