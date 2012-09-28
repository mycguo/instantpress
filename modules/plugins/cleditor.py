#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 Plugin CLeditor
 version: 1.0
 Copyright (c) 2011 Mulone, Pablo Martin (http://martin.tecnodoc.com.ar/)
 License: MIT

 This is plugin of the web editor https://github.com/cleditor/cleditor

 WARNING: If you alter this plugin you can cause damage in instantpress plugin
"""

from gluon import *


class PluginCLeditor(object):
    """ ABOUT CLeditor: This is the editor
        https://github.com/cleditor/cleditor """

    def __init__(self, boilerplate):
        """ Init """

        self.boilerplate = boilerplate

        # Languages supported
        self.languages = [('HTML', 'xml')]
        self.defaultlang = 'xml'

        self.editor_settings = '''{
            width:        "100%", // width not including margins, borders or padding
            height:       "250" // height not including margins, borders or padding
            }
        '''

    def install(self):
        """ Install the plugin """

        response = current.response
        response.files.append(URL('static',
                                'plugins/cleditor/jquery.cleditor.css'))
        response.files.append(URL('static',
                                'plugins/cleditor/jquery.cleditor.js'))
        #notused
        #response.files.append(URL('static',
        #                        'plugins/cleditor/jquery.cleditor.extimage.js'))

    def _render_editor(self, divelement, markup='xml', id=0, onready=True):
        """ Render the editor in a divelement """

        response = current.response

        if not markup or markup == "":
            markup = self.defaultlang

        response.scripts_ready.append(self.plugin_extimage(id))

        script = '''jQuery("%s").cleditor(%s);''' %\
             (divelement,
             self.editor_settings)
        if onready:
            response.scripts_ready.append(script)

        self.install()

        return script

    def render_editor(self, widgets_list, markup, id=0):
        """ This render the editor """

        if isinstance(widgets_list, list):
            for widget in widgets_list:
                self._render_editor(widget, markup, id=id)
        else:
            self._render_editor(widgets_list, markup, id=id)

    def render_content(self, content, markup):
        """ Render the content content """

        if markup in ['xml']:
            return XML(content)
        else:
            return ""

    def plugin_extimage(self, id):
        """ Script of plugin image"""

        script = """
        $.cleditor.buttons.image = {
            name: 'image',
            title: 'Insert/Upload Image',
            command: 'inserthtml', //insertimage
            popupName: 'image',
            popupClass: 'cleditorPrompt',
            stripIndex: $.cleditor.buttons.image.stripIndex,
            popupContent:
                '<iframe class="upload_editor" src="%s" style="width:370;height:400;border:0;" />',
            buttonClick: imageButtonClick
        };

        function closePopup(editor) {
            editor.hidePopups();
            editor.focus();
        }

        function imageProperties(url, $iframe) {
              var width = $iframe.contents().find("input#no_table_width").val();
              var height = $iframe.contents().find("input#no_table_height").val();
              var alt = $iframe.contents().find("input#no_table_alt").val();
              var colorbox = $iframe.contents().find("input#no_table_colorbox").val();
              var align = $iframe.contents().find("select#no_table_align").val();
              var style='';
              if (align=='Left') {style += " float: left; "} else if (align=='Right'){style += " float: right;"};
              var v_space = $iframe.contents().find("input#no_table_v_space").val();
              var h_space = $iframe.contents().find("input#no_table_h_space").val();
              if (v_space != "") {style += " margin-top: "+v_space +"; margin-bottom: "+v_space+";"};
              if (h_space != "") {style += " margin-left: "+h_space +"; margin-right: "+h_space+";"};
              var upcontent = '<a class="colorboxgallery" href="' + url + '"><img height="'+height+'" width="'+width+'" src="' + url +'" alt="'+alt+'" style="'+style+'" /></a>';
              return upcontent
        }

        function imageButtonClick(e, data) {
            var $iframe = $(data.popup).find('iframe.upload_editor');
            var editor = data.editor;
            $iframe.bind('load', function() {
                $iframe.contents().find(".u_image img").bind("click", function(){
                  var url = $(this).data("url");
                  upcontent = imageProperties(url, $iframe);
                  editor.execCommand(data.command, upcontent, null, data.button);
                  $iframe.unbind('load');
                  closePopup(editor);
                });
                $iframe.contents().find("form.url_external").bind("submit", function(){
                  var url = $iframe.contents().find("input#no_table_url").val();
                  upcontent = imageProperties(url, $iframe);
                  editor.execCommand(data.command, upcontent, null, data.button);
                  $iframe.unbind('load');
                  closePopup(editor);
                  return false;
                });
              });
            //this reload the iframe
            $iframe.attr("src", $iframe.attr("src"));
        }

        """ % URL('instantpress', 'uploads_editor', vars={'postid': id})

        return script
