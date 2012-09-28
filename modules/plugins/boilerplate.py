#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 Plugin Boilerplate
 version: 2.0
 Copyright (c) 2011 Mulone, Pablo Martin (http://martin.tecnodoc.com.ar/)
 License: MIT
"""

from gluon import *
from gluon.tools import Auth, Recaptcha
from gluon.contrib.login_methods.rpx_account import RPXAccount
from gluon.tools import Mail
from gluon.tools import Crud
from gluon.tools import Service


class BoilerPlate(object):
    """ Web2py main logic and boilerplate. Also this control the layout
    that render the view """

    def __init__(self, app_settings, db, cache=None):
        """ Init """

        self.app_settings = app_settings
        self.db = db
        self.cache = cache
        self.mail = None
        self.group_admin = 'Admin'

        self.init_app()  # init some vars

        self.auth_def = lambda: self.define_auth(self)
        self.render_flash = lambda: self.default_flash(self)
        self.render_style = lambda: self.default_style(self)
        self.render_calendar = lambda: self.default_calendar(self)
        self.render_web2py = lambda: self.default_web2py(self)
        self.render_layout = lambda: self.default_layout(self)

        self.default()

    def default(self):
        """ Default """

        request = current.request
        self.app_settings.verify_email = 'Click on the link http://'+request.env.http_host+\
            URL(r=request,c='default',f='user',args=['verify_email'])+\
            '/%(key)s to verify your email'
        self.app_settings.reset_password = 'Click on the link http://'+request.env.http_host+\
            URL(r=request,c='default',f='user',args=['reset_password'])+\
            '/%(key)s to reset your password'

    def init_app(self):
        """ The same as boiler plate for bottle but in web2py. Settings  """

        app_response = current.response  # we use response
        app_settings = self.app_settings

        app_response.scripts_ready = []
        app_response.scripts_head = []
        app_response.scripts_bottom = []
        app_response.metanames = {}

        #Metanames tags
        app_response.title = app_settings.title
        app_response.metanames['author'] = app_settings.author
        app_response.metanames['description'] = app_settings.description
        app_response.metanames['keywords'] = app_settings.keywords
        app_response.metanames['generator'] = app_settings.generator

    def render_metanames(self):
        """ Render Metanames """

        response = current.response
        metanames = response.metanames
        xml = ""
        for k, v in metanames.items():
            xml = "".join([xml, '<meta name="%s" content="%s" />\n' % (k, v)])

        return XML(xml)

    def render_scriptsonready(self):
        """ Render scripts on ready """

        response = current.response
        script = '''<script type="text/javascript">
                    jQuery(document).ready(function() { %s });
                    </script>\n''' % ("".join(response.scripts_ready))

        return XML(script)

    def render_scriptsonhead(self):
        """ Render scripts on head """

        response = current.response
        script = '''<script type="text/javascript">
                    %s
                    </script>\n''' % ("".join(response.scripts_head))

        return XML(script)

    def render_scriptsonbottom(self):
        """ Render scripts on the bottom """

        response = current.response
        script = '''<script type="text/javascript">
                    %s
                    </script>\n''' % ("".join(response.scripts_bottom))

        return XML(script)

    def default_flash(self, lambdaself):
        """ Default flash """

        response = current.response
        script = '''
            function ShowFlash(message,alertcode)
            {
            jQuery('.flash').html(message);
            if(message) jQuery('.flash').slideDown();
            };
        '''  # you can replace with your own plugin flash displaying message.

        response.scripts_head.append(script)

    def default_style(self, lambdaself):
        """ This add the default style. From getskeleton.com """
        #insert at the begining

        app_response = current.response
        app_response.files.insert(0, URL('static', 'css/base.css'))
        app_response.files.insert(1, URL('static', 'css/skeleton.css'))
        app_response.files.insert(2, URL('static', 'css/layout.css'))
        app_response.files.insert(3, URL('static', 'js/tabs.js'))

    def default_calendar(self, lambdaself):
        """ Change if you want to change files of calendar """

        app_response = current.response
        app_response.files.append(URL('static',
                                    'plugins/anytime/js/anytime.js'))
        app_response.files.append(URL('static',
                                    'plugins/anytime/css/anytime.css'))

    def default_web2py(self, lambdaself):
        """ Default web2py required this at the end """

        app_response = current.response

        # web2py required to work properly
        app_response.files.insert(0, URL('static', 'js/jquery.js'))
        app_response.files.append(URL('static', 'js/web2py_ajax.js'))
        app_response.scripts_ready.append('''jQuery('.flash').hide();
        var flash = jQuery('.flash').html();
        if(flash!='') {ShowFlash(flash,1);}''')
        app_response.scripts_ready.append('''web2py_ajax_init();''')

    def default_layout(self, lambdaself):
        """ Render layout """

        lambdaself.render_flash()
        lambdaself.render_style()
        lambdaself.render_calendar()
        lambdaself.render_web2py()

    def init_mail(self):
        """ Init Mail """

        mail = Mail()  # mailer
        mail.settings.server = self.app_settings.email_server or \
                                    'smtp.gmail.com:587'  # your SMTP server
        mail.settings.sender = self.app_settings.email_sender  # your email
        mail.settings.login = self.app_settings.email_login  # your credentials
                                                             # or None
        self.mail = mail

    def init_crud(self):
        """ Init Crud """

        db = self.db
        crud = Crud(db)
        crud.settings.auth = None  # =auth to enforce authorization on crud
        self.crud = crud

        return crud

    def init_service(self):
        """ Init Services """

        self.service = Service()

        return self.service

    def init_auth(self):
        """ Auth """

        request = current.request
        settings = self.app_settings

        auth = Auth(self.db)
        self.auth = auth
        auth.settings.hmac_key = settings.security_key  # before define_tables()

        #If I use janrain to login, disable register.
        if settings.register_method in ['Disabled', 'Janrain']:
            # disable register
            auth.settings.actions_disabled.append('register')

        # If I use Recaptcha to register.
        if settings.register_method in ['Recaptcha']:
            auth.settings.captcha = Recaptcha(request,
                                                settings.recaptcha_public_key,
                                                settings.recaptcha_private_key)

        self.auth_def()  # the auth definition

        # creates all needed tables
        auth.define_tables(username=True, migrate=settings.migrate)
        auth.settings.mailer = self.mail  # for user email verification

        if settings.register_method in ['None', 'Recaptcha', 'Approval']:
            auth.settings.registration_requires_verification = False
        else:
            auth.settings.registration_requires_verification = True

        if settings.register_method in ['Approval']:
            auth.settings.registration_requires_approval = True
        else:
            auth.settings.registration_requires_approval = False

        auth.settings.reset_password_requires_verification = True

        if settings.register_method in ['Janrain']:
            base_http = 'http://' + str(request.env.http_host)
            auth.settings.actions_disabled = ['register',
                                              'change_password',
                                              'request_reset_password']
            auth.settings.login_form = RPXAccount(request,
                                            api_key=settings.janrain_api_key,
                                            domain=settings.janrain_domain,
                                            url=base_http + \
                                            '/%s/default/user/login' % \
                                            request.application)

        auth.messages.verify_email = settings.verify_email
        auth.messages.reset_password = settings.reset_password

        return auth

    def define_auth(self, lambdaself):
        """ Define Auth """

        db = lambdaself.db
        request = current.request
        settings = lambdaself.app_settings
        auth = lambdaself.auth
        T = current.T

        #Add your own users fields
        db.define_table('auth_user',
            Field('id', 'id'),
            Field('username', type='string',
                  label=T('Username')),
            Field('first_name', type='string',
                  label=T('First Name')),
            Field('last_name', type='string',
                  label=T('Last Name')),
            Field('email', type='string',
                  label=T('Email')),
            Field('password', type='password',
                  readable=False,
                  label=T('Password')),
            Field('created_on', 'datetime', default=request.now,
                  label=T('Created On'), writable=False, readable=False),
            Field('modified_on', 'datetime', default=request.now,
                  label=T('Modified On'), writable=False, readable=False,
                  update=request.now),
            Field('registration_key', default='',
                  writable=False, readable=False),
            Field('reset_password_key', default='',
                  writable=False, readable=False),
            Field('registration_id', default='',
                  writable=False, readable=False),
            format='%(username)s',
            migrate=settings.migrate)

        db.auth_user.first_name.requires = \
                            IS_NOT_EMPTY(error_message=auth.messages.is_empty)
        db.auth_user.last_name.requires = \
                            IS_NOT_EMPTY(error_message=auth.messages.is_empty)
        db.auth_user.password.requires = \
                            CRYPT(key=auth.settings.hmac_key)
        db.auth_user.username.requires = \
                            IS_NOT_IN_DB(db, db.auth_user.username)
        db.auth_user.registration_id.requires = \
                            IS_NOT_IN_DB(db, db.auth_user.registration_id)
        db.auth_user.email.requires = \
                        (IS_EMAIL(error_message=auth.messages.invalid_email),
                       IS_NOT_IN_DB(db, db.auth_user.email))

    def navbar(self):
        """ Auth nav bar """

        navbar = ""
        try:
            navbar = self.auth.navbar(action=URL('default', 'user'))
            navbar = str(str(navbar.xml()).replace('[', '')).replace(']', '')
            navbar = XML(str(navbar).replace('|',
                                    '<span class="auth_separator">|</span>'))
        except:
            pass

        return navbar

    def authbar(self):
        """New auth bar"""

        T = current.T

        action = URL('default', 'user')
        logout = A(T('Logout'), _href=action + '/logout')
        profile = A(T('Profile'), _href=action + '/profile')
        login = A(T('Log in'), _href=action + '/login')
        register = A(T('Register'), _href=action + '/register')

        if self.auth.is_logged_in():
            content = SPAN(profile, SPAN('|', _class='auth_separator'), logout, _class='auth_navbar')
        else:
            content = SPAN(login, SPAN('|', _class='auth_separator'), register, _class='auth_navbar')
        return content

    def isadmin(self):
        """ Check if user is admin """

        return self.auth.has_membership(self.auth.id_group(self.group_admin))

    def check_first_time(self):
        """ Check if there are no users """

        db = self.db
        if db(db.auth_user.id > 0).count() > 0:
            return
        else:
            redirect(URL('users', 'index'))
