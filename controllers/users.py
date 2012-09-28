#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 Plugin Users
 version: 2.0
 Copyright (c) 2011 Mulone, Pablo Martin (http://martin.tecnodoc.com.ar/)
 License: BSD
"""

from plugins.users import PluginUsers
from plugins.prettyexception import PRETTYHTTP


def index():
    """
    WARNING: You can delete this controller after you create an admin user.
    """

    response.view = 'plugins/users/index.html'
    passw = PluginUsers(boilerplate).autoadmin()
    if passw == '':
        raise PRETTYHTTP(401, 'Not authorized')

    return dict(passw=passw)


@boilerplate.auth.requires_membership('Admin')
def users():
    """ Users """

    response.view = 'plugins/users/users.html'

    pluginusers = PluginUsers(boilerplate)
    table = pluginusers.index()

    return dict(table=table)


@boilerplate.auth.requires_membership('Admin')
def activate():
    """ activate"""

    try:
        user = int(request.args[0])
    except:
        raise PRETTYHTTP(400, 'Problem with id')

    message = PluginUsers(boilerplate).activate(user)

    return "ShowFlash('%s');" % (message)


@boilerplate.auth.requires_membership('Admin')
def disable():
    """Disable"""

    try:
        user = int(request.args[0])
    except:
        raise PRETTYHTTP(400, 'Problem with id')

    message = PluginUsers(boilerplate).disable(user)

    return "ShowFlash('%s');" % (message)


@boilerplate.auth.requires_membership('Admin')
def membership():
    """ membership """

    response.view = 'plugins/users/membership.html'

    try:
        user = int(request.args[0])
    except:
        raise PRETTYHTTP(400, 'Problem with id')

    plgusers = PluginUsers(boilerplate)
    table = plgusers.membership(user)
    username = plgusers.username(user)

    return dict(table=table, user=user, username=username)


@boilerplate.auth.requires_membership('Admin')
def membership_assign():

    try:
        user = int(request.vars.user)
        group = int(request.vars.group)
    except:
        raise PRETTYHTTP(400, 'Problem with id')

    message = PluginUsers(boilerplate).membership_assign(user, group)

    return "ShowFlash('%s');" % (message)


@boilerplate.auth.requires_membership('Admin')
def membership_remove():

    try:
        user = int(request.vars.user)
        group = int(request.vars.group)
    except:
        raise PRETTYHTTP(400, 'Problem with id')

    message = PluginUsers(boilerplate).membership_remove(user, group)

    return "ShowFlash('%s');" % (message)


@boilerplate.auth.requires_membership('Admin')
def groups():
    """ membership """

    response.view = 'plugins/users/groups.html'

    table = PluginUsers(boilerplate).groups()

    return dict(table=table)
