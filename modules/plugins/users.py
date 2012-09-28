#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 Plugin Users
 version: 2.0
 Copyright (c) 2011 Mulone, Pablo Martin (http://martin.tecnodoc.com.ar/)
 License: BSD
"""

import string
from random import choice
from gluon import *

from plugins.admin import admin_ui


class PluginUsers(object):
    """ Plugin users """

    def __init__(self, boilerplate):
        """ Init """

        self.boilerplate = boilerplate
        self.admin_group = 'Admin'
        self.rec_x_pag = 10
        self.controller_name = 'users'

    def url_pages(self, var_request, page=1, controller='default',
                                            function='default'):
        """ Url pages function """

        var_request['pag'] = page
        return URL(controller, function, vars=var_request)

    def autoadmin(self):
        """ Auto admin """

        db = self.boilerplate.db
        auth = self.boilerplate.auth
        T = current.T

        #if there are only one user
        #check for groups need if not exist create it.
        #give proper rights to the first user in auth_user

        gen_pass = ''

        if db(db.auth_user.id > 0).count() == 0:
            # random password generate
            size = 9
            gen_pass = ''.join([choice(string.letters + string.digits) for i in range(size)])
            gen_emailhost = ''.join([choice(string.letters + string.digits) for i in range(6)])
            gen_email = ''.join([choice(string.letters + string.digits) for i in range(5)])

            id_user = self.add_manual('Firstname',
                                    'Lastname',
                                    '%s@%s.com' % (gen_email, gen_emailhost),
                                    'Admin',
                                    gen_pass)

            if id_user > 0:
                g_admin = self.required_group(self.admin_group,
                               description=T('Admin group. All privilege'))
                auth.add_membership(g_admin, id_user)
            else:
                gen_pass = ""

        return gen_pass

    def required_group(self, role, description='The description of this group'):
        """ Required group """

        auth = self.boilerplate.auth
        id_group = auth.id_group(role)
        if id_group > 0:
            return id_group
        else:
            id_group = auth.add_group(role, description)
            return id_group

    def exist_admin_group(self):
        """Exist admin group?"""

        auth = self.boilerplate.auth
        return auth.id_group(self.admin_group)

    def add_manual(self, first_name, last_name, email, username, passw):
        """Add user manually"""

        db = self.boilerplate.db
        auth = self.boilerplate.auth

        users = db((db.auth_user.email == email) | \
                   (db.auth_user.username == username)).select()
        if users:
            return users[0].id
        else:
            my_crypt = CRYPT(key=auth.settings.hmac_key)
            crypt_pass = my_crypt(passw)[0]
            id_user = db.auth_user.insert(
                                       first_name=first_name,
                                       last_name=last_name,
                                       email=email,
                                       username=username,
                                       password=crypt_pass
                                       )
            return id_user

    def represent(self):
        """ Represent """

        auth = self.boilerplate.auth
        T = current.T
        db = self.boilerplate.db

        def status(value, row):
            """ Status """

            id_group_admin = auth.id_group('Admin')
            if row.registration_key == 'pending':
                caption_status = '<span style="color: orange;" title="%s">%s</span>'%(T('Pending'),value)
            elif row.registration_key == 'disabled':
                caption_status = '<span style="color: orange;" title="%s">%s</span>'%(T('Disabled'),value)
            elif row.registration_key == 'blocked':
                caption_status =  '<span style="color: orange;" title="%s">%s</span>'%(T('Block'),value)
            else:
                caption_status = '<span style="color: green;" title="%s">%s</span>'%(T('Active'),value)

            if auth.has_membership(id_group_admin, row.id, 'Admin'):
                caption_status = '<span style="color: red;" title="%s">%s</span>'%(T('Admin'),value)

            return XML(caption_status)

        db.auth_user.username.represent = lambda value, row: status(value, row)

    def index(self):
        """ Index"""

        db = self.boilerplate.db
        T = current.T

        self.represent()

        query = (db.auth_user.id > 0)
        fields = [db.auth_user.id,
                  db.auth_user.username,
                  db.auth_user.email,
                  db.auth_user.created_on
                  ]

        links = [lambda row: \
                A(SPAN(_class='icon activate'), SPAN(T('Activate')),
              _href="javascript: void(0);",
              _onclick="if(!confirm('%s')){ return } ajax('%s', [], ':eval');" %\
              (T('Activate this user?'),
                  URL(self.controller_name, "activate", args=[row.id])),
              _title=T('Activate user'), _class='w2p_trap button16'),
                 lambda row: \
                 A(SPAN(_class='icon disable'), SPAN(T('Disable')),
                     _href="javascript: void(0);",
                    _onclick="if(!confirm('%s')){ return } ajax('%s', [], ':eval');" %\
                    (T('Disable user?'),
                        URL(self.controller_name, "disable", args=[row.id])),
                    _title=T('Disable user?'), _class='w2p_trap button16'),
                 lambda row: A(SPAN(_class='icon group'), SPAN(T('Membership')),
                        _href=URL(self.controller_name,
                                  'membership',
                                  args=[row.id]),
                        _title=T('Memberships of the user'), _class='w2p_trap button16')]

        table = SQLFORM.grid(query,
                        searchable=False,
                        fields=fields,
                        links=links,
                        create=True,
                        editable=True,
                        paginate=self.rec_x_pag,
                        ui=admin_ui()
                        )

        return table

    def activate(self, iduser):
        """activate"""

        db = self.boilerplate.db
        T = current.T

        message = T("User doesn't exist.")
        users = db(db.auth_user.id == iduser).select()
        if users:
            user = users[0]
            user.update_record(registration_key='')
            message = T("User has been activated.")

        return message

    def disable(self, iduser):
        """Disabled"""

        db = self.boilerplate.db
        T = current.T

        message = T("User doesn't exist.")
        users = db(db.auth_user.id == iduser).select()
        if users:
            user = users[0]
            user.update_record(registration_key='disabled')
            message = T("User has been disabled.")

        return message

    def represent_membership(self, iduser):
        """Status group"""

        auth = self.boilerplate.auth
        T = current.T
        db = self.boilerplate.db

        def group_status(value, group):

            if auth.has_membership(group.id, iduser, group.role):
                return XML('%s (<span style="color: green;">%s</span>)' % \
                                (value, T('YES')))
            else:
                return XML('%s (<span style="color: red;">%s</span>)' % \
                                (value, T('NO')))

        db.auth_group.role.represent = lambda value, row: \
                                        group_status(value, row)

    def username(self, id):
        """ User name"""

        db = self.boilerplate.db
        user = db(db.auth_user.id == id).select(db.auth_user.username).first()

        return user.username

    def membership(self, iduser):
        """ membership """

        db = self.boilerplate.db
        T = current.T

        query = (db.auth_group.id > 0)
        self.represent_membership(iduser)

        links = [lambda row: \
            A(SPAN(_class='icon activate'), SPAN(T('Assign')),
             _href="javascript: void(0);",
            _onclick="if(!confirm('%s')){ return } ajax('%s', [], ':eval');" % \
            (T('Warning!. Assign user to this group?'),
                URL(self.controller_name,
                    "membership_assign",
                    vars={'user': iduser, 'group':row.id})),
            _title=T('Assign user to this group'), _class='w2p_trap button16'),
                 lambda row: \
             A(SPAN(_class='icon remove'), SPAN(T('Remove')),
            _href="javascript: void(0);",
            _onclick="if(!confirm('%s')){ return } ajax('%s', [], ':eval');" % \
            (T('Warning!. Remove user from this group?.'),
                URL(self.controller_name,
                "membership_remove",
                vars={'user': iduser, 'group': row.id})),
            _title=T('Remove user from this group'), _class='w2p_trap button16')]

        table = SQLFORM.grid(query,
                        links=links,
                        create=False,
                        deletable=False,
                        editable=False,
                        details=False,
                        searchable=False,
                        sortable=False,
                        csv=False,
                        paginate=1000,
                        ui=admin_ui()
                        )

        return table

    def membership_assign(self, iduser, idgroup):
        """Assign group"""

        auth = self.boilerplate.auth
        db = self.boilerplate.db
        T = current.T

        message = T("User doesn't exist.")
        users = db(db.auth_user.id == iduser).select()
        if users:
            user = users[0]
            auth.add_membership(idgroup, user.id)
            message = T("User added to group. Reload the page.")

        return message

    def membership_remove(self, iduser, idgroup):
        """group_remove"""

        auth = self.boilerplate.auth
        db = self.boilerplate.db
        T = current.T

        message = T("User doesn't exist.")
        users = db(db.auth_user.id == iduser).select()
        if users:
            user = users[0]
            auth.del_membership(idgroup, iduser)
            message = T("User has been remove it from the group. Reload the page.")

        return message

    def groups(self):
        """ List all groups """

        db = self.boilerplate.db
        T = current.T

        query = (db.auth_group.id > 0)

        table = SQLFORM.grid(query,
                        searchable=False,
                        paginate=self.rec_x_pag,
                        ui=admin_ui()
                        )

        return table
