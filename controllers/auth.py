# -*- coding: utf-8 -*-

# Authentication routes

def index():
    """
    Immediate redirect to the default controller's index page
    """
    redirect(URL('default', 'index'))


def user():
    """
    Immediate redirect to the auth controller's sign in page
    """
    redirect(URL('auth', 'sign_in', vars=request.vars))


def register():
    """
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """

    registration_form = FORM(FIELD_WITH_DESC('Username',
                                             INPUT(_id='username-field', _class='form-control', _name='username',
                                                   requires=[IS_NOT_EMPTY(error_message='Please pick a username'),
                                                             IS_NOT_IN_DB(db, 'auth_user.username',
                                                                          error_message=('This username has already been taken. '
                                                                                         + 'Please try a different username.'))]),
                                             ('This is the name which other users will use to identify your collections, '
                                              + 'and will be used to identify you in trades.')),
                             FIELD_WITH_DESC('Email Address',
                                             INPUT(_id='email-field', _class='form-control', _name='email',
                                                   requires=[IS_NOT_EMPTY(error_message='Please enter your email address'),
                                                             IS_EMAIL(error_message=('This does not appear to be a valid email address. '
                                                                                     + 'Email addresses should be in the form:'
                                                                                     + 'your-name@email-provider.com')),
                                                             IS_NOT_IN_DB(db, 'auth_user.email',
                                                                          error_message=('An account with this email address already '
                                                                                         + 'exists.'))]),
                                             'Your email address. We will use this if we need to contact you.'),
                             FIELD_WITH_DESC('Password',
                                             INPUT(_id='password-field', _class='form-control', _name='password',
                                                   _type='password',
                                                   requires=[IS_NOT_EMPTY(error_message='Please pick a password'),
                                                             CRYPT(min_length=8,
                                                                   error_message='Please enter a stronger password.')]),
                                             ('This is the password you will use to access the site. '
                                              + 'Passwords must contain at least 8 characters, and should have a mix of lower-case '
                                              + 'and upper-case letters, numbers and symbols.')),
                             FIELD_WITH_DESC('Confirm Password',
                                             INPUT(_id='password-confirm-field', _class='form-control', _name='password_confirm',
                                                   _type='password',
                                                   requires=[IS_NOT_EMPTY(error_message='Please confirm your password'),
                                                             IS_EQUAL_TO(request.vars.password,
                                                                         error_message='The two passwords did not match')]),
                                             'Please re-enter your password to confirm.'),
                             DIV(DIV(INPUT(_id='register-button', _name='register', _type='submit',
                                           _value='Register', _class='btn btn-primary pull-right'),
                                     _class='col-sm-6 col-md-6 col-lg-6'),
                                 DIV(_class='col-sm-6 col-md-6 col-lg-6')),

                             _id='registration-form', _role='form')

    if registration_form.accepts(request, session):
        user_id = db.auth_user.insert(username=registration_form.vars.username,
                                      password=registration_form.vars.password,
                                      email=registration_form.vars.email)
        db.collection.insert(name='Default', owner=user_id, public='F')
        db.user_settings.insert(user=user_id)

        if authenticate(registration_form.vars.username, registration_form.vars.password):
            session.flash = (T('Hi ' + registration_form.vars.username + '! '
                               + 'Welcome to CollectShare.'), 'success')
            redirect(URL('collection', 'my'))
    elif registration_form.errors:
        if registration_form.errors.password_confirm:
            registration_form.errors.password = ' '
    else:
        pass
    
    add_breadcrumb('Register')
    return dict(form=registration_form)


@auth.requires_login()
def edit():
    trade_non_tradable_items = db(db.user_settings.user == auth.user.id).select().first().trade_non_tradable_items

    edit_form = FORM(FIELD_WITH_DESC('Username',
                                     INPUT(_id='username-field', _class='form-control', _name='username', _value=auth.user.username,
                                           requires=[IS_EMPTY_OR(IS_STRING_OR(IS_NOT_IN_DB(db, 'auth_user.username',
                                                                                           error_message=('This username has already been taken. '
                                                                                                          + 'Please try a different username.')),
                                                                              auth.user.username))]),
                                     'Your new username.'),
                     FIELD_WITH_DESC('Trade Any Item',
                                     DIV(P('This setting controls whether other users are able to request items '
                                           + 'which you have not specified that you are happy to receive offers for.',
                                           _class='form-field-description'),
                                         SELECT(OPTION('Yes', _value='Yes'), OPTION('No', _value='No'),
                                                _id='trade-any-item-select', _class='form-control',
                                                _name='trade_any_item', value=('Yes' if trade_non_tradable_items else 'No'),
                                                requires=[IS_IN_SET(['Yes', 'No'],
                                                                    error_message='Please select either \'Yes\' or \'No\'')])),
                                     [('Select \'Yes\' if you are happy to receive requests to trade any item '
                                       + 'in any of your collections.'), BR(),
                                      ('Select \'No\' if you only wish to be contacted about items which you '
                                       + 'have selected to trade.')]),
                     FIELD_WITH_DESC('Old Password',
                                     INPUT(_id='old-password-field', _class='form-control', _name='old_password',
                                           _type='password'),
                                     'Your current password.'),
                     FIELD_WITH_DESC('New Password',
                                     INPUT(_id='password-field', _class='form-control', _name='password',
                                           _type='password',
                                           requires=[IS_EMPTY_OR(CRYPT(min_length=8,
                                                                       error_message='Please enter a stronger password.'))]),
                                     'Your new password.'),
                     FIELD_WITH_DESC('Confirm Password',
                                     INPUT(_id='password-confirm-field', _class='form-control', _name='password_confirm',
                                           _type='password',
                                           requires=[IS_EQUAL_TO(request.vars.password,
                                                                 error_message='The two passwords did not match')]),
                                     'Please re-enter your password to confirm.'),
                     DIV(DIV(INPUT(_id='update-button', _name='update', _type='submit',
                                   _value='Update', _class='btn btn-primary pull-right'),
                             _class='col-sm-6 col-md-6 col-lg-6'),
                         DIV(_class='col-sm-6 col-md-6 col-lg-6')),
                     _id='user-edit-form', _role='form')

    if edit_form.accepts(request, session):
        # Track whether any errors have occurred
        errors = False

        # Update the user's username (if it has changed)
        if (edit_form.vars.username and edit_form.vars.username != ""):
            db(db.auth_user.id == auth.user.id).update(username=edit_form.vars.username)

        # Update the user's password (if it has changed)
        if edit_form.vars.password and edit_form.vars.password != "":
            user = auth.login_bare(auth.user.username, edit_form.vars.old_password)
            if user:
                db(db.auth_user.id == auth.user.id).update(password=edit_form.vars.password)
            else:
                errors = True
                edit_form.errors.old_password = ('Password check failed. Please check that you have '
                                                 + 'entered your current password correctly.')

        if edit_form.vars.trade_any_item:
            if edit_form.vars.trade_any_item == 'Yes':
                db(db.user_settings.user == auth.user.id).update(trade_non_tradable_items=True)
            elif edit_form.vars.trade_any_item == 'No':
                db(db.user_settings.user == auth.user.id).update(trade_non_tradable_items=False)

        if not errors:
            if edit_form.vars.username != "" or edit_form.vars.password != "":
                user = db(db.auth_user.id == auth.user.id).select().first()
                auth.login_user(user)
                session.flash = (T('Your account details have been updated.'), 'success')
            else:
                session.flash = (T('Your account details have not been changed.'), 'info')
            redirect_to_next(default=URL('collection', 'my'))
    elif edit_form.errors:
        if edit_form.errors.password_confirm:
            edit_form.errors.password = ' '
    else:
        pass

    add_breadcrumb('Edit Your Details')
    return dict(form=edit_form)


def sign_in():
    """
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """

    sign_in_form = FORM(DIV(LABEL('Username or Email Address'),
                            INPUT(_id='username-email-field', _class='form-control', _name='username_email',
                                  requires=[IS_NOT_EMPTY(error_message=('Please enter your username or '
                                                                             + 'email address'))]),
                            _class='form-group'),
                        DIV(LABEL('Password'),
                            INPUT(_id='password-field', _class='form-control', _name='password',
                                  _type='password',
                                  requires=[IS_NOT_EMPTY(error_message='Please enter your password')]),
                            _class='form-group'),
                        INPUT(_id='sign-in-button', _name='sign_in', _type='submit',
                              _value='Sign In', _class='btn btn-primary pull-right'),
                        _id='sign-in-form', _role='form')

    if sign_in_form.accepts(request, session):
        if authenticate(sign_in_form.vars.username_email, sign_in_form.vars.password):
            redirect_to_next(default=URL('collection', 'my'))
        else:
            sign_in_form.errors.username_email = ' '
            sign_in_form.errors.password = ('Sign in failed. Please ensure that your username and password '
                                            + 'have been entered correctly.')
    elif sign_in_form.errors:
        pass
    else:
        pass

    add_breadcrumb('Sign In')
    return dict(form=sign_in_form)


def sign_out():
    auth.logout(next=URL('default', 'index'))
    return dict()



# Helper functions

def authenticate(username_or_email, password):
    # Treat username_or_email as a username
    user = auth.login_bare(username_or_email, password)
    if not user:
        # username_or_email may be an email, so check if it is in auth_user
        users_with_email = db(db.auth_user.email == username_or_email).select()

        if len(users_with_email) > 0:
            user = auth.login_bare(users_with_email[0].username, password)

    if user:
        auth.login_user(user)

    return user


def redirect_to_next(default=URL('default', 'index')):
    if request.vars['_next']:
        redirect(request.vars['_next'])
    else:
        redirect(default)


def FIELD_WITH_DESC(name, field, description):
    return DIV(DIV(LABEL(name),
                   _class='col-sm-12 col-md-12 col-lg-12'),
               DIV(field,
                   _class='col-sm-6 col-md-6 col-lg-6'),
               DIV(P(description,
                     _class='form-field-description'),
                   _class='col-sm-6 col-md-6 col-lg-6'),
               _class='form-group row')

class IS_STRING_OR(object):
    def __init__(self, other, comparison_string=""):
        self.other = other
        self.comparison_string = comparison_string
        if hasattr(other, 'multiple'):
            self.multiple = other.multiple
        if hasattr(other, 'options'):
            self.options = self._options

    def __call__(self, value):
        if value == self.comparison_string:
            return (value, None)
        if isinstance(self.other, (list, tuple)):
            error = None
            for item in self.other:
                value, error = item(value)
                if error:
                    break
            return value, error
        else:
            return self.other(value)

    def formatter(self, value):
        if hasattr(self.other, 'formatter'):
            return self.other.formatter(value)
        return value
