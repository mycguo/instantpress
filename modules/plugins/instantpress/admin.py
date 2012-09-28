#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 Plugin Instant Press  https://bitbucket.org/mulonemartin/instantpress/
 version: 2.0
 Copyright (c) 2011 Mulone, Pablo Martin (http://martin.tecnodoc.com.ar/)
 License: MIT
"""

import os.path
from gluon import *

from appsettings import app_settings

from plugins.markitup import PluginMarkitup
from plugins.cleditor import PluginCLeditor

from plugins.instantpress.core import PluginI2PCore
from plugins.prettyexception import PRETTYHTTP
from plugins.admin import admin_ui

from PIL import Image


class PluginI2PAdmin(object):
    """ Admin """

    def __init__(self, boilerplate, i2pcore=None):
        """Init"""

        self.boilerplate = boilerplate

        if not i2pcore:
            self.i2pcore = PluginI2PCore(self.boilerplate)
            self.i2pcore.install()  # define tables
        else:
            self.i2pcore = i2pcore

        self.rec_x_page = 10
        self.max_images_x_page = 5
        self.thumb_size = (140, 80)
        self.controller_name = 'instantpress'

        if app_settings.i2p_editor in ['cleditor']:
            self.plugin_editor = PluginCLeditor(boilerplate)
        elif app_settings.i2p_editor in ['markitup']:
            self.plugin_editor = PluginMarkitup(boilerplate)
        else:
            raise PRETTYHTTP(400, "Bad config settings, i2p_editor")

        self.image_download = lambda image: self.static_upload_folder(image)

        self.create_fist_time()

    def static_upload_folder(self, image):
        """ Generate image download """

        v_path = image.split('.')
        return URL('static', 'uploads',
                args=[v_path[0] + '.' + v_path[1],
                      v_path[2][:2],
                      image], extension=0)

    def create_fist_time(self):
        """ Create only the first time """

        db = self.boilerplate.db
        request = current.request

        if self.i2pcore.migrate:  # insert if not exist
            if db(db[self.i2pcore.table_name_categories].id > 0).count() == 0:
                db[self.i2pcore.table_name_categories].insert(
                    name='uncategorized',
                  title='Uncategorized',
                  description='Uncategorized',
                  created_on=request.now
                  )
            #widget: about me
            if db((db[self.i2pcore.table_name_post].name == 'widget-about-me') & \
                  (db[self.i2pcore.table_name_post].is_widget == True)).count() == 0:
                content = ""
                db[self.i2pcore.table_name_post].insert(name='widget-about-me',
                                                      title='Widget About Me',
                                                      description=content,
                                                      created_by_id=0,
                                                      updated_by_id=0,
                                                      is_page=True,
                                                      is_widget=True,
                                                      published=True,
                                                      markup='xml'
                                                      )

            #widget: front page
            if db((db[self.i2pcore.table_name_post].name == 'widget-front-page') & \
                  (db[self.i2pcore.table_name_post].is_widget == True)).count() == 0:
                content = ""
                db[self.i2pcore.table_name_post].insert(name='widget-front-page',
                                                      title='Widget Front Page',
                                                      description=content,
                                                      created_by_id=0,
                                                      updated_by_id=0,
                                                      is_page=True,
                                                      is_widget=True,
                                                      published=True,
                                                      markup='xml'
                                                      )

    def keywords_to_list(self, value):
        """ Keyworkds to list """

        keywordsList = []
        keywords = value.split(',')  # first separate the keys
        for keyw in keywords:
            cleanKeyword = keyw.strip()
            cleanKeyword = cleanKeyword.lower()  # lower the words

            if cleanKeyword == "":
                continue
            keywordsList.append(cleanKeyword)

        keywordsList = {}.fromkeys(keywordsList).keys()  # Remove duplicate
        try: keywordsList.remove('')
        except: pass  # remove

        return keywordsList

    def _remove_taglist(self, post_id):
        """ Remove tags list """

        db = self.boilerplate.db

        t_tags = self.i2pcore.table_name_tags
        t_taglist = self.i2pcore.table_name_tagslist

        tagslist = db(db[t_taglist].post_id == post_id).select()
        for tag_entry in tagslist:
            tag_id = tag_entry.tag_id
            count = db(db[t_taglist].tag_id == tag_id).count()
            if count <= 1:
                #delete the description if there are only entry
                db(db[t_tags].id == tag_id).delete()
        db(db[t_taglist].post_id == post_id).delete()

    def _add_new_keyword(self, name, title):
        """ Add new keyword """

        db = self.boilerplate.db

        t_tags = self.i2pcore.table_name_tags
        tags = db(db[t_tags].name == name).select()
        if tags:
            return tags[0].id
        else:
            id_tag = db[t_tags].insert(name=name, title=title)
            return id_tag

    def _add_keyword(self, post_id, key):
        """ Add keyword """

        db = self.boilerplate.db

        t_taglist = self.i2pcore.table_name_tagslist
        name = (IS_SLUG()(key))[0]  # _utils_flat_title(key)
        idtag = self._add_new_keyword(name, key)
        new_entry = db[t_taglist].insert(tag_id=idtag, post_id=post_id)

    def save_keywords_as_tags(self, post_id, keywordsList):
        """ Save keywords as tags """

        self._remove_taglist(post_id)  # first remove all entries in tags with
        for key in keywordsList:
            self._add_keyword(post_id, key)

    def postlist(self):
        """ Post list """

        T = current.T
        db = self.boilerplate.db
        t_posts = self.i2pcore.table_name_post

        self.i2pcore.represent()  # represent fields

        query = (db[t_posts].is_page == False)

        fields = [db[t_posts]['id'],
                  db[t_posts]['title'],
                  db[t_posts]['updated_on'],
                  db[t_posts]['published']
                  ]

        links = [lambda row: A(SPAN(_class='icon edit'),
                               SPAN(T('Edit')),
                                _href="%s" % URL(self.controller_name,
                                    'postedit',
                                    args=[row.id],
                                    vars={'markup':''}),
                                    _title=T('Edit'), _class='w2p_trap button16'),
                 lambda row: A(SPAN(_class='icon view'),
                               SPAN(T('Preview')),
                                 _href="%s" % URL(self.controller_name,
                                     'postpreview',
                                     args=[row.id]),
                                     _title=T('Preview'),
                                     _target='_blank', _class='w2p_trap button16')]

        table = SQLFORM.grid(query,
                        fields=fields,
                        links=links,
                        orderby=~db[t_posts].id,
                        csv=False,
                        searchable=False,
                        create=False,
                        editable=False,
                        details=False,
                        paginate=self.rec_x_page,
                        ui=admin_ui()
                        )

        return table

    def url_pages(self, var_request, page=1,
                    controller='default', function='default'):
        """ Url pages function """

        var_request['pag'] = page
        return URL(controller, function, vars=var_request)

    def postadd(self):
        """ A new post """

        basic_fields = ['categories', 'title', 'description', 'text_slice',
                        'keywords_txt', 'published']

        form = self.changepost(id=0, parent=0, is_page=False,
                                basic_fields=basic_fields)

        return form

    def postedit(self, id, markup=""):
        """ Edit Content """

        response = current.response

        basic_fields = ['categories', 'title', 'description', 'text_slice',
                        'keywords_txt', 'published']

        form = self.changepost(id=id, is_page=False, basic_fields=basic_fields,
                                 markup=markup)

        return form

    def changepost(self, id=0, parent=0, is_page=True, basic_fields=None,
                            markup=''):
        """Change post update"""

        db = self.boilerplate.db
        T = current.T
        session = current.session
        request = current.request
        response = current.response

        t_posts = self.i2pcore.table_name_post

        if id > 0:
            basic_fields.append('name')

        if markup == "":
            markup = self.plugin_editor.defaultlang

        if 'description' in basic_fields:
            self.plugin_editor.render_editor('#i2p_posts_description', markup, id=id)

        if 'text_slice' in basic_fields:
            self.plugin_editor.render_editor('#i2p_posts_text_slice', markup, id=id)

        user_id = session.auth.user.id
        form = SQLFORM(db[t_posts],
                       id,
                       showid=False,
                       fields=basic_fields,
                       submit_button=T('Save'))

        if id == 0:
            form.vars.created_by_id = user_id
            form.vars.created_on = request.now
            form.vars.published_on = request.now
            form.vars.parent = parent
            form.vars.is_page = is_page

        form.vars.updated_by_id = user_id
        form.vars.updated_on = request.now

        if form.accepts(request.vars, session):
            if id > 0:
                editing = True
            else:
                editing = False
            self._change_post_extra(form.vars.id,
                                    title=form.vars.title,
                                    keywords_txt=form.vars.keywords_txt,
                                    editing=editing,
                                    markup=markup)

            response.flash = T('Record updated!')

        return form

    def _change_post_extra(self, id, title="", keywords_txt="",
                                 editing=False, markup=""):
        """ Change post extra """

        db = self.boilerplate.db

        t_posts = self.i2pcore.table_name_post
        posts = db(db[t_posts].id == id).select()
        if posts:
            post = posts[0]

            #flat name
            if not editing:
                try:
                    flat_name = (IS_SLUG()(title))[0]
                    post.update_record(name=flat_name)
                except:
                    pass

            #the tags
            if keywords_txt != "":
                keywordsList = self.keywords_to_list(keywords_txt)
                self.save_keywords_as_tags(id, keywordsList)
                post.update_record(keywords=keywordsList)

            #language editor markup
            post.update_record(markup=markup)

    """ PAGES """

    def pagelist(self, iswidgets=False):
        """ Page list """

        T = current.T
        db = self.boilerplate.db
        t_posts = self.i2pcore.table_name_post

        self.i2pcore.represent()  # represent fields

        query = (db[t_posts].is_page == True) &\
                (db[t_posts].is_widget == iswidgets)

        fields = [db[t_posts]['id'],
                  db[t_posts]['title'],
                  db[t_posts]['parent'],
                  db[t_posts]['menu_order'],
                  db[t_posts]['menu_show'],
                  db[t_posts]['published']
          ]

        links = [lambda row: A(SPAN(_class='icon edit'), SPAN(T('Edit')),
                            _href="%s" % URL(self.controller_name,
                                        'pageedit',
                                        args=[row.id],
                                        vars={'markup':''}),
                                        _title=T('Edit'),
                                        _class='w2p_trap button16'),
                 lambda row: A(SPAN(_class='icon add'), SPAN(T('Add')),
                             _href="%s" % URL(self.controller_name,
                             'pageadd',
                             args=[row.id]),
                             _title=T('Add page to this page as a child'),
                             _class='w2p_trap button16'),
                 lambda row: A(SPAN(_class='icon view'), SPAN(T('Preview')),
                             _href="%s" % URL(self.controller_name,
                                 'pagepreview',
                                 args=[row.id]),
                                 _title=T('Preview'),
                                 _target='_blank', _class='w2p_trap button16')]

        table = SQLFORM.grid(query,
                        fields=fields,
                        links=links,
                        orderby=~db[t_posts].id,
                        csv=False,
                        searchable=False,
                        create=False,
                        editable=False,
                        details=False,
                        paginate=self.rec_x_page,
                        ui=admin_ui()
                        )
        return table

    def pageadd(self, parent):
        """ Page Add """

        basic_fields = ['categories', 'title', 'description',
                        'keywords_txt', 'published', 'menu_show',
                        'menu_order', 'is_widget']

        form = self.changepost(id=0, parent=parent, basic_fields=basic_fields)
        return form

    def pageedit(self, id, markup=""):
        """ Page Content """

        response = current.response

        basic_fields = ['categories', 'title', 'description',
                        'keywords_txt', 'published', 'menu_show',
                        'menu_order', 'is_widget']

        form = self.changepost(id=id, basic_fields=basic_fields, markup=markup)

        return form

    def pagemarkup(self, id):
        """ Page save and continue """

        db = self.boilerplate.db
        markup = ''

        t_posts = self.i2pcore.table_name_post
        posts = db(db[t_posts].id == id).select()
        if posts:
            post = posts[0]
            markup = post.markup

        return markup

    def editoractionbar(self, id, setmarkup=''):
        """ Editor Bar """

        T = current.T
        response = current.response
        request = current.request

        markups = self.plugin_editor.languages
        options = []
        for markup in markups:
            if markup[1] == setmarkup:
                options.append(OPTION(markup[0], _value=markup[1],
                                 _selected='selected'))
            else:
                options.append(OPTION(markup[0], _value=markup[1]))

        sel_markup = SELECT(options, _name='s_markups',
                            _id="s_markups")

        script = '''
                $('#s_markups').change(function(){
                markup = jQuery('#s_markups').val();
                window.location = "%(url_base)s/%(id)s/?markup=" + markup;
                });
        ''' % {'url_base': URL(self.controller_name, request.function), 'id': id}

        response.scripts_ready.append(script)

        return sel_markup

    """ CATEGORIES """

    def catlist(self):
        """ Categories List """

        T = current.T
        db = self.boilerplate.db
        t_cats = self.i2pcore.table_name_categories

        links = [lambda row: A(SPAN(_class='icon edit'),
                               SPAN(T('Edit')),
                          _href="%s" % URL(self.controller_name,
                                                   'catedit',
                                                   args=[row.id]),
                          _title='Edit', _class='w2p_trap button16')]

        query = (db[t_cats].id > 0)
        table = SQLFORM.grid(query,
                             links=links,
                             orderby=~db[t_cats].id,
                             csv=False,
                             searchable=False,
                             create=False,
                             editable=False,
                             paginate=self.rec_x_page,
                             ui=admin_ui()
                            )
        return table

    def catadd(self):
        """ Categorie add """

        db = self.boilerplate.db
        T = current.T
        request = current.request
        session = current.session

        t_cats = self.i2pcore.table_name_categories

        basic_fields = ['title', 'description']

        form = SQLFORM(db[t_cats],
                       showid=False,
                       fields=basic_fields,
                       formstyle="divs",
                       submit_button=T('Save'))

        form.vars.created_on = request.now
        if form.accepts(request.vars, session):

            cats = db(db[t_cats].id == form.vars.id).select()
            if cats:
                cat = cats[0]
                flat_name = (IS_SLUG()(form.vars.title))[0]  # flat name
                cat.update_record(name=flat_name)

            session.flash = T('Cat added!')
            redirect(URL('categories'))

        return form

    def editcat(self, id):
        """ Edit categories """

        db = self.boilerplate.db
        T = current.T
        session = current.session
        request = current.request

        t_cats = self.i2pcore.table_name_categories

        basic_fields = ['title', 'name', 'description']

        form = SQLFORM(db[t_cats],
                       id,
                       showid=False,
                       fields=basic_fields,
                       formstyle="divs",
                       submit_button=T('Save'))

        form.vars.created_on = request.now
        if form.accepts(request.vars, session):
            session.flash = T('Cat updated!')
            redirect(URL('categories'))

        return form

    """ IMAGES """
    def thumbnail_upload(self, image):
        """ Get the url thumbnail of upload file """

        extension = str(os.path.splitext(image)[1]).lower()
        if extension in ['.jpg', '.png', '.gif', '.jpeg']:
            return self.image_download(image)
        else:
            return URL('static', 'plugins/admin/images/generic.png')

    def uploads(self):
        """ Uploads """

        T = current.T
        db = self.boilerplate.db
        t_images = self.i2pcore.table_name_images

        fields = [
                  db[t_images]['thumb'],
                  db[t_images]['post_id'],
                  db[t_images]['comment'],
                  db[t_images]['upload_on']
                  ]

        self.i2pcore.represent_uploads()  # represent fields

        query = (db[t_images].id > 0)

        table = SQLFORM.grid(query,
                        orderby=~db[t_images].id,
                        fields=fields,
                        csv=False,
                        searchable=False,
                        create=False,
                        editable=False,
                        details=False,
                        paginate=self.rec_x_page,
                        ui=admin_ui()
                        )

        return table

    def make_thumbnail(self, id, size=(48, 48)):
        """Make the thumbnail"""

        db = self.boilerplate.db
        request = current.request
        t_images = self.i2pcore.table_name_images

        image_row = db(db[t_images].id == id).select().first()
        if image_row:
            v_path = image_row.image.split('.')
            folder_path = os.path.join(self.i2pcore.storage_upload,
                                        v_path[0] + '.' + v_path[1],
                                        v_path[2][:2]
                                        )
            im = Image.open(os.path.join(folder_path, image_row.image))
            im.thumbnail(size, Image.ANTIALIAS)
            root, ext = os.path.splitext(image_row.image)
            thumbName = '%s_thumb%s' % (root, ext)
            im.save(os.path.join(folder_path, thumbName))
            image_row.update_record(thumb=thumbName)

    def form_upload(self, id):
        """ Form Upload """

        db = self.boilerplate.db
        T = current.T
        session = current.session
        request = current.request
        response = current.response

        t_images = self.i2pcore.table_name_images

        basic_fields = ['image', 'comment']

        form = SQLFORM(db[t_images],
                       showid=False,
                       fields=basic_fields,
                       submit_button=T('Upload'))

        form.vars.post_id = id
        form.vars.upload_on = request.now
        form.vars.upload_by = session.auth.user.id
        if form.accepts(request.vars, session):
            response.flash = T('Image uploaded!')
            self.make_thumbnail(form.vars.id)

        return form

    def uploads_editor(self, postid):
        """ Uploads """

        T = current.T
        db = self.boilerplate.db
        t_images = self.i2pcore.table_name_images

        if postid > 0:
            images = db(db[t_images].post_id == postid).select()
        else:
            images = db(db[t_images].id > 0).select()

        imglist = ""
        for image in images:
            i_img = IMG(_src=self.image_download(image.thumb),
                                            _height="48px", _width="48px",
                                            _replace="replace")
            i_div = DIV(i_img, _class='u_image')

            imglist += str(i_div.xml()).replace('replace="replace"',
                                                'data-url="%s"' %\
                            self.image_download(image.image))

        link_all = A(T('all'), _href=URL('instantpress', 'uploads_editor'))
        link_art = A(T('article'), _href=URL('instantpress',
                                        'uploads_editor',
                                        vars={'postid': postid}))
        note = T('Browse %s or only related to this %s') % (link_all, link_art)

        return (note, imglist)
