#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 Instant 2 Press (https://bitbucket.org/mulonemartin/instantpress/)
 version: 2.0
 Copyright (c) 2011 Mulone, Pablo Martin (http://martin.tecnodoc.com.ar/)
 License: BSD
"""

from plugins.instantpress.admin import PluginI2PAdmin
from plugins.instantpress.widgets import PluginI2PWidgets
from plugins.prettyexception import PRETTYHTTP


@boilerplate.auth.requires_membership('Admin')
def index():
    """ Post list index """

    response.view = 'plugins/instantpress/index.html'
    i2padmin = PluginI2PAdmin(boilerplate)

    return dict(i2padmin=i2padmin)


@boilerplate.auth.requires_membership('Admin')
def posts():
    """ Post list index """

    response.view = 'plugins/instantpress/posts.html'
    i2padmin = PluginI2PAdmin(boilerplate)
    table = i2padmin.postlist()
    return dict(table=table, i2padmin=i2padmin)


@boilerplate.auth.requires_membership('Admin')
def postadd():
    """ Add a new post """

    response.view = 'plugins/instantpress/postadd.html'
    i2padmin = PluginI2PAdmin(boilerplate)
    form = i2padmin.postadd()

    return dict(form=form, i2padmin=i2padmin)


@boilerplate.auth.requires_membership('Admin')
def postedit():

    response.view = 'plugins/instantpress/postedit.html'
    try:
        post_id = int(request.args[0])
    except:
        raise PRETTYHTTP(400, 'Problem with id')

    try:
        markup = request.vars.markup
    except:
        raise PRETTYHTTP(400, 'Problem with markup value')

    i2padmin = PluginI2PAdmin(boilerplate)

    if not markup or markup == '':
        db_markup = i2padmin.pagemarkup(post_id)
        if db_markup != markup:
            redirect(URL(i2padmin.controller_name,
                        request.function,
                        args=[post_id],
                        vars={'markup': db_markup}))

    form = i2padmin.postedit(post_id, markup)
    editoractionbar = i2padmin.editoractionbar(post_id, setmarkup=markup)

    return dict(form=form, post_id=post_id, editoractionbar=editoractionbar,
                i2padmin=i2padmin)


@boilerplate.auth.requires_membership('Admin')
def postremove():
    """ Remove post id """

    try:
        post_id = int(request.args[0])
    except:
        raise PRETTYHTTP(400, 'Problem with post_id')

    i2padmin = PluginI2PAdmin(boilerplate)
    message = i2padmin.postremove(post_id)

    return "ShowFlash('%s');" % (message)


@boilerplate.auth.requires_membership('Admin')
def postpreview():
    """ Post Preview """

    response.view = 'plugins/instantpress/default_post.html'

    var_request = {}
    try:
        var_request['id'] = int(request.args[0])
    except:
        raise PRETTYHTTP(400, 'Problem with post id')

    i2pwidget = PluginI2PWidgets(boilerplate)

    return i2pwidget.default_post(var_request)


@boilerplate.auth.requires_membership('Admin')
def pages():
    """ Page list """

    response.view = 'plugins/instantpress/pages.html'
    i2padmin = PluginI2PAdmin(boilerplate)
    table = i2padmin.pagelist()

    return dict(table=table, i2padmin=i2padmin)


@boilerplate.auth.requires_membership('Admin')
def pageswidgets():
    """ Page list """

    response.view = 'plugins/instantpress/pages.html'
    i2padmin = PluginI2PAdmin(boilerplate)
    table = i2padmin.pagelist(iswidgets=True)

    return dict(table=table, i2padmin=i2padmin)


@boilerplate.auth.requires_membership('Admin')
def pageadd():
    """Page Add"""

    response.view = 'plugins/instantpress/pageadd.html'
    try:
        parent = int(request.args[0])
    except:
        parent = 0

    i2padmin = PluginI2PAdmin(boilerplate)
    form = i2padmin.pageadd(parent)

    return dict(form=form, i2padmin=i2padmin)


@boilerplate.auth.requires_membership('Admin')
def pageedit():
    """ Page Content """

    response.view = 'plugins/instantpress/pageedit.html'

    try:
        page_id = int(request.args[0])
    except:
        raise PRETTYHTTP(400, 'Problem with page_id')

    try:
        markup = request.vars.markup
    except:
        raise PRETTYHTTP(400, 'Problem with markup value')

    i2padmin = PluginI2PAdmin(boilerplate)
    if not markup or markup == '':
        db_markup = i2padmin.pagemarkup(page_id)
        if db_markup != markup:
            redirect(URL(i2padmin.controller_name,
                        request.function,
                        args=[page_id],
                        vars={'markup': db_markup}))

    form = i2padmin.pageedit(page_id, markup)
    editoractionbar = i2padmin.editoractionbar(page_id, setmarkup=markup)

    return dict(form=form, page_id=page_id, editoractionbar=editoractionbar,
    i2padmin=i2padmin)


@boilerplate.auth.requires_membership('Admin')
def pagepreview():
    """ Page preview """

    response.view = 'plugins/instantpress/default_page.html'
    var_request = {}
    try:
        var_request['id'] = request.args[0]
    except:
        raise PRETTYHTTP(400, 'Problem with page_id')

    i2pwidget = PluginI2PWidgets(boilerplate).install()
    page = i2pwidget.page_by_id(var_request['id'], allow_unpublished=True)

    return dict(page=page)


""" CATEGORIES """


@boilerplate.auth.requires_membership('Admin')
def catadd():
    """ Categorie Add """

    response.view = 'plugins/instantpress/catadd.html'
    i2padmin = PluginI2PAdmin(boilerplate)
    form = i2padmin.catadd()

    return dict(form=form, i2padmin=i2padmin)


@boilerplate.auth.requires_membership('Admin')
def catedit():
    """ Categorie edit """

    response.view = 'plugins/instantpress/catedit.html'

    try:
        cat_id = int(request.args[0])
    except:
        raise PRETTYHTTP(400, 'Problem with cat_id')

    i2padmin = PluginI2PAdmin(boilerplate)

    form = i2padmin.editcat(cat_id)

    return dict(form=form, i2padmin=i2padmin)


@boilerplate.auth.requires_membership('Admin')
def categories():
    """ Categories """

    response.view = 'plugins/instantpress/categories.html'
    i2padmin = PluginI2PAdmin(boilerplate)
    table = i2padmin.catlist()

    return dict(table=table, i2padmin=i2padmin)

""" Uploads """

@boilerplate.auth.requires_membership('Admin')
def uploads():
    """ uploads list index """

    response.view = 'plugins/instantpress/uploads.html'

    try:
        postid = int(request.vars.postid)
    except:
        postid = 0

    i2padmin = PluginI2PAdmin(boilerplate)
    form = i2padmin.form_upload(postid)
    table = i2padmin.uploads()
    return dict(table=table, form=form, i2padmin=i2padmin)


@boilerplate.auth.requires_membership('Admin')
def uploads_editor():
    """ uploads list index """

    response.view = 'plugins/instantpress/uploads_editor.html'

    try:
        postid = int(request.vars.postid)
    except:
        postid = 0

    i2padmin = PluginI2PAdmin(boilerplate)
    form = i2padmin.form_upload(postid)
    note, uploads = i2padmin.uploads_editor(postid)
    form_external = SQLFORM.factory(Field('url', label=T('Fill url')),
                                  Field('width', label=T('Width'), default='300'),
                                  Field('height', label=T('Height'), default='200'),
                                  Field('alt', label=T('Alt text'), default=''),
                                  Field('colorbox', 'boolean', label='Colorbox', default=True),
                                  Field('align', label='Align', requires=IS_IN_SET(['N/a', 'Left', 'Right'])),
                                  Field('v_space', label=T('Vert. space'), default=''),
                                  Field('h_space', label=T('Horz. space'), default=''),
                                _class='url_external')
    return dict(uploads=uploads, note=note, form=form, i2padmin=i2padmin,
                form_external=form_external)
