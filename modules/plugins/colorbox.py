#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
 Plugin Colorbox
 version: 2.0
 Copyright (c) 2011 Mulone, Pablo Martin (http://martin.tecnodoc.com.ar/)
 License: MIT
"""

"""
 ABOUT PluginColorbox:
 http://colorpowered.com/colorbox/

 A light-weight, customizable lightbox plugin for jQuery 1.3 through 1.6

 Usage
ColorBox accepts settings from an object of key/value pairs, and can be assigned to any HTML element.

// Format:
$(selector).colorbox({key:value, key:value, key:value});
// Examples:
// Image links displayed as a group
$('a.gallery').colorbox({rel:'gal'});

// Ajax
$('a#login').colorbox();

// Called directly, without assignment to an element:
$.colorbox({href:"thankyou.html"});

// Called directly with HTML
$.colorbox({html:"<h1>Welcome</h1>"});

// ColorBox can accept a function in place of a static value:
$("a.gallery").colorbox({rel: 'gal', title: function(){
    var url = $(this).attr('href');
    return '<a href="' + url + '" target="_blank">Open In New Window</a>';
}});

"""

from gluon.globals import current
from gluon.html import URL


class PluginColorbox(object):
    """ PluginColorbox """

    def __init__(self, boilerplate):

        self.boilerplate = boilerplate
        self.css_theme = URL('static',
                        'plugins/colorbox/css/theme4/colorbox.css')

    def install(self):
        """ Load need it to run """

        response = current.response

        response.files.append(URL('static',
                            'plugins/colorbox/js/jquery.colorbox-min.js'))
        response.files.append(self.css_theme)

        return self

    def add(self, code):
        """ Response on ready """

        response = current.response
        response.scripts_ready.append(code)
