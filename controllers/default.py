#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
from plugins.instantpress.widgets import PluginI2PWidgets
from plugins.comments import PluginComments
from plugins.prettyexception import PRETTYHTTP


def index():
    """ Default Blog Index """

    boilerplate.check_first_time()

    response.view = 'plugins/instantpress/default_index.html'

    var_request = {}
    try:
        var_request['pag'] = int(request.vars.pag)
    except:
        var_request['pag'] = 1

    i2pwidget = PluginI2PWidgets(boilerplate)
    response.menu = i2pwidget.pages_to_menu(response.menu)

    return i2pwidget.default_index(var_request)


def category():
    """ Blog index by category """

    response.view = 'plugins/instantpress/default_category.html'

    var_request = {}

    try:
        var_request['id'] = int(request.vars.id)
    except:
        raise PRETTYHTTP(404, T("Sorry, but the page doesn't exist."))

    try:
        var_request['pag'] = int(request.vars.pag)
    except:
        var_request['pag'] = 1

    i2pwidget = PluginI2PWidgets(boilerplate)
    response.menu = i2pwidget.pages_to_menu(response.menu)

    return i2pwidget.default_category(var_request)


def tag():
    """ Blog index by tag """

    response.view = 'plugins/instantpress/default_tag.html'

    var_request = {}
    try:
        var_request['name'] = request.vars.name
        if not var_request['name']:
            raise ValueError

    except ValueError:
        raise PRETTYHTTP(404, T("Sorry, but the page doesn't exist."))

    try:
        var_request['pag'] = int(request.vars.pag)
    except:
        var_request['pag'] = 1

    i2pwidget = PluginI2PWidgets(boilerplate)
    response.menu = i2pwidget.pages_to_menu(response.menu)

    return i2pwidget.default_tag(var_request)


def search():
    """ Blog index by search query """

    response.view = 'plugins/instantpress/default_search.html'

    var_request = {}
    try:
        var_request['q'] = request.vars.q
        if not var_request['q']:
            raise ValueError

    except ValueError:
        raise PRETTYHTTP(404, T("Sorry, but the page doesn't exist."))

    try:
        var_request['pag'] = int(request.vars.pag)
    except:
        var_request['pag'] = 1

    i2pwidget = PluginI2PWidgets(boilerplate)
    response.menu = i2pwidget.pages_to_menu(response.menu)

    return i2pwidget.default_search(var_request)


def archives():
    """ Blog index by archives """

    response.view = 'plugins/instantpress/default_archives.html'

    var_request = {}
    try:
        var_request['year'] = int(request.vars.year)
        var_request['month'] = int(request.vars.month)
        d_lower = datetime.date(var_request['year'], var_request['month'], 1)
    except:
        raise PRETTYHTTP(404, T("Sorry, but the page doesn't exist."))

    try:
        var_request['pag'] = int(request.vars.pag)
    except:
        var_request['pag'] = 1

    i2pwidget = PluginI2PWidgets(boilerplate)
    response.menu = i2pwidget.pages_to_menu(response.menu)

    return i2pwidget.default_archives(var_request)


def post():
    """ An example of post controller ex: 2011/04/11/2_my-article """

    response.view = 'plugins/instantpress/default_post.html'

    var_request = {}
    try:
        var_request['year'] = request.args[0]
        var_request['month'] = request.args[1]
        var_request['day'] = request.args[2]
        arg0 = str(request.args[3]).split("_")[0]
        var_request['id'] = int(arg0)
    except:
        raise PRETTYHTTP(404, T("Sorry, but the page doesn't exist."))

    i2pwidget = PluginI2PWidgets(boilerplate)
    response.menu = i2pwidget.pages_to_menu(response.menu)

    return i2pwidget.default_post(var_request)


def page():
    """ An example of page controller by id """

    response.view = 'plugins/instantpress/default_page.html'

    var_request = {}
    try:
        var_request['name'] = request.args[0]
    except:
        raise PRETTYHTTP(404, T("Sorry, but the page doesn't exist."))

    i2pwidget = PluginI2PWidgets(boilerplate)
    response.menu = i2pwidget.pages_to_menu(response.menu)

    return i2pwidget.default_page(var_request)


def feed():
    """ RSS """

    response.view = 'plugins/instantpress/default_feed.rss'

    i2pwidget = PluginI2PWidgets(boilerplate)

    rss = i2pwidget.default_rss_posts()

    return rss


def feed_comments():
    """ RSS comments """

    response.view = 'plugins/instantpress/default_feed.rss'

    plgrss = PluginComments(boilerplate).install()
    rss = plgrss.rss(tablename="instantpress",
                          site_title=plgrss.site_name,
                          site_link=URL('default', 'index'),
                          site_description=plgrss.site_description)

    return rss


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=boilerplate.auth())
