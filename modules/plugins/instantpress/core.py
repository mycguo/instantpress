#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 Instant Press  https://bitbucket.org/mulonemartin/instantpress/
 version: 2.0
 Copyright (c) 2011 Mulone, Pablo Martin (http://martin.tecnodoc.com.ar/)
 License: MIT
"""

from gluon import *
import os


class PluginI2PCore(object):
    """ Plugin INSTANT TO PRESS CORE"""

    def __init__(self, boilerplate, migrate=True):
        """ Init """

        self.boilerplate = boilerplate
        self.migrate = migrate
        request = current.request

        self.prefix = 'i2p_'
        self.table_name_post = '%sposts' % self.prefix
        self.table_name_categories = '%scategories' % self.prefix
        self.table_name_categorieslist = '%scategorieslist' % self.prefix
        self.table_name_images = '%simages' % self.prefix
        self.table_name_links = '%slinks' % self.prefix
        self.table_name_tags = '%stags' % self.prefix
        self.table_name_tagslist = '%stagslist' % self.prefix

        self.markup_languages = [('Markmin', 'markmin'),
                                ('HTML', 'xml'),
                                ('Textile', 'textile'),
                                ('Markdown', 'markdown')]
        self.markup_default = 'markmin'
        self.storage_upload = os.path.join(request.folder, 'static', 'uploads')
        self.image_download = lambda image: self.static_upload_folder(image)

    def static_upload_folder(self, image):
        """ Generate image download """

        v_path = image.split('.')
        return URL('static', 'uploads',
                args=[v_path[0] + '.' + v_path[1],
                      v_path[2][:2],
                      image], extension=0)

    def install(self):
        """Install create the tables or define"""

        db = self.boilerplate.db
        T = current.T
        request = current.request

        #TABLE NAME: POST
        db.define_table(self.table_name_post,
            Field('id', 'id'),
            Field('name', 'string', length=255, default="",
                label=T("Name (Slug)"),
                comment=T("Ex: my-page or leave it blank")),
            Field('title', 'string', length=255, required=True,
                  label=T("Title"),
                  comment=T("Ex: My Title"),
                  requires=IS_NOT_EMPTY()),
            Field('description', 'text', default="",
                  label=T("Body"),
                  comment=T("Write your article"),
                  requires=IS_LENGTH(2**28)),
            Field('text_slice', 'text', default="",
                  label=T("Extract"),
                  comment=T("This is a part of body that display on search."),
                  requires=IS_LENGTH(2**28)),
            Field('keywords_txt', 'string', length=255,
                  label=T("Keywords"), \
                  comment=T("Fill keywords separated with ',' comma. Ex: key1, key2.")),
            Field('keywords', 'list:string', readable=False, writable=False),
            Field('categories', 'list:reference %s' % self.table_name_categories,
                  requires=IS_IN_DB(db, '%s.id' % self.table_name_categories,
                                      '%(title)s', multiple=True),
                  widget=SQLFORM.widgets.checkboxes.widget,
                  label=T("Categories"),
                  comment=T("Select categories.")),
            Field('created_on', 'datetime', default=request.now, label=T("Created on")),
            Field('published_on', 'datetime', default=request.now),
            Field('updated_on', 'datetime', default=request.now, label=T("Updated on")),
            Field('created_by_id', 'integer', default=0, required=True),
            Field('updated_by_id', 'integer', default=0, required=True),
            Field('published', 'boolean', default=False, label=T("Published")),
            Field('is_widget', 'boolean', default=False, label=T("Is widget?")),
            Field('is_page', 'boolean', default=True),
            Field('parent', 'integer', default=0, label=T("Parent")),
            Field('menu_show', 'boolean', default=True, label=T("Display menu")),
            Field('menu_order', 'integer', default=0, label=T("Menu Order")),
            Field('post_url', 'text', default="", requires=(IS_URL())),
            Field('markup', 'string', default="", length=255,
                  requires=(IS_IN_SET(['markmin',
                                       'xml',
                                       'textile',
                                       'markdown']))),
                       #to set the language editor
            migrate=self.migrate)

        db[self.table_name_post].name.requires = \
          [IS_EMPTY_OR(IS_SLUG()),
           IS_NOT_IN_DB(db, db[self.table_name_post].name)]

        #TABLE NAME: CATEGORIES
        db.define_table(self.table_name_categories,
            Field('id', 'id'),
            Field('name', 'string', length=255, requires=(IS_SLUG()), label=T('Name')),
            Field('title', 'string', length=255, required=True, label=T('Title')),
            Field('description', 'text', default="", label=T('Description')),
            Field('created_on', 'datetime', default=request.now, label=T('Created on')),
            migrate=self.migrate)

        #TABLE NAME: CATEGORIESLIST
        db.define_table(self.table_name_categorieslist,
            Field('id', 'id'),
            Field('cat_id', 'integer', required=True),
            Field('post_id', 'integer', required=True),
            migrate=self.migrate)

        db[self.table_name_categorieslist].cat_id.requires = \
          IS_IN_DB(db, '%s.id' % self.table_name_categories,
                   '%s.title' % self.table_name_categories)
        db[self.table_name_categorieslist].post_id.requires = \
          IS_IN_DB(db, '%s.id' % self.table_name_post,
                   '%s.title' % self.table_name_post)

        #TABLE NAME: IMAGES
        # New changes upload to static folder
        db.define_table(self.table_name_images,
            Field('id', 'id'),
            Field('post_id', 'integer', default=0, label=T('Article')),
            Field('comment', 'string', default=""),
            Field('image', 'upload', default="", autodelete=True,
                  uploadseparate=True, label=T('File'),
                  uploadfolder=self.storage_upload),
            Field('thumb', 'upload', default="", label=T('Thumb'),
                  autodelete=True,
                  writable=False, readable=False, uploadseparate=True,
                  uploadfolder=self.storage_upload),
            Field('upload_on', 'datetime', default=request.now,
                    label=T('Uploaded on'),
                  writable=False, readable=False),
            Field('upload_by', 'integer', default=0, required=True),
            migrate=self.migrate)

        #TABLE NAME: TAGS
        db.define_table(self.table_name_tags,
            Field('id', 'id'),
            Field('name', 'string', length=255, requires=(IS_SLUG())),
            Field('title', 'string', length=255, required=True),
            Field('created_on', 'datetime', default=request.now),
            migrate=self.migrate)

        #TABLE NAME: TAGSLIST
        db.define_table(self.table_name_tagslist,
            Field('id', 'id'),
            Field('tag_id', 'integer', required=True),
            Field('post_id', 'integer', required=True),
            migrate=self.migrate)

        db[self.table_name_tagslist].tag_id.requires = \
          IS_IN_DB(db, '%s.id' % self.table_name_tags,
                   '%s.title' % self.table_name_tags)
        db[self.table_name_tagslist].post_id.requires = \
          IS_IN_DB(db, '%s.id' % self.table_name_post,
                   '%s.title' % self.table_name_post)

    def uninstall(self):
        """To uninstall the plugin
        WARNING:
        This will delete the information in the tables
        """
        db = self.boilerplate.db

        tables = [self.table_name_post,
                    self.table_name_categories,
                    self.table_name_categorieslist,
                    self.table_name_images,
                    self.table_name_links,
                    self.table_name_tags,
                    self.table_name_tagslist,
                    self.table_name_language]

        for table in tables:
            try:
                db[table].drop()
            except KeyError:
                query = 'DROP TABLE %s;' % table
                db.executesql(query)

    def represent(self):
        """Represent tables"""

        T = current.T
        db = self.boilerplate.db
        t_posts = self.table_name_post

        def repre_parent(id):

            posts = db(db[t_posts].id == id).select(db[t_posts].title)
            if posts:
                return "%s (%s)" % (posts[0].title, id)
            else:
                return 'N/a'

        #Represents
        db[t_posts].created_by_id.represent = lambda value, row: \
                                        db.auth_user(value).username
        db[t_posts].updated_by_id.represent = lambda value, row: \
                                        db.auth_user(value).username
        db[t_posts].parent.represent = lambda value, row: repre_parent(value)

    def represent_uploads(self):
        """Represent tables"""

        T = current.T
        db = self.boilerplate.db
        t_posts = self.table_name_post
        t_images = self.table_name_images

        def repre_post(id):

            posts = db(db[t_posts].id == id).select(db[t_posts].title)
            if posts:
                return "%s (%s)" % (posts[0].title, id)
            else:
                return 'N/a'

        db[t_images].thumb.readable = True
        db[t_images].thumb.represent = lambda value, row: \
                                        IMG(_src=self.image_download(value),
                                            _height="48px", _width="48px")
        db[t_images].post_id.represent = lambda value, row: repre_post(value)
