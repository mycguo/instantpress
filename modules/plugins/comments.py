#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 Plugin Comments  https://bitbucket.org/mulonemartin/instantpress/
 version: 2.0
 Copyright (c) 2011 Mulone, Pablo Martin (http://martin.tecnodoc.com.ar/)
 License: MIT

 NOTE: ONly working with markmin language.
"""

import math
import cStringIO
import os

from gluon import *
from gluon.tools import prettydate
from gluon.compileapp import LoadFactory

# We use markitup in the editor
from plugins.markitup import PluginMarkitup
from appsettings import app_settings


class PluginComments(object):
    """ Plugin comments """

    def __init__(self, boilerplate):
        """ Init """

        request = current.request

        self.boilerplate = boilerplate
        self.migrate = True

        self.tablename = 'default'
        self.record_id = 0
        self.controller_name = 'comments'

        #don't change cause will broke things
        self.table_comments = 'plugin_comments_comments'
        self.table_profiles = 'plugin_comments_profiles'
        self.table_notifications = 'plugin_comments_notifications'
        self.table_votes = 'plugin_comments_votes'
        self.table_flags = 'plugin_comments_flags'
        self.max_results_x_page = 10
        self.max_display_pages = 5
        self.avatar_size = 32
        self.group_admin = 'Admin'

        self.recordscount = 0
        self.currentpage = 1
        self.request_vars = {}

        self.url_logout = URL(request.application, 'default', 'user/logout', extension=0)
        self.url_login = URL(request.application, 'default', 'user/login', extension=0)
        self.url_register = URL(request.application,'default','user/register',extension=0)

        self.notificationfunc = lambda reply_id: self.notification(reply_id)
        self.pageurlfunction = lambda page: self.render_url_page(page)
        self.render_text_editor = lambda: self.render_editor()
        self.render_markup_comment = lambda content: self.render_comment(content)

        self.site_name = app_settings.title
        self.site_mail = app_settings.author_email
        self.site_description = app_settings.description

        self.storage_upload = os.path.join(request.folder, 'static', 'avatars')
        self.url_avatar = lambda avatar: self.static_upload_folder(avatar)

    def static_upload_folder(self, image):
        """ Generate image download """

        v_path = image.split('.')
        return URL('static', 'avatars',
                args=[v_path[0] + '.' + v_path[1],
                      v_path[2][:2],
                      image], extension=0)

    def install(self):
        """Install the plugins create the tables if necesary"""

        db = self.boilerplate.db
        auth = self.boilerplate.auth
        T = current.T
        request = current.request

        db.define_table(self.table_comments,
                        Field('id', 'id'),
                        Field('tablename', required=True, notnull=True,
                              writable=False, readable=False),
                        Field('record_id', 'integer', required=True,
                            notnull=True, writable=False, readable=False),
                        Field('author_id', db.auth_user, default=auth.user_id,
                              notnull=True, writable=False, readable=False),
                        Field('author_name', 'string', length=255, default="",
                              label=T("Your name"), comment=T("Your name")),
                        Field('author_email', 'string', length=255, default="",
                              label=T("Your email"), comment=T("Your email")),
                        Field('author_url', 'text', default=""),
                        Field('reply_id', 'integer', default=0),
                        Field('approved', 'boolean', default=True),
                        Field('comment', 'text', default="", required=True,
                              notnull=True,
                              requires=[IS_NOT_EMPTY(), IS_LENGTH(2**28)],
                              label=T("Your comment")),
                        Field('comment_on', 'datetime', default=request.now,
                              writable=False, readable=False),
                        migrate=self.migrate)

        db.define_table(self.table_profiles,
                        Field('id', 'id'),
                        Field('author_id', db.auth_user, default=auth.user_id,
                              notnull=True, writable=False, readable=False),
                        Field('display_name', 'string', length=255, default="",
                              label=T("Display name"),
                              comment=T("The name you want to be displayed in comments")),
                        Field('avatar_image', 'upload', default="",
                                uploadseparate=True,
                              autodelete=True, label=T('Avatar'),
                              comment=T('Choose an image ".jpg",".png",".gif"'),
                              uploadfolder=self.storage_upload,
                              requires=[IS_IMAGE(),
                                          RESIZE_IMAGE(self.avatar_size,
                                                      self.avatar_size)]),
                        Field('avatar_upload_on', 'datetime', default=request.now,
                              writable=False, readable=False),
                        Field('avatar_up_count', 'integer', default=0,
                              writable=False, readable=False),
                        Field('notification', 'boolean', default=True,
                              label=T("Notification"),
                              comment=T("You want to be notified by mail?")),
                        Field('url_site', 'string', length=512, default="",
                              label=T('Your home site'),
                              comment=T("Url of your site ex: http://www.mysite.com"),
                              requires=(IS_URL())),
                        migrate=self.migrate)

        db.define_table(self.table_notifications,
                        Field('id', 'id'),
                        Field('tablename', required=True, notnull=True,
                              writable=False, readable=False),
                        Field('record_id','integer', required=True,
                                notnull=True, writable=False, readable=False),
                        Field('author_id', db.auth_user, default=auth.user_id,
                              notnull=True, writable=False, readable=False),
                        Field('send', 'boolean', default=False),
                        Field('success', 'boolean', default=False),
                        Field('sendit_at', 'datetime', default=request.now),
                        migrate=self.migrate)

        db.define_table(self.table_votes,
                        Field('id', 'id'),
                        Field('tablename', required=True, notnull=True,
                              writable=False, readable=False),
                        Field('record_id', 'integer', required=True,
                                notnull=True, writable=False, readable=False),
                        Field('author_id', db.auth_user, default=auth.user_id,
                              notnull=True, writable=False, readable=False),
                        Field('comment_id','integer', required=True,
                            notnull=True, writable=False, readable=False),
                        Field('vote', 'integer', default=0),
                        Field('vote_at', 'datetime', default=request.now),
                        migrate=self.migrate)

        db.define_table(self.table_flags,
                        Field('id', 'id'),
                        Field('tablename', required=True, notnull=True,
                              writable=False, readable=False),
                        Field('record_id', 'integer', required=True,
                                notnull=True, writable=False, readable=False),
                        Field('author_id', db.auth_user, default=auth.user_id,
                              notnull=True, writable=False, readable=False),
                        Field('comment_id', 'integer', writable=False,
                            readable=False),
                        Field('type', 'integer', default=0),
                        Field('time', 'datetime', default=request.now),
                        migrate=self.migrate)

        return self

    def uninstall(self):
        """To uninstall the plugin
        WARNING:
        This will delete the information in the tables
        """
        db = self.boilerplate.db

        tables = [self.table_comments,
                self.table_profiles,
                self.table_notifications,
                self.table_votes,
                self.table_flags]

        for table in tables:
            try:
                db[table].drop()
            except KeyError:
                query = 'DROP TABLE %s;' % table
                db.executesql(query)

    def render(self, id=0, tablename="default", page=1, order=0):
        """ Render the comments DIVS """

        response = current.response
        response.files.append(URL('static', 'plugins/comments/css/plugin.comments.css'))
        response.files.append(URL('static', 'plugins/comments/js/plugin.comments.js'))

        self.tablename = tablename
        self.record_id = id

        self.render_scripts()
        self.render_text_editor()

        environment = {}
        environment['request'] = current.request
        environment['response'] = current.response
        LOAD = LoadFactory(environment)
        return LOAD(self.controller_name, 'comments',
                    vars={'tablename': tablename,
                        'record_id': id,
                        'page': page,
                        'order': order},
                    ajax=True)

    def render_scripts(self):
        """ Needit javascript """

        response = current.response
        request = current.request

        response.scripts_head.append('''
        var plg_comments_static = "%(static)s";
        var plg_comments_showcomment = "%(showcomment)s";
        ''' % {
               'static': URL(r=request, c='static', f='plugins/comments/images/'),
               'showcomment': URL(self.controller_name, 'comment_id')
           })

    def render_editor(self):
        """ Markit up editor """

        markitup = PluginMarkitup(self.boilerplate)
        script = markitup.render_editor('#%s_comment' % self.table_comments, markup='markmin', onready=False)
        return script

    def render_comment(self, content):
        """ Render the commentn """

        return MARKMIN(content)

    def render_pages(self):
        """ Render pages """

        T = current.T
        request = current.request

        rendered =[]
        if self.recordscount>self.max_results_x_page:
            total_pages = self.recordscount // self.max_results_x_page
            if (self.recordscount % self.max_results_x_page)>0:
                total_pages += 1

            first_page = int(math.ceil(self.currentpage / self.max_display_pages)) \
                       * self.max_display_pages
            if first_page<1:
                first_page=1
                if total_pages < self.max_display_pages:
                    last_page = total_pages
                else:
                    last_page=self.max_display_pages
            else:
                last_page=first_page + self.max_display_pages

            backward=A(T('Prior'), _href=self.pageurlfunction(self.currentpage-1), cid=request.cid)
            forward=A(T('Next'), _href=self.pageurlfunction(self.currentpage+1), cid=request.cid)
            first=A(T('First'), _href=self.pageurlfunction(1), cid=request.cid)
            last=A(T('Last'), _href=self.pageurlfunction(last_page), cid=request.cid)

            listpages=[]
            listpages.append(first)

            if self.currentpage>1:
                listpages.append(LI(backward))

            for page in range(first_page, last_page+1):
                page_a=A(str(page), _href=self.pageurlfunction(page), cid=request.cid)
                if page<=total_pages:
                    if page==self.currentpage:
                        class_current = 'current'
                    else:
                        class_current = ''

                    listpages.append(LI(page_a,_class=class_current))

            if total_pages>self.currentpage:
                listpages.append(LI(forward))

            listpages.append(last)

            if listpages!=[]:
                rendered=DIV(UL(listpages),_class='pages')

        if rendered==[]:
            rendered=''

        return rendered

    def render_pagination(self):
        """ Render Head """

        T = current.T

        firstresult = self.currentpage * self.max_results_x_page \
                    - self.max_results_x_page
        lastresult = self.currentpage * self.max_results_x_page
        recordscount = self.recordscount
        title = '''%(displaying)s %(firstresult)s %(to)s %(lastresult)s %(of)s %(recordscount)s ''' % \
              {'displaying': T('Displaying'),
              'to': T('to'),
              'of': T('of'),
                'firstresult': firstresult,
                'lastresult': lastresult,
                'recordscount': recordscount}
        divtitle = DIV(title, _class='title')
        cleardiv = DIV(_style='clear: both')
        pagination = DIV(divtitle, self.render_pages(), cleardiv,
                        _class='pagination')
        return pagination

    def render_url_page(self, page):
        """ Generate the url to a page """

        request = current.request

        rq_vars = self.request_vars.copy()
        rq_vars['page'] = page

        return URL(self.controller_name, 'comments', vars=rq_vars)

    def orderbydate(self):
        """Order by date"""

        request = current.request
        T = current.T

        rq_vars = self.request_vars.copy()
        rq_vars['order'] = 0
        return A(T("date"), _href=URL(self.controller_name,
                                   'comments',
                                   vars=rq_vars),
                                    _title=T("order by date"),
                cid=request.cid)

    def orderbyvotes(self):
        """Order by votes"""

        request = current.request
        T = current.T

        rq_vars = self.request_vars.copy()
        rq_vars['order'] = 1
        return A(T("most voted"), _href=URL(self.controller_name,
                                   'comments',
                                   vars=rq_vars),
                _title=T("order by most voted"),
                cid=request.cid)

    def get_user_avatar(self, author_id, style=""):
        """ Get User Avatar """

        db = self.boilerplate.db
        T = current.T

        img = IMG(_src=URL('static',
                           'plugins/comments/images/avatar_%s.png' % \
                                           self.avatar_size),
                  alt="User avatar", _title=T('No avatar'), _style=style)

        table_profiles = db[self.table_profiles]

        query = (table_profiles.author_id == author_id)
        profiles = db(query).select()

        style += " width: %(size)spx; height: %(size)spx;" % \
                                {'size': self.avatar_size}

        if profiles:
            profile = profiles[0]
            img_avatar = profile.avatar_image
            if img_avatar:
                url_avatar = self.url_avatar(img_avatar)
                img = IMG(_src=url_avatar, alt="User avatar", \
                          _title='User avatar',
                          _style=style)

        return img

    def generate_title(self, comments_count):
        """ Generate title """

        T = current.T

        if comments_count == 0:
            text_response = T('No Responses')
        elif comments_count == 1:
            text_response = "1 %s" % T('Response')
        elif comments_count > 1:
            text_response = "%s %s" % (comments_count, T('Responses'))

        title_comment = '<h2>%s</h2> %s' % (text_response,
                            T('You can reply leaving your comment.'))

        return XML(title_comment)

    def generate_comment_on(self, comment_on):
        """Generate on"""

        return prettydate(comment_on)

    def is_admin(self):
        """ Is an Admin user """

        auth = self.boilerplate.auth
        return auth.has_membership(auth.id_group(self.group_admin))

    def generate_buttons(self, id):
        """Generate buttons"""

        T = current.T

        admin_delete = ''
        link_reply = A(SPAN(_class='comments icon'), T("Reply"), _href='javascript: void(0);', \
                           _onclick="ShowReplyBox(%s);" % (id),_class='button2')
        link_flag = A(SPAN(_class='rosette icon'), T("Flag"), _href='javascript: void(0);', \
                           _onclick="alert('Not implemented, yet!');", _class='button2')
        if self.is_admin():
            admin_delete = (A(SPAN(_class='comment_delete icon'), T("Delete")\
                        ,_href="javascript: void(0);", \
                        _onclick="if(!confirm('Warning!!!. Are you sure you want to delete this\
                        comment?.')){ return } ajax('%s', [], ':eval');"%
                                            (URL(self.controller_name,"delete_comment",args=[id])),\
                        _title='Remove comment',
                        _class='button2')).xml()

        buttons = "%s %s" % (link_reply, admin_delete)
        buttons = XML(buttons)
        return buttons

    def get_user_title(self, id, link=True):
        """ Get user title """

        db = self.boilerplate.db

        user_title = ""

        query = (db.auth_user.id == id)
        qleft = (db[self.table_profiles].on(db.auth_user.id ==\
                                        db[self.table_profiles].author_id))

        users = db(query).select(
            db.auth_user.last_name,
            db.auth_user.first_name,
            db[self.table_profiles].display_name,
            db[self.table_profiles].url_site,
            left=qleft)
        if users:
            user = users[0]
            if user[self.table_profiles].display_name:
                user_label = user[self.table_profiles].display_name
            else:
                user_label = "%s %s" % (user['auth_user'].first_name,
                                        user['auth_user'].last_name)

            if user[self.table_profiles].url_site and link:
                user_title = A(user_label,
                                _href=user[self.table_profiles].url_site)
            else:
                user_title = user_label

        return user_title

    def count_votes(self, comment_id):
        """ Count Votes"""

        db = self.boilerplate.db

        count = 0
        table_votes = db[self.table_votes]
        tablename = self.tablename
        record_id = self.record_id

        query = ((table_votes.tablename == tablename) & \
                (table_votes.record_id == record_id) & \
                (table_votes.comment_id == comment_id))

        votes = db(query).select()

        for vote in votes:
            count += vote.vote

        return count

    def count_votes_user(self, user_id):
        """ Count votes user """

        db = self.boilerplate.db

        count = 0
        table_votes = db[self.table_votes]
        tablename = self.tablename
        record_id = self.record_id

        query = ((table_votes.tablename == tablename) & \
                (table_votes.record_id == record_id) & \
                (table_votes.author_id == user_id))

        votes = db(query).select()

        for vote in votes:
            count += vote.vote

        return count

    def form_profile(self):
        """ Form profile """

        db = self.boilerplate.db
        T = current.T
        session = current.session
        request = current.request
        response = current.response

        user_id = session.auth.user.id
        table_profiles = db[self.table_profiles]

        query = (table_profiles.author_id == user_id)
        profiles = db(query).select()

        if profiles:  # if not exist create the record
            idprofile = profiles[0].id
        else:
            idprofile = table_profiles.insert(author_id=user_id)

        form = SQLFORM(table_profiles, idprofile, showid=False)
        if form.accepts(request.vars, session):
            response.flash = T('Your profile was updated!')

        return form

    def vote_comment(self, comment_id, vote=1):
        """ Vote comment """

        db = self.boilerplate.db
        T = current.T
        session = current.session
        request = current.request

        user_id = session.auth.user.id
        table_votes = db[self.table_votes]
        tablename = self.tablename
        record_id = self.record_id

        query = ((table_votes.tablename == tablename) & \
                (table_votes.record_id == record_id) & \
                (table_votes.author_id == user_id) & \
                (table_votes.comment_id == comment_id))

        votes = db(query).select()
        if not votes:
            newid = table_votes.insert(tablename=tablename, \
                                       record_id=record_id, \
                                       author_id=user_id, \
                                       comment_id=comment_id, \
                                       vote=vote)
            message = T('You have vote!')
        else:
            message = T("You already vote this one")

        return message

    def form_reply(self, tablename, record_id):
        """ Form Reply """

        db = self.boilerplate.db
        T = current.T
        request = current.request
        auth = self.boilerplate.auth
        session = current.session
        response = current.response

        if auth.is_logged_in():
            table_comments = db[self.table_comments]
            form = SQLFORM(table_comments,
                           fields=['comment', 'reply_id'],
                           formstyle="divs")
            form.vars.tablename = tablename
            form.vars.record_id = record_id
            if form.accepts(request.vars, session):
                #for hackers who want to play messing
                 #with reply id, check is valid
                reply_id = request.vars.reply_id
                if reply_id != 0:
                    query = ((table_comments.tablename == tablename) & \
                             (table_comments.record_id == record_id) & \
                             (table_comments.id == reply_id))
                    count = db(query).count()
                    if count <= 0:
                        request.vars.reply_id = 0
                    else:
                        #notification by email to replyier
                        self.notificationfunc(reply_id)

                response.flash = T('Thank you for your reply!')

            link_profile = A(T("My profile"),
                        _href=URL(self.controller_name, 'profile', extension=0))
            link_logout = A(T("Logout"), _href=self.url_logout)
            div_form = DIV(link_profile, " | ", link_logout, form)

        else:

            login_link = A(T("Sign in"), _href=self.url_login)
            register_link = A(T("Register"), _href=self.url_register)

            need_login = T('You have to %s to your account before comment.') % \
                        login_link.xml()
            register_action = T("If you don't have an account you can %s one.") % \
                            register_link.xml()
            form = "%s %s" % (need_login, register_action)
            div_form = XML(form)

        return div_form

    def in_reply_to(self, reply_id, current_id):
        """ In reply to """

        db = self.boilerplate.db

        if reply_id == 0:
            return ""

        in_reply_to = ""
        tablename = self.tablename
        record_id = self.record_id

        table_comments = db[self.table_comments]
        query = ((table_comments.tablename == tablename) & \
                 (table_comments.record_id == record_id) & \
                 (table_comments.id == reply_id))
        comments = db(query).select()
        if comments:
            comment = comments[0]
            user_title = self.get_user_title(comment.author_id, link=False)
            user_title_link = A(user_title,
                                _href="javascript: void(0);",
                                _onclick="ShowBoxContent(%s,%s);" % \
                                            (reply_id, current_id))
            in_reply_to = T('In reply to %s') % (user_title_link.xml())
            in_reply_to = XML(in_reply_to)

        return in_reply_to

    def comment_comment(self, comment_id):
        """ Comment Comment"""

        db = self.boilerplate.db

        table_comments = db[self.table_comments]
        tablename = self.tablename
        record_id = self.record_id

        query = ((table_comments.tablename == tablename) & \
                 (table_comments.record_id == record_id) & \
                 (table_comments.id == comment_id))

        body = ""
        comments = db(query).select()
        if comments:
            comment = comments[0]
            body = comment.comment

        return body

    def recordid_count(self, tablename, record_id):
        """ Record count """

        db = self.boilerplate.db

        table_comments = db[self.table_comments]

        query = ((table_comments.tablename == tablename) & \
                 (table_comments.record_id == record_id))

        return db(query).count()

    def comments(self, tablename, record_id, currentpage, order):
        """ Comments from the db """

        db = self.boilerplate.db
        max_comments = self.max_results_x_page

        limit_inf = (max_comments * currentpage) - max_comments
        limit_sup = limit_inf + max_comments

        table_comments = db[self.table_comments]
        query = (db[self.table_comments].tablename == tablename) & \
                 (db[self.table_comments].record_id == record_id)
        qleft = (db[self.table_votes].on(db[self.table_comments].id ==\
                                        db[self.table_votes].comment_id))

        if order == 0:
            orderby = ~db[self.table_comments].comment_on
        else:
            orderby = ~db[self.table_votes].id.count()

        count = db(query).count()
        comments = db(query).select(
            db[self.table_comments].id,
            db[self.table_comments].tablename,
            db[self.table_comments].record_id,
            db[self.table_comments].author_id,
            db[self.table_comments].reply_id,
            db[self.table_comments].comment,
            db[self.table_comments].comment_on,
            db[self.table_votes].id.count(),
            left=qleft,
            groupby=db[self.table_comments].id,
            orderby=orderby,
            limitby=(limit_inf, limit_sup))

        self.recordscount = count
        self.currentpage = currentpage

        return (count, comments)

    def delete_comment(self, idcomment):
        """ Delete a comment """

        db = self.boilerplate.db
        T = current.T

        db(db[self.table_comments].id == idcomment).delete()
        message = T("Comment has been deleted!")

        return message

    def notification(self, reply_id):
        """Super simple message notification"""

        if not hasattr(self.boilerplate, 'mail'):
            return

        mail = self.boilerplate.mail
        db = self.boilerplate.db
        request = current.request

        base_http = 'http://' + str(request.env.http_host)

        query = (db[self.table_comments].author_id == db.auth_user.id) & \
              (db[self.table_comments].id == reply_id)

        users = db(query).select(db.auth_user.email)
        if users:
            user = users[0]

            noti_subject = "The are a new reply to your comment [%s]" %\
                        self.site_name
            noti_template = '''
            The are a new reply to your comment. Please visit %(url)s to view it.
            '''
            message = noti_template % {'url': base_http}
            mail.settings.sender = self.site_mail

            mail.send(user.email, noti_subject, message)  # send the email

    def rss(self, tablename="default", page=1,
            results_x_page=300,
            site_title="Comment system",
            site_link="http://www.myursite.com/",
            site_description="my desctiption"):
        """ RSS of the lasts comments """

        db = self.boilerplate.db
        T = current.T
        request = current.request
        table_comments = db[self.table_comments]

        limit_inf = (results_x_page * page) \
                  - results_x_page
        limit_sup = limit_inf + results_x_page

        query = (db[self.table_comments].tablename == tablename)

        comments = db(query).select(
            db[self.table_comments].id,
            db[self.table_comments].tablename,
            db[self.table_comments].record_id,
            db[self.table_comments].author_id,
            db[self.table_comments].reply_id,
            db[self.table_comments].comment,
            db[self.table_comments].comment_on,
            orderby=~db[self.table_comments].comment_on,
            limitby=(limit_inf, limit_sup))

        entries = []
        for comment in comments:
            entries.append(dict(title=comment.comment[:70],
                            link="",
                            description="%s" %\
                                self.render_markup_comment(comment.comment),
                            author=self.get_user_title(comment.author_id,
                                                        link=False),
                            created_on=str(comment.comment_on)))

        return dict(title=site_title,
                    link=site_link,
                    description=site_description,
                    entries=entries)


class RESIZE_IMAGE(object):
    """ This is from here:
    http://www.web2pyslices.com/main/slices/take_slice/62
    """
    def __init__(self, nx=64, ny=64, error_message='Error'):
        (self.nx, self.ny, self.error_message) = (nx, ny, error_message)

    def __call__(self, value):
        if isinstance(value, str) and len(value) == 0:
            return (value, None)
        from PIL import Image
        try:
            img = Image.open(value.file)
            img.thumbnail((self.nx, self.ny), Image.ANTIALIAS)
            s = cStringIO.StringIO()
            img.save(s, 'JPEG', quality=100)
            s.seek(0)
            value.file = s
        except:
            return (value, self.error_message)
        else:
            return (value, None)
