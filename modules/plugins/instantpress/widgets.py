#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 Instant 2 Press  https://bitbucket.org/mulonemartin/instantpress/
 version: 2.0
 Copyright (c) 2011 Mulone, Pablo Martin (http://martin.tecnodoc.com.ar/)
 License: MIT
"""

import datetime
from string import punctuation
import math

from gluon import *
from gluon.tools import prettydate
from gluon.contrib.markdown import *

from appsettings import app_settings
from plugins.instantpress.core import PluginI2PCore
from plugins.comments import PluginComments
from plugins.prettyexception import PRETTYHTTP
from plugins.navigation import PluginNavigation, MenuRoot, MenuItem


class PluginI2PWidgets(object):
    """ Widgets """

    def __init__(self, boilerplate, i2pcore=None):
        """Init"""

        self.boilerplate = boilerplate

        if not i2pcore:
            self.i2pcore = PluginI2PCore(self.boilerplate)
            self.i2pcore.install()  # define tables
        else:
            self.i2pcore = i2pcore

        self.posts_controller = 'default'
        self.posts_function = 'index'
        self.page_controller = 'default'
        self.page_function = 'page'
        self.post_controller = 'default'
        self.post_function = 'post'
        self.cat_controller = 'default'
        self.cat_function = 'category'
        self.archives_controller = 'default'
        self.archives_function = 'archives'
        self.tags_controller = 'default'
        self.tags_function = 'tag'
        self.feed_controller = 'default'
        self.feed_function = 'feed'
        self.feed_comment_controller = 'default'
        self.feed_comment_function = 'feed_comments'
        self.search_controller = 'default'
        self.search_function = 'search'

        self.display_navigation = True
        self.display_rootnav = True
        self.render_menu = True
        self.show_feed = True

        self.max_results_x_page = 10
        self.max_display_pages = 5

        self.widgets_ajax = False
        self.max_tag_display = 50

        self.recordscount = 0
        self.currentpage = 1
        self.request_vars = {}

        self.comments_enabled = True
        self.comments_on_page = False
        self.comments_feed = True

        self.render_url_page = lambda page, controller, function: \
                    self.default_url_page(page, controller, function)
        self.render_link_post = lambda post, title, anchor, host, onlyurl, **attributes: \
                    self.default_link_post(post, title, anchor, host, onlyurl, **attributes)

        self.engine_comments = lambda: PluginComments(boilerplate).install()
        self.render_comments = lambda id: self.default_comments(id)
        self.render_comments_count = lambda post, engine_comments: \
                    self.default_comments_count(post, engine_comments)

        self.render_page = lambda page: self.default_render_page(page)
        self.render_post = lambda post: self.default_render_post(post)
        self.render_post_extract = lambda post, engine_comments: \
                    self.default_post_extract(post, engine_comments)

        self.render_navigation_bar = lambda page: self.default_navigation_bar(page)
        self.render_navigation_bar_post = lambda post: self.default_navigation_bar_post(post)

        self.author = lambda iduser: self.default_author(iduser)

        self.menutxt_trunk = 200
        self.extra_blocks = {}  # markup extrablocks

    def install(self):
        """ Render the CSS """

        #response = current.response
        #response.files.append(self.css_theme)

        return self

    def default_link_post(self, post, title="", anchor="", host=None, onlyurl=False, **attributes):
        """Post permanent link"""

        if title == "":
            title = post.title

        year = post.published_on.strftime("%Y")
        month = post.published_on.strftime("%m")
        day = post.published_on.strftime("%d")
        idpost = str(post.id) + '_' + str(post.name)
        url_post = URL(self.post_controller,
                    self.post_function,
                    args=[year, month, day, idpost],
                    anchor=anchor, host=host, extension=0)
        if onlyurl:
            return url_post
        else:
            return A(title, _href=url_post, **attributes)

    def default_url_page(self, page, controller, function):
        """ Generate the url to a page """

        request = current.request

        rq_vars = self.request_vars.copy()
        rq_vars['pag'] = page

        return URL(controller, function, vars=rq_vars)

    def _get_page_id(self, id):
        """Get page id"""

        db = self.boilerplate.db

        t_posts = self.i2pcore.table_name_post
        query = (db[t_posts].is_page == True) & \
              (db[t_posts].published == True) & \
              (db[t_posts].id == id)

        pages = db(query).select(db[t_posts].id,
                                db[t_posts].name,
                                db[t_posts].title,
                                db[t_posts].description,
                                db[t_posts].published,
                                db[t_posts].parent,
                                db[t_posts].menu_order,
                                db[t_posts].markup
                                )
        if pages:
            return pages[0]
        else:
            return None

    def default_navigation_bar(self, page):
        """ Navigation bar """

        T = current.T

        if not self.display_navigation:
            return ""

        parentpage = page
        count = 0
        link = A(parentpage.title, _href=URL(self.page_controller,
                                            self.page_function,
                                            args=[parentpage.name]))
        navigation = " &raquo; %s " % link.xml()
        while ((parentpage.parent > 0) or (count > 5)):
            parentpage = self._get_page_id(parentpage.parent)
            if not parentpage:
                break
            link = A(parentpage.title, _href=URL(self.page_controller,
                                                self.page_function,
                                                args=[parentpage.name]))
            navigation = " &raquo; %s " % link.xml() + navigation
            count = count + 1

        if self.display_rootnav:
            navigation = " %s " % T('Pages') + navigation

        return navigation

    def default_navigation_bar_post(self, post):
        """ Render navigation bar post"""

        T = current.T

        if not self.display_navigation:
            return ""

        parentpage = post
        count = 0
        link = self.render_link_post(post, title="", anchor="",
                                    host=None, onlyurl=False)
        navigation = " &raquo; %s " % link.xml()

        if self.display_rootnav:
            navigation = " %s " % T('Posts') + navigation

        return navigation

    def default_render_page(self, page):
        """ Render page """

        T = current.T

        description = self.render_content(page.description,
                                                  markup=page.markup)
        navigation_bar = self.render_navigation_bar(page)

        if self.comments_on_page:
            comments = self.render_comments(post.id)
        else:
            comments = ""

        if self.boilerplate.isadmin():
            edit_link = A(T('[Edit]'), _href=URL('instantpress', 'pageedit', args=[page.id], vars={'markup': ''}))
        else:
            edit_link = ""

        xml_page = '''
        <div class="i2p_page">
          <div class="post_nav">%(navigation_bar)s</div>
          %(edit_link)s
          <div class="post_description">%(description)s</div>
          <div style="clear: both;"></div>
        </div>
        %(comments)s
        ''' % {'description': description,
             'navigation_bar': navigation_bar,
             'comments': comments,
             'edit_link': edit_link
             }

        return XML(xml_page)

    def post_categories(self, post):
        """ Post categories """

        db = self.boilerplate.db

        xml_cats = ""
        t_cats = self.i2pcore.table_name_categories

        for cat_id in post.categories:
            categories = db(db[t_cats].id == cat_id).select()
            if categories:
                cat = categories[0]
                cat_title = A(cat.title, \
                              _href=URL(self.cat_controller,
                                        self.cat_function,
                                        vars={'id': cat.id}))
                xml_cats += " %s " % cat_title.xml()

        return xml_cats

    def default_author(self, iduser):
        """ Autor name"""

        db = self.boilerplate.db

        name = 'No name'
        users = db(db.auth_user.id == iduser).select()
        if users:
            user = users[0]
            name = user.first_name + " " + user.last_name

        return name

    def post_meta(self, post):
        """Post meta"""

        T = current.T

        post_author_caption = '<span class="author">%s</span>' \
                                % self.author(post.created_by_id)

        post_category = self.post_categories(post)

        if post_category == "":
            post_category = T("uncategorized")
            in_category = T('in')
        else:
            in_category = T('in categories')

        post_time = prettydate(post.published_on)
        year_full = post.published_on.strftime("%Y")
        month = post.published_on.strftime("%m")
        link_time = A(post_time, _href=URL(self.archives_controller,
                                           self.archives_function,
                                           vars={'year': year_full,
                                                 'month': month}))
        posted_by = T('by')
        updated_on = T('Published ')
        byline = '''<span class="updated_on">%s %s </span> %s
        <span class="updated_by"> %s </span>
        <span class="meta_categories"> %s %s </span>''' % \
                                (updated_on,
                                 link_time.xml(),
                                 posted_by,
                                 post_author_caption,
                                 in_category,
                                 post_category)

        return byline

    def post_tags(self, keywords):
        """ Tags """

        xml = ''
        if keywords:
            for key in keywords:
                name = (IS_SLUG()(key))[0]
                link = A(key, _href=URL(self.tags_controller,
                                        self.tags_function,
                                        vars={'name': name}))
                xml += " " + link.xml()

        return xml

    def default_render_post(self, post):
        """ Render post """

        T = current.T

        description = self.render_content(post.description,
                                            markup=post.markup)
        navigation_bar = self.render_navigation_bar_post(post)
        post_meta = self.post_meta(post)

        post_updated = '''%s <span class="updated_on">%s</span>
            %s <span class="updated_by">%s</span>''' % \
                (T('This article was updated '),
                 prettydate(post.updated_on),
                 T('by'),
                 self.author(post.updated_by_id))

        xmltags = self.post_tags(post.keywords)
        if xmltags != '':
            post_tags = "%s <span class='bottom_tags'>%s</span> " %\
                      (T('Tags'), xmltags)
        else:
            post_tags = ''

        if self.boilerplate.isadmin():
            edit_link = A(T('[Edit]'), _href=URL('instantpress', 'postedit', args=[post.id], vars={'markup': ''}))
        else:
            edit_link = ""

        xml_post = '''
        <div class="i2p_post">
          <div class="post_nav">%(navigation_bar)s</div>
          <div class="post_title"><h3>%(title)s</h3>%(edit_link)s</div>
          <div class="post_meta">%(post_meta)s</div>
          <div class="post_description">%(description)s</div>
          <div style="clear: both;"></div>
          <div class="post_metabottom">
               <div class="post_updated">%(post_updated)s</div>
               <div class="post_tags">%(post_tags)s</div>
          </div>
        </div>
        %(post_comments)s
        ''' % {'description': description,
             'title': post.title,
             'navigation_bar': navigation_bar,
             'post_meta': post_meta,
             'post_updated': post_updated,
             'post_tags': post_tags,
             'post_comments': self.render_comments(post.id),
             'edit_link': edit_link}

        return XML(xml_post)

    def default_comments(self, id):
        """ Defaults comments, render the comments by default """

        if self.comments_enabled:
            comments = PluginComments(self.boilerplate).install().render(id, tablename="instantpress")
        else:
            comments = ""

        return comments

    def default_comments_count(self, post, engine_comments=None):
        """ Default comments count """

        T = current.T

        if self.comments_enabled and engine_comments:

            comments_count = engine_comments.recordid_count('instantpress', post.id)

            if comments_count == 0:
                text_response = T('No Responses')
            elif comments_count == 1:
                text_response = "1 %s" % T('Response')
            elif comments_count > 1:
                text_response = "%s %s" % (comments_count, T('Responses'))

            responses_caption = "%s" % text_response
            responses = self.render_link_post(post, title=responses_caption, anchor="comments", host=None, onlyurl=False)
            responses_xml = '<div class="post_responses"> %s </div> ' % responses

        else:

            responses_xml = ""

        return responses_xml

    def default_post_extract(self, post, engine_comments=None):
        """Render Post Extract"""

        T = current.T

        description = self.render_content(post.text_slice, markup=post.markup)
        post_meta = self.post_meta(post)

        post_updated = '''%s <span class="updated_on"> %s </span>
          %s <span class="updated_by">%s</span>''' % \
                                (T('This article was updated '),
                                 prettydate(post.updated_on),
                                 T('by'),
                                 self.author(post.updated_by_id))

        xmltags = self.post_tags(post.keywords)
        if xmltags != '':
            post_tags = "%s <span class='bottom_tags'>%s</span> " %\
                      (T('Tags'), xmltags)
        else:
            post_tags = ''

        if self.boilerplate.isadmin():
            edit_link = A(T('[Edit]'), _href=URL('instantpress', 'postedit', args=[post.id], vars={'markup': ''}))
        else:
            edit_link = ""
        read_more = self.render_link_post(post, title=T('Read more'), anchor="", host=None, onlyurl=False)
        title = self.render_link_post(post, title="", anchor="", host=None, onlyurl=False)

        responses_xml = self.render_comments_count(post, engine_comments)

        xml_post = '''
        <div class="post_extract">
          <div class="post_title"><h3>%(title)s</h3>%(edit_link)s</div>
          <div class="post_meta">%(post_meta)s</div>
          <div class="post_description">%(description)s</div>
          <div style="clear: both;"></div>
          <div class="post_metabottom">
               <div class="post_updated">%(post_updated)s</div>
               <div class="post_tags">%(post_tags)s</div>
          </div>
          <div class="post_readmore"> %(read_more)s  </div>
                                      %(responses)s

          <div style="clear: both;"></div>
        </div>
        ''' % {'description': description,
             'title': title.xml(),
             'post_meta': post_meta,
             'post_updated': post_updated,
             'post_tags': post_tags,
             'read_more': read_more.xml(),
             'responses': responses_xml,
             'edit_link': edit_link}

        return XML(xml_post)

    def page_by_id(self, id, allow_unpublished=False):
        """Page by id"""

        db = self.boilerplate.db
        T = current.T

        t_posts = self.i2pcore.table_name_post
        query = ((db[t_posts].is_page == True) \
                 & (db[t_posts].id == id))

        if not allow_unpublished:
            addquery = (db[t_posts].published == True)
            query = query & addquery

        pages = db(query).select(db[t_posts].id,
                                db[t_posts].name,
                                db[t_posts].title,
                                db[t_posts].description,
                                db[t_posts].published,
                                db[t_posts].parent,
                                db[t_posts].menu_order,
                                db[t_posts].markup,
                                )

        if pages:
            page = pages[0]
            render_page = self.render_page(page)

        else:
            raise PRETTYHTTP(404, T("Sorry, but the page doesn't exist"))

        return render_page

    def page_by_name(self, name):
        """Page by name"""

        db = self.boilerplate.db
        T = current.T

        t_posts = self.i2pcore.table_name_post
        query = (db[t_posts].is_page == True) & \
                 (db[t_posts].published == True) & \
                 (db[t_posts].name.like(name))
        pages = db(query).select(db[t_posts].id,
                                db[t_posts].name,
                                db[t_posts].title,
                                db[t_posts].description,
                                db[t_posts].published,
                                db[t_posts].parent,
                                db[t_posts].markup,
                                db[t_posts].menu_order
                                )

        if pages:
            page = pages[0]
            render_page = self.render_page(page)

        else:
            raise PRETTYHTTP(404, T("Sorry, but the page doesn't exist"))

        return (render_page, page.id)

    def post_by_id(self, id, allow_unpublished=False):
        """Post by id"""

        db = self.boilerplate.db
        T = current.T

        t_posts = self.i2pcore.table_name_post
        query = ((db[t_posts].is_page == False) & \
                 (db[t_posts].id == id))

        if not allow_unpublished:
            addquery = (db[t_posts].published == True)
            query = query & addquery

        posts = db(query).select(db[t_posts].id,
                                db[t_posts].name,
                                db[t_posts].title,
                                db[t_posts].description,
                                db[t_posts].published,
                                db[t_posts].text_slice,
                                db[t_posts].keywords_txt,
                                db[t_posts].keywords,
                                db[t_posts].categories,
                                db[t_posts].published_on,
                                db[t_posts].updated_on,
                                db[t_posts].created_by_id,
                                db[t_posts].updated_by_id,
                                db[t_posts].markup
                                )
        if posts:
            post = posts[0]
            render_post = self.render_post(post)

        else:
            raise PRETTYHTTP(404, T("Sorry, but the post doesn't exist"))

        return render_post

    def parent_pages(self, parent=0):
        """ Parent pages """

        db = self.boilerplate.db
        t_posts = self.i2pcore.table_name_post

        query = (db[t_posts].is_page == True) & \
                     (db[t_posts].menu_show == True) & \
                     (db[t_posts].published == True) & \
                     (db[t_posts].is_widget == False) & \
                     (db[t_posts].parent == parent)

        pages = db(query).select(db[t_posts].id,
                            db[t_posts].title,
                            db[t_posts].parent,
                            db[t_posts].name,
                            orderby=db[t_posts].menu_order | db[t_posts].id,
                            cache=(self.boilerplate.cache.ram, 60))
        return pages

    def add_subpages(self, subpages, page):
        """ Add the subpages """

        root = MenuRoot(MenuItem(SPAN(page.title[:self.menutxt_trunk],
                                        _class='dir'),
                                        URL(self.page_controller,
                                            self.page_function,
                                            args=[page.name])))

        for subpage in subpages:
            subsubpages = self.parent_pages(subpage.id)
            if subsubpages:
                root.append(self.add_subpages(subsubpages, subpage))
            else:
                root.appenditem(subpage.title[:self.menutxt_trunk],
                            URL(self.page_controller,
                                self.page_function,
                                args=[subpage.name]))

        return root

    def pages_to_menu(self, menu=None):
        """ Pages to menu """

        if not menu:
            menu = PluginNavigation(_class='topdropdown')
            menu.root.attributes.update(_id='nav',
                            _class='dropdown dropdown-horizontal')

        pages = self.parent_pages(parent=0)  # Get root pages
        for page in pages:
            subpages = self.parent_pages(page.id)
            if subpages:
                menu.append(self.add_subpages(subpages, page))
            else:
                menu.appenditem(page.title[:self.menutxt_trunk],
                                URL(self.page_controller,
                                    self.page_function,
                                    args=[page.name]))

        return menu

    """
     SIDEBARS
    """

    def _sidebar_categories(self):
        """ Sidebar categories """

        db = self.boilerplate.db
        T = current.T

        t_cats = self.i2pcore.table_name_categories
        t_posts = self.i2pcore.table_name_post

        xml_cats = ""
        categories = ""

        cats = db(db[t_cats].id > 0).select()

        for cat in cats:
            # contains bug in web2py
            post_count = db((db[t_posts].categories.contains(cat.id)) &
                            (db[t_posts].published == True) &
                            (db[t_posts].is_page == False)).count()
            if post_count <= 0:
                continue  # with 0 count not added to list

            text_cat = " %s" % cat.title
            link_cat = A(text_cat,
                        _href=URL(self.cat_controller,
                                  self.cat_function,
                                  vars={'id': cat.id,
                                        'pag': '1'}))

            xml_cat = '<li>%s <span class="sidebar_count">(%s)</span></li>' %\
                    (link_cat, post_count)

            xml_cats += xml_cat

        if xml_cats != "":
            categories = "<h4>%s</h4>" % T('Categories')
            categories += "<ul>%s</ul>" % xml_cats

        return categories

    def sidebar_categories(self):
        """ Sidebar categories """

        xml_cats = ""
        if not self.widgets_ajax:
            xml_cats = self._sidebar_categories()

        xml_categories = '<div class="sidebars" id="sidebar-categories">%s</div>' % xml_cats

        return XML(xml_categories)

    def _count_archive_post(self, month, year):
        """
        if you wanna try:
        change in sqlite similar like dis:
        update posts set created_on="2010-08-08 11:54:01",
        published_on="2010-08-08 11:54:01",
        updated_on="2010-08-08 11:54:01" where id=1;
        """

        db = self.boilerplate.db

        def last_day_of_month(date):
            if date.month == 12:
                return date.replace(day=31)
            return date.replace(month=date.month+1, day=1) - \
                   datetime.timedelta(days=1)

        t_posts = self.i2pcore.table_name_post
        d_lower = datetime.datetime(year, month, 1)
        d_upper = last_day_of_month(d_lower)

        query = ((db[t_posts].is_page == False) &
                 (db[t_posts].published == True) &
                 (db[t_posts].published_on >= d_lower) &
                 (db[t_posts].published_on <= d_upper))

        count = db(query).count()

        return count

    def _sidebar_archive(self):
        """Sidebar archive"""

        db = self.boilerplate.db
        T = current.T

        xml_archive = ''
        t_posts = self.i2pcore.table_name_post

        query = (db[t_posts].is_page == False) & \
                 (db[t_posts].published == True)
        posts = db(query).select(db[t_posts].id,
                                db[t_posts].name,
                                db[t_posts].title,
                                db[t_posts].published,
                                db[t_posts].published_on,
                                db[t_posts].updated_on,
                                db[t_posts].created_by_id,
                                db[t_posts].updated_by_id,
                                db[t_posts].markup,
                                orderby=~db[t_posts].published_on,
                                )

        calendar_list = []
        archive_list = ""
        for post in posts:
            year_full = post.published_on.strftime("%Y")
            month_full = post.published_on.strftime("%B")
            month = post.published_on.strftime("%m")
            month_year = "%s %s" % (year_full, month_full)
            if month_year not in calendar_list:
                calendar_list.append(month_year)
                count = self._count_archive_post(int(month),
                                                int(year_full))
                link_month = A(month_year,
                               _href=URL(self.archives_controller,
                                        self.archives_function,
                                        vars={'year': year_full,
                                              'month': month}))

                archive_list += '<li>%s <span class="sidebar_count">(%s)</span></li>'\
                             % (link_month, count)

        if archive_list != '':
            archive_caption = T('Archives')
            xml_archive = '<h4>%s</h4><ul>%s</ul>' % \
                        (archive_caption, archive_list)

        return xml_archive

    def sidebar_archive(self):
        """Sidebar archive"""

        archive_generate = ""
        if not self.widgets_ajax:
            archive_generate = self._sidebar_archive()
        archive_xml = '<div class="sidebars" id="sidebar-archive"> %s </div>' % \
                    archive_generate

        return XML(archive_xml)

    def _popular_tags(self, top_size=5, min_size=0):
        """Popular tags"""

        db = self.boilerplate.db
        T = current.T

        def most_common_words(items):
            words = {}
            words_gen = (word.strip(punctuation).lower() \
                         for word in items)
            for word in words_gen:
                words[word] = words.get(word, 0) + 1
            top_words = sorted(words.iteritems(),
                               key=lambda(word, count): (-count, word))
            return top_words

        t_posts = self.i2pcore.table_name_post
        xml_tags = ''
        limit_tags = self.max_tag_display

        query = ((db[t_posts].is_page == False) & \
                 (db[t_posts].published == True))
        posts = db(query).select(db[t_posts].id,
                                db[t_posts].name,
                                db[t_posts].title,
                                db[t_posts].keywords,
                                db[t_posts].published,
                                db[t_posts].published_on,
                                db[t_posts].updated_on,
                                db[t_posts].created_by_id,
                                db[t_posts].updated_by_id,
                                db[t_posts].markup,
                                orderby=~db[t_posts].published_on,
                                )

        list_tags = []
        for post in posts:
            if post.keywords:
                keywords = post.keywords
                for key in keywords:
                    list_tags.append(key)  # all tags in a list

        if list_tags != []:
            common_tags = most_common_words(list_tags)[:limit_tags]
            count_top_tag = len(common_tags)

            if count_top_tag > 0:
                steps = float(top_size - min_size) / float(count_top_tag)
            else:
                steps = 1

            acum_steps = top_size

            for word in common_tags:
                tag = word[0]
                name = (IS_SLUG()(tag))[0]
                link_search = SPAN(A(tag,
                                     _href=URL(self.tags_controller,
                                               self.tags_function,
                                               vars={'name': name})),
                                   _class="tagcloud_%s" % int(acum_steps))

                xml_tags += '<li>%s</li>' % link_search.xml()
                acum_steps -= steps

            tags_caption = T('Popular Tags')
            if xml_tags != '':
                xml_tags = '<div class="sidebars" id="popular-tags"><h4>%s</h4><ul>%s</ul></div>' % \
                (tags_caption, xml_tags)

        return xml_tags

    def sidebar_tags(self):
        """Sidebar tags"""

        tags_generate = ""
        if not self.widgets_ajax:
            tags_generate = self._popular_tags()
        tags_xml = '''<div class="sidebars" id="sidebar-tags">%s</div>
        <div style="clear: both; float: none;"></div>''' \
                    % tags_generate

        return XML(tags_xml)

    def sidebar_aboutme(self, content, title=None):
        """Sidebar about me"""

        T = current.T

        if not title:
            title = T('About me')

        xml_about = ""
        if not self.widgets_ajax:
            if str(content) != "":
                xml_about = '''<h4>%s</h4><ul>%s</ul>''' % \
                (title, content)

        xml_abouts='<div class="sidebars about-me" id="sidebar-aboutme">%s</div>' % xml_about

        return XML(xml_abouts)

    """
     SEARCH IN POSTS
    """

    def category_name(self, id):
        """Category name"""

        db = self.boilerplate.db
        t_cats = self.i2pcore.table_name_categories

        name = ''
        categories = db(db[t_cats].id == id).select()
        if categories:
            cat = categories[0]
            name = cat.title

        return name

    def last_posts(self, var_request, controller=None, function=None):
        """Last posts"""

        db = self.boilerplate.db

        t_posts = self.i2pcore.table_name_post
        limit_inf = (self.max_results_x_page * var_request['pag']) \
                  - self.max_results_x_page
        limit_sup = limit_inf + self.max_results_x_page

        query = (db[t_posts].is_page == False) & \
                 (db[t_posts].published == True)

        render_posts = ""

        count = db(query).count()
        posts = db(query).select(db[t_posts].id,
                                db[t_posts].name,
                                db[t_posts].title,
                                db[t_posts].description,
                                db[t_posts].published,
                                db[t_posts].text_slice,
                                db[t_posts].keywords_txt,
                                db[t_posts].keywords,
                                db[t_posts].categories,
                                db[t_posts].published_on,
                                db[t_posts].updated_on,
                                db[t_posts].created_by_id,
                                db[t_posts].updated_by_id,
                                db[t_posts].markup,
                                orderby=~db[t_posts].published_on,
                                limitby=(limit_inf, limit_sup)
                                )
        self.recordscount = count
        self.currentpage = var_request['pag']

        if self.comments_enabled:
            engine_comments = self.engine_comments()
        else:
            engine_comments = None

        for post in posts:
            render_posts += self.render_post_extract(post, engine_comments)

        if not controller:
            controller = self.posts_controller
        if not function:
            function = self.posts_function

        pagination = self.render_pagination(controller, function)

        widget = '''
        <div class="i2p_post_index">
        %(render_posts)s
        %(pagination)s
        <div style="clear: both;"></div>
        </div>
        ''' % {'render_posts': render_posts,
               'pagination': XML(pagination)}

        return (XML(widget), count)

    def posts_by_category(self, id, page=1, controller=None, function=None):
        """Post by category"""

        db = self.boilerplate.db

        t_posts = self.i2pcore.table_name_post
        limit_inf = (self.max_results_x_page * page) - \
                  self.max_results_x_page
        limit_sup = limit_inf + self.max_results_x_page

        query = (db[t_posts].is_page == False) & \
                 (db[t_posts].published == True) & \
                 (db[t_posts].categories.contains(id))

        render_posts = ""

        count = db(query).count()
        posts = db(query).select(db[t_posts].id,
                                db[t_posts].name,
                                db[t_posts].title,
                                db[t_posts].description,
                                db[t_posts].published,
                                db[t_posts].text_slice,
                                db[t_posts].keywords_txt,
                                db[t_posts].keywords,
                                db[t_posts].categories,
                                db[t_posts].published_on,
                                db[t_posts].updated_on,
                                db[t_posts].created_by_id,
                                db[t_posts].updated_by_id,
                                db[t_posts].markup,
                                orderby=~db[t_posts].published_on,
                                limitby=(limit_inf, limit_sup)
                                )
        self.recordscount = count
        self.currentpage = page

        if self.comments_enabled:
            engine_comments = self.engine_comments()
        else:
            engine_comments = None

        for post in posts:
            render_posts += self.render_post_extract(post, engine_comments)

        self.request_vars['id'] = id
        if not controller:
            controller = self.cat_controller
        if not function:
            function = self.cat_function

        pagination = self.render_pagination(controller, function)

        widget = '''
        <div class="i2p_post_index">
        %(render_posts)s
        %(pagination)s
        <div style="clear: both;"></div>
        </div>
        ''' % {'render_posts': render_posts,
               'pagination': XML(pagination)}

        return (XML(widget), count)

    def posts_by_tag(self, tag, page=1, controller=None, function=None):
        """Posts by tags"""

        db = self.boilerplate.db

        t_posts = self.i2pcore.table_name_post
        limit_inf = (self.max_results_x_page * page) - \
                  self.max_results_x_page
        limit_sup = limit_inf + self.max_results_x_page

        tag = tag.replace("-", " ")  # replace "-" with "space"

        query = (db[t_posts].is_page == False) & \
                 (db[t_posts].published == True) & \
                 (db[t_posts].keywords.contains(tag))

        render_posts = ""

        count = db(query).count()
        posts = db(query).select(db[t_posts].id,
                                db[t_posts].name,
                                db[t_posts].title,
                                db[t_posts].description,
                                db[t_posts].published,
                                db[t_posts].text_slice,
                                db[t_posts].keywords_txt,
                                db[t_posts].keywords,
                                db[t_posts].categories,
                                db[t_posts].published_on,
                                db[t_posts].updated_on,
                                db[t_posts].created_by_id,
                                db[t_posts].updated_by_id,
                                db[t_posts].markup,
                                orderby=~db[t_posts].published_on,
                                limitby=(limit_inf, limit_sup)
                                )
        self.recordscount = count
        self.currentpage = page

        if self.comments_enabled:
            engine_comments = self.engine_comments()
        else:
            engine_comments = None

        for post in posts:
            render_posts += self.render_post_extract(post, engine_comments)

        self.request_vars['name'] = tag
        if not controller:
            controller = self.tags_controller
        if not function:
            function = self.tags_function

        pagination = self.render_pagination(controller, function)

        widget = '''
        <div class="i2p_post_index">
        %(render_posts)s
        %(pagination)s
        <div style="clear: both;"></div>
        </div>
        ''' % {'render_posts': render_posts,
               'pagination': XML(pagination)}

        return (XML(widget), count)

    def posts_by_search(self, tag, page=1, controller=None, function=None):
        """Posts by search"""

        db = self.boilerplate.db

        t_posts = self.i2pcore.table_name_post
        limit_inf = (self.max_results_x_page * page) - \
                  self.max_results_x_page
        limit_sup = limit_inf + self.max_results_x_page

        tag = "%" + "%s" % tag.replace("-", " ") + "%"  # replace "-" with "space"

        query = (db[t_posts].is_page == False) & \
                 (db[t_posts].published == True) & \
                 (db[t_posts].description.like(tag) or \
                                             db[t_posts].title.like(tag))

        render_posts = ""

        count = db(query).count()
        posts = db(query).select(db[t_posts].id,
                                db[t_posts].name,
                                db[t_posts].title,
                                db[t_posts].description,
                                db[t_posts].published,
                                db[t_posts].text_slice,
                                db[t_posts].keywords_txt,
                                db[t_posts].keywords,
                                db[t_posts].categories,
                                db[t_posts].published_on,
                                db[t_posts].updated_on,
                                db[t_posts].created_by_id,
                                db[t_posts].updated_by_id,
                                db[t_posts].markup,
                                orderby=~db[t_posts].published_on,
                                limitby=(limit_inf, limit_sup)
                                )
        self.recordscount = count
        self.currentpage = page

        if self.comments_enabled:
            engine_comments = self.engine_comments()
        else:
            engine_comments = None

        for post in posts:
            render_posts += self.render_post_extract(post, engine_comments)

        self.request_vars['q'] = tag
        if not controller:
            controller = self.search_controller
        if not function:
            function = self.search_function

        pagination = self.render_pagination(controller, function)

        widget = '''
        <div class="i2p_post_index">
        %(render_posts)s
        %(pagination)s
        <div style="clear: both;"></div>
        </div>
        ''' % {'render_posts': render_posts,
               'pagination': XML(pagination)}

        return (XML(widget), count)

    def posts_by_archive(self, year, month, page=1,
                                controller=None, function=None):
        """Posts by archive"""

        db = self.boilerplate.db

        def last_day_of_month(date):
            if date.month == 12:
                return date.replace(day=31)
            return date.replace(month=date.month + 1, day=1) - \
                   datetime.timedelta(days=1)

        t_posts = self.i2pcore.table_name_post
        limit_inf = (self.max_results_x_page * page) - \
                  self.max_results_x_page
        limit_sup = limit_inf + self.max_results_x_page

        d_lower = datetime.datetime(year, month, 1)
        d_upper = last_day_of_month(d_lower)

        query = (db[t_posts].is_page == False) & \
                 (db[t_posts].published == True) &\
                 (db[t_posts].published_on >= d_lower) &\
                 (db[t_posts].published_on <= d_upper)

        render_posts = ""

        count = db(query).count()
        posts = db(query).select(db[t_posts].id,
                                db[t_posts].name,
                                db[t_posts].title,
                                db[t_posts].description,
                                db[t_posts].published,
                                db[t_posts].text_slice,
                                db[t_posts].keywords_txt,
                                db[t_posts].keywords,
                                db[t_posts].categories,
                                db[t_posts].published_on,
                                db[t_posts].updated_on,
                                db[t_posts].created_by_id,
                                db[t_posts].updated_by_id,
                                db[t_posts].markup,
                                orderby=~db[t_posts].published_on,
                                limitby=(limit_inf, limit_sup)
                                )

        self.recordscount = count
        self.currentpage = page

        if self.comments_enabled:
            engine_comments = self.engine_comments()
        else:
            engine_comments = None

        for post in posts:
            render_posts += self.render_post_extract(post, engine_comments)

        self.request_vars['year'] = year
        self.request_vars['month'] = month
        if not controller:
            controller = self.archives_controller
        if not function:
            function = self.archives_function

        pagination = self.render_pagination(controller, function)

        widget = '''
        <div class="i2p_post_index">
        %(render_posts)s
        %(pagination)s
        <div style="clear: both;"></div>
        </div>
        ''' % {'render_posts': render_posts,
               'pagination': XML(pagination)}

        return (XML(widget), count)

    def render_pages(self, controller='default', function='blog'):
        """ Render pages """

        T = current.T
        request = current.request

        rendered = []
        if self.recordscount > self.max_results_x_page:
            total_pages = self.recordscount // self.max_results_x_page
            if (self.recordscount % self.max_results_x_page)>0:
                total_pages += 1

            first_page = int(math.ceil(self.currentpage / self.max_display_pages)) \
                       * self.max_display_pages
            if first_page < 1:
                first_page = 1
                if total_pages < self.max_display_pages:
                    last_page = total_pages
                else:
                    last_page = self.max_display_pages
            else:
                last_page = first_page + self.max_display_pages

            backward = A(T('Prior'), _href=self.render_url_page(self.currentpage-1, controller, function), cid=request.cid)
            forward = A(T('Next'), _href=self.render_url_page(self.currentpage+1, controller, function), cid=request.cid)
            first = A(T('First'), _href=self.render_url_page(1, controller, function), cid=request.cid)
            last = A(T('Last'), _href=self.render_url_page(last_page, controller, function), cid=request.cid)

            listpages = []
            listpages.append(first)

            if self.currentpage > 1:
                listpages.append(LI(backward))

            for page in range(first_page, last_page + 1):
                page_a = A(str(page), _href=self.render_url_page(page, controller, function), cid=request.cid)
                if page <= total_pages:
                    if page == self.currentpage:
                        class_current = 'current'
                    else:
                        class_current = ''

                    listpages.append(LI(page_a, _class=class_current))

            if total_pages > self.currentpage:
                listpages.append(LI(forward))

            listpages.append(last)

            if listpages != []:
                rendered = DIV(UL(listpages), _class='pages')

        if rendered == []:
            rendered = ''

        return rendered

    def render_pagination(self, controller='default', function='blog'):
        """ Render Head """

        T = current.T

        firstresult = self.currentpage * self.max_results_x_page \
                    - self.max_results_x_page
        lastresult = self.currentpage * self.max_results_x_page
        recordscount = self.recordscount

        if recordscount < self.max_results_x_page:
            return ""
        title = '''%(displaying)s %(firstresult)s %(to)s %(lastresult)s %(of)s %(recordscount)s ''' % \
              {'displaying': T('Displaying'),
              'to': T('to'),
              'of': T('of'),
                'firstresult': firstresult + 1,
                'lastresult': lastresult,
                'recordscount': recordscount}
        divtitle = DIV(title, _class='title')
        cleardiv = DIV(_style='clear: both')
        pagination = DIV(divtitle,
                            self.render_pages(controller, function),
                            cleardiv, _class='pagination')
        return pagination

    def post_meta_by_id(self, id, allow_unpublished=False):
        """meta attributes to fill response"""

        db = self.boilerplate.db

        t_posts = self.i2pcore.table_name_post
        query = (db[t_posts].is_page == False) & \
                 (db[t_posts].id == id)

        if not allow_unpublished:
            addquery = (db[t_posts].published == True)
            query = query & addquery

        posts = db(query).select(db[t_posts].id,
                                db[t_posts].name,
                                db[t_posts].title,
                                db[t_posts].keywords_txt
                                )

        meta = {}
        if posts:
            post = posts[0]
            meta['name'] = post.name
            meta['title'] = post.title
            meta['keywords_txt'] = post.keywords_txt

        else:
            meta['name'] = ''
            meta['title'] = ''
            meta['keywords_txt'] = ''

        return meta

    def page_content(self, name):
        """Page content"""

        db = self.boilerplate.db

        t_posts = self.i2pcore.table_name_post
        query = (db[t_posts].is_page == True) & \
                 (db[t_posts].published == True) & \
                 (db[t_posts].name.like(name))
        pages = db(query).select(db[t_posts].id,
                                 db[t_posts].description,
                                 db[t_posts].markup)

        if pages:
            page = pages[0]
            return (self.render_content(page.description,
                                                markup=page.markup),
                    page.id)
        else:
            return ("", -1)

    def page_widget(self, name):
        """Page content"""

        db = self.boilerplate.db

        t_posts = self.i2pcore.table_name_post
        query = (db[t_posts].is_page == True) & \
                 (db[t_posts].published == True) & \
                 (db[t_posts].is_widget == True) & \
                 (db[t_posts].name == name)

        pages = db(query).select(db[t_posts].id,
                                 db[t_posts].description,
                                 db[t_posts].markup)

        if pages:
            page = pages[0]
            return (self.render_content(page.description,
                                                markup=page.markup),
                    page.id)
        else:
            return ("", -1)

    def default_index(self, var_request):
        """ Default Index """

        response = current.response

        self.install()  # default css

        last_posts, count = self.last_posts(var_request)
        sidebar_categories = self.sidebar_categories()
        sidebar_archive = self.sidebar_archive()
        sidebar_tags = self.sidebar_tags()
        sidebar_aboutme = self.sidebar_aboutme(self.page_widget('widget-about-me')[0])
        front_page = self.page_widget('widget-front-page')[0]
        sidebar_feed = self.sidebar_feed()
        sidebar_search = self.sidebar_search()

        return dict(last_posts=last_posts,
                    front_page=front_page,
                    sidebar_categories=sidebar_categories,
                    sidebar_archive=sidebar_archive,
                    sidebar_tags=sidebar_tags,
                    sidebar_aboutme=sidebar_aboutme,
                    sidebar_feed=sidebar_feed,
                    sidebar_search=sidebar_search)

    def default_category(self, var_request):
        """ Default category """

        response = current.response

        self.install()

        last_posts, count = self.posts_by_category(var_request['id'],
                                                 var_request['pag'])
        category_name = self.category_name(var_request['id'])

        sidebar_categories = self.sidebar_categories()
        sidebar_archive = self.sidebar_archive()
        sidebar_tags = self.sidebar_tags()
        sidebar_aboutme = self.sidebar_aboutme(self.page_widget('widget-about-me')[0])
        sidebar_feed = self.sidebar_feed()
        sidebar_search = self.sidebar_search()

        return dict(last_posts=last_posts,
                    sidebar_aboutme=sidebar_aboutme,
                    sidebar_categories=sidebar_categories,
                    sidebar_archive=sidebar_archive,
                    sidebar_tags=sidebar_tags,
                    sidebar_feed=sidebar_feed,
                    sidebar_search=sidebar_search,
                    category_name=category_name,
                    count=count)

    def default_tag(self, var_request):
        """ Default category """

        response = current.response

        self.install()
        last_posts, count = self.posts_by_tag(var_request['name'],
                                                var_request['pag'])

        sidebar_categories = self.sidebar_categories()
        sidebar_archive = self.sidebar_archive()
        sidebar_tags = self.sidebar_tags()
        sidebar_aboutme = self.sidebar_aboutme(self.page_widget('widget-about-me')[0])
        sidebar_feed = self.sidebar_feed()
        sidebar_search = self.sidebar_search()

        return dict(last_posts=last_posts,
                    sidebar_aboutme=sidebar_aboutme,
                    sidebar_categories=sidebar_categories,
                    sidebar_archive=sidebar_archive,
                    sidebar_tags=sidebar_tags,
                    sidebar_feed=sidebar_feed,
                    sidebar_search=sidebar_search,
                    tag_name=var_request['name'],
                    count=count)

    def default_search(self, var_request):
        """ Default search a query """

        response = current.response

        self.install()
        last_posts, count = self.posts_by_search(var_request['q'],
                                                    var_request['pag'])

        sidebar_categories = self.sidebar_categories()
        sidebar_archive = self.sidebar_archive()
        sidebar_tags = self.sidebar_tags()
        sidebar_aboutme = self.sidebar_aboutme(self.page_widget('widget-about-me')[0])
        sidebar_feed = self.sidebar_feed()
        sidebar_search = self.sidebar_search()

        return dict(last_posts=last_posts,
                    sidebar_aboutme=sidebar_aboutme,
                    sidebar_categories=sidebar_categories,
                    sidebar_archive=sidebar_archive,
                    sidebar_tags=sidebar_tags,
                    sidebar_feed=sidebar_feed,
                    sidebar_search=sidebar_search,
                    tag_name=var_request['q'],
                    count=count)

    def default_archives(self, var_request):
        """ Default category """

        response = current.response

        self.install()
        last_posts, count = self.posts_by_archive(var_request['year'],
                                                  var_request['month'],
                                                  var_request['pag'])
        archive_name = '%s - %s' % (var_request['year'], var_request['month'])

        sidebar_categories = self.sidebar_categories()
        sidebar_archive = self.sidebar_archive()
        sidebar_tags = self.sidebar_tags()
        sidebar_aboutme = self.sidebar_aboutme(self.page_widget('widget-about-me')[0])
        sidebar_feed = self.sidebar_feed()
        sidebar_search = self.sidebar_search()

        return dict(last_posts=last_posts,
                    sidebar_aboutme=sidebar_aboutme,
                    sidebar_categories=sidebar_categories,
                    sidebar_archive=sidebar_archive,
                    sidebar_tags=sidebar_tags,
                    sidebar_feed=sidebar_feed,
                    sidebar_search=sidebar_search,
                    archive_name=archive_name,
                    count=count)

    def default_post(self, var_request):
        """ Default post """

        response = current.response

        self.install()

        post = self.post_by_id(var_request['id'])

        meta = self.post_meta_by_id(var_request['id'])

        response.title = meta['title']
        response.keywords = meta['keywords_txt']

        sidebar_categories = self.sidebar_categories()
        sidebar_archive = self.sidebar_archive()
        sidebar_tags = self.sidebar_tags()
        sidebar_aboutme = self.sidebar_aboutme(self.page_widget('widget-about-me')[0])
        sidebar_feed = self.sidebar_feed()
        sidebar_search = self.sidebar_search()

        return dict(post=post,
                    sidebar_aboutme=sidebar_aboutme,
                    sidebar_categories=sidebar_categories,
                    sidebar_archive=sidebar_archive,
                    sidebar_tags=sidebar_tags,
                    sidebar_feed=sidebar_feed,
                    sidebar_search=sidebar_search
                    )

    def default_page(self, var_request):
        """ Default page """

        response = current.response

        self.install()

        page, id = self.page_by_name(var_request['name'])

        return dict(page=page)

    def default_pages(self):
        """ Default index pages """

        response = current.response

        self.install()

        menu = self.pages_to_menu()

        return dict(pages=menu)

    def default_rss_posts(self, page=1, results_x_page=200, full_content=False):
        """ RSS of the lasts posts """

        db = self.boilerplate.db
        T = current.T
        request = current.request
        t_posts = self.i2pcore.table_name_post

        limit_inf = (results_x_page * page) \
                  - results_x_page
        limit_sup = limit_inf + results_x_page

        query = (db[t_posts].is_page == False) & \
                 (db[t_posts].published == True)

        posts = db(query).select(db[t_posts].id,
                                db[t_posts].name,
                                db[t_posts].title,
                                db[t_posts].published,
                                db[t_posts].description,
                                db[t_posts].text_slice,
                                db[t_posts].published_on,
                                db[t_posts].updated_on,
                                db[t_posts].created_by_id,
                                db[t_posts].updated_by_id,
                                db[t_posts].markup,
                                orderby=~db[t_posts].published_on,
                                limitby=(limit_inf, limit_sup)
                                )

        entries = []
        for post in posts:
            if full_content:
                description = "%s" % self.render_content(post.description,
                                                         markup=post.markup)
            else:
                description = "%s" % self.render_content(post.text_slice,
                                                        markup=post.markup)

            entries.append(dict(title=post.title,
                            link=self.render_link_post(post, title="",
                                            anchor="",
                                            host=request.env.http_host,
                                            onlyurl=True),
                            description=description,
                            author=self.author(post.updated_by_id),
                            created_on=str(post.published_on)))

        return dict(title=app_settings.title,
                    link=URL('default', 'index'),
                    description=app_settings.description,
                    entries=entries)

    def sidebar_feed(self, title=None):
        """Sidebar feed (RSS) syndication """

        db = self.boilerplate.db
        T = current.T
        t_posts = self.i2pcore.table_name_post
        xml_feeds = ""

        if not title:
            title = T('RSS')

        if not self.widgets_ajax:
            t_posts = self.i2pcore.table_name_post
            query = (db[t_posts].is_page == False) & \
                     (db[t_posts].published == True)
            post_count = db(query).count()
            if post_count > 0 and self.show_feed:
                content = LI(A(T('Posts'),
                            _href=URL(self.feed_controller,
                                        self.feed_function))).xml()
                if self.comments_feed:
                    content += LI(A(T('Comments'),
                                    _href=URL(self.feed_comment_controller,
                                        self.feed_comment_function))).xml()
                xml_content = '''<h4>%s</h4><ul>%s</ul>''' % \
                (title, content)
            else:
                xml_content = ""

        xml_feeds = '<div class="sidebars feed" id="sidebar-feed">%s</div>' % xml_content

        return XML(xml_feeds)

    def sidebar_search(self, title=None):
        """ Search sidebar """

        T = current.T
        if not title:
            title = T('Search')

        xml_search = ""
        if not self.widgets_ajax:
            search_url = URL(self.search_controller, self.search_function)
            xml_search = '''<h4>%s</h4>
                            <form method="get" action="%s">
                            <div><input type="text" name="q" id="sidebar-search-text" value="" /></div>
                            <div><input type="submit" id="sidebar-search-submit" value="%s" /></div>
                            </form>
                            ''' % (title, search_url, title)

        search = '<div class="sidebars search" id="sidebar-search">%s</div>' % xml_search

        return XML(search)

    def render_content(self, content, markup=''):
        """ Render The content """

        if markup in ['markmin']:
            self.markmin_extra_blocks()
            return MARKMIN(content, extra=self.extra_blocks)
        elif markup in ['xml']:
            return XML(content)
        elif markup in ['markdown']:
            return markdown(content)
        elif markup in ['textile']:
            return textile(content)
        else:
            return ""

    def markmin_extra_blocks(self):
        """Extra blocks for markmin language"""

        extra = self.extra_blocks
        LATEX = '<img src="http://chart.apis.google.com/chart?cht=tx&chl=%s" align="center"/>'
        extra['latex'] = lambda code: LATEX % code.replace('"','\"')
        extra['code'] = lambda code: CODE(code, language=None).xml()
        extra['code_python'] = lambda code: CODE(code, language='python').xml()
        extra['code_c'] = lambda code: CODE(code, language='c').xml()
        extra['code_cpp'] = lambda code: CODE(code, language='cpp').xml()
        extra['code_java'] = lambda code: CODE(code, language='java').xml()
        extra['code_html_plain'] = lambda code: CODE(code, language='html_plain').xml()
        extra['code_html'] = lambda code: CODE(code, language='html').xml()
        extra['code_web2py'] = lambda code: CODE(code, language='web2py').xml()
        extra['youtube'] = lambda code: self.widget_youtube(code)
        extra['vimeo'] = lambda code: self.widget_vimeo(code)

        return extra

    def widget_latex(self, expression):
        """
        ## Uses Google charting API to embed LaTeX
        """
        return XML('<img src="http://chart.apis.google.com/chart?cht=tx&chl=%s" align="center"/>' % expression.replace('"','\"'))

    def widget_youtube(self, code, width=400, height=250):
        """
        ## Embeds a youtube video (by code)
        - ``code`` is the code of the video
        - ``width`` is the width of the image
        - ``height`` is the height of the image
        """

        return XML("""<object width="%(width)s" height="%(height)s"><param name="movie" value="http://www.youtube.com/v/%(code)s&hl=en_US&fs=1&"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="http://www.youtube.com/v/%(code)s&hl=en_US&fs=1&" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="%(width)s" height="%(height)s"></embed></object>""" % dict(code=code, width=width, height=height))

    def widget_vimeo(self, code, width=400, height=250):
        """
        ## Embeds a viemo video (by code)
        - ``code`` is the code of the video
        - ``width`` is the width of the image
        - ``height`` is the height of the image
        """
        return XML("""<object width="%(width)s" height="%(height)s"><param name="allowfullscreen" value="true" /><param name="allowscriptaccess" value="always" /><param name="movie" value="http://vimeo.com/moogaloop.swf?clip_id=%(code)s&amp;server=vimeo.com&amp;show_title=1&amp;show_byline=1&amp;show_portrait=0&amp;color=&amp;fullscreen=1" /><embed src="http://vimeo.com/moogaloop.swf?clip_id=%(code)s&amp;server=vimeo.com&amp;show_title=1&amp;show_byline=1&amp;show_portrait=0&amp;color=&amp;fullscreen=1" type="application/x-shockwave-flash" allowfullscreen="true" allowscriptaccess="always" width="%(width)s" height="%(height)s"></embed></object>""" % dict(code=code, width=width, height=height))
