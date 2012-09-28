#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
 Plugin PRETTYHTTP
 version: 2.0
 Copyright (c) 2011 Mulone, Pablo Martin (http://martin.tecnodoc.com.ar/)
 License: MIT
"""

"""
 ABOUT PRETTYHTTP:
"""

from gluon.globals import current
from gluon.http import HTTP
from gluon.html import IMG, A, URL


class PRETTYHTTP(BaseException):
    """ PRETTYHTTP """

    def __init__(
        self,
        status,
        body='',
        **headers
        ):
        self.status = status
        self.body = body
        self.headers = headers

        body = self.render()

        raise HTTP(status, body, **headers)

    def render(self):
        """ Render """

        response = current.response
        T = current.T

        return '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="utf-8">
        <title>%(title)s</title>
        <style type="text/css">
        body {
            margin: 0;
            padding: 0;
            background: #fff;
            font-family: Arial,Helvetica,sans-serif;
            color: #444;
        }
        #wrapper {
            margin: 0 auto;
            padding: 0;
        }
        #page {
            width: 500px;
            margin: 0 auto;
            padding: 40px;
        }
        #warning {
            -webkit-border-radius: 5px;
            -moz-border-radius: 5px;
            border-radius: 5px;
            width: 350px
            padding: 20px;
            background-color: #fff;
            border: 1px solid #d0cfc2;
            }
        .title {
            font-size: 20px;
            font-weight: bold;
            }
        .content {
            padding: 20px;
            }
        .description {
            font-size: 16px;
            }
        </style>
        </head>
        <body>
        <div id="wrapper">
        <div id="page">
        <div id="warning">
            %(image)s
            <div class="content">
            <div class="title"> %(title)s </div>
            <div class="description">%(message)s <p>%(index)s</p> </div>
            <div style="clear: both; float: none;"></div>
            </div>
        </div>
        </div>
        </div>
        </body>
        </html>
        ''' % {'title': self.body,
               'image': IMG(_src=URL('static','plugins/prettyexception/images/warning.png'), _alt="Warning",_style="float: left; padding: 5px;").xml(),
               'message':self.body,
               'index':A(T('Back to the index page'), _href=URL('default','index')).xml()}
