#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 Plugin Comments
 version: 2.0
 Copyright (c) 2011 Mulone, Pablo Martin (http://martin.tecnodoc.com.ar/)
 License: MIT
"""

from plugins.comments import PluginComments


def comments():
    """ Display the comments """

    response.view = 'plugins/comments/comments.html'

    try:
        tablename = request.vars.tablename
        record_id = int(request.vars.record_id)
        order = int(request.vars.order)
        page = int(request.vars.page)
    except:
        raise HTTP(400, 'Problem with vars')

    if not tablename:
        tablename = "default"

    if not order in [0, 1]:
        raise HTTP(400, 'Problem with vars')

    plg = PluginComments(boilerplate)
    plg.install()

    plg.request_vars['tablename'] = tablename
    plg.request_vars['record_id'] = record_id
    plg.request_vars['order'] = order
    plg.request_vars['page'] = page

    form = plg.form_reply(tablename, record_id)
    count, comments = plg.comments(tablename, record_id, page, order)
    title = plg.generate_title(count)
    pagination = plg.render_pagination()
    editor = XML('<script type="text/javascript">jQuery(document).ready(function(){%s});</script>' %\
           plg.render_text_editor())  # render the editor

    return dict(form=form,
                comments=comments,
                title=title,
                pagination=pagination,
                editor=editor,
                plg=plg)


def comment_id():
    """ Comment id display"""

    try:
        comment_id = int(request.args(0))
    except:
        raise HTTP(400, "Problem with id.")

    plg = PluginComments(boilerplate).install()

    body = plg.render_markup_comment(_.comment_comment(comment_id))

    return body


@boilerplate.auth.requires_login()
def profile():
    """ Display profile form """

    response.view = 'plugins/comments/profile.html'
    form = PluginComments(boilerplate).install().form_profile()

    return dict(form=form)


@boilerplate.auth.requires_login()
def vote_up():
    """Vote up"""

    try:
        comment_id = int(request.args[0])
    except:
        raise HTTP(400, "Problem with comment id.")

    message = PluginComments(boilerplate).install().vote_comment(comment_id, 1)

    return "ShowFlash('%s');" % (message)


@boilerplate.auth.requires_login()
def vote_down():
    """Vote down"""

    try:
        comment_id = int(request.args[0])
    except:
        raise HTTP(400, "Problem with comment id.")

    message = PluginComments(boilerplate).install().vote_comment(comment_id, -1)

    return "ShowFlash('%s');" % (message)


@boilerplate.auth.requires_membership('Admin')
def delete_comment():
    """ Delete a comment only by admin user """

    try:
        comment_id = int(request.args[0])
    except:
        raise HTTP(400, "Problem with comment id.")

    message = PluginComments(boilerplate).install().delete_comment(comment_id)

    return "ShowFlash('%s');" % (message)
