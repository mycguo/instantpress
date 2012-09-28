#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 Instant Press  https://bitbucket.org/mulonemartin/instantpress/
 Copyright (c) 2011 Mulone, Pablo Martin
 License: MIT
"""

from gluon.storage import Storage

app_settings = Storage()
app_settings.migrate = True
app_settings.title = 'Instantpress 2.1.2'
app_settings.subtitle = 'powered by Instantpress 2.1.2'
app_settings.author = 'Martin Mulone'
app_settings.author_email = 'blabla@mail.com'
app_settings.keywords = 'Instantpress, Powerpack, Boilerplate, web2py, application'
app_settings.generator = 'Web2py Framework'
app_settings.copyright = 'Copyright 2011'
app_settings.description = 'Instant press application App'
app_settings.database_uri = 'sqlite://storage.sqlite'
app_settings.security_key = '241ab211-ba3c-4692-1e99-63712f2a2b75'
app_settings.email_server = 'logging'  # localhost
app_settings.email_sender = 'you@example.com'
app_settings.email_login = None  # "username:password" or None
app_settings.login_method = 'local'
app_settings.login_config = ''

"""
 REGISTER_METHOD:
 ----------------
 'Disabled' : Nobody can register
 'Verification': Verification here mean: mail verification
 'Approval': Approval need an admin approval
 'Recaptcha': Recaptcha verify that is not a bot?
 'Janrain': Recaptcha verify that is not a bot?
 'None': No verification, never use in production
"""
app_settings.register_method = 'None'

"""
 Recaptcha settings
"""
app_settings.recaptcha_public_key = 'PUBLIC_KEY'
app_settings.recaptcha_private_key = 'PRIVATE_KEY'

"""
 Janrain settings
"""
app_settings.janrain_api_key = 'JANRAIN_API_KEY'
app_settings.janrain_domain = 'JANRAIN_DOMAIN'

"""
 GA Google analytics
"""
app_settings.ga_id = 'UA-XXXXX-X'

"""
Instantpress Settings
"""

"""
 Instantpress Editor
 'markitup': The common markitup
 'cleditor': The new one
"""
app_settings.i2p_editor = 'cleditor'
