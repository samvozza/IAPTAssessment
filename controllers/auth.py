# -*- coding: utf-8 -*-

# Authentication routes

def index():
    """
    Immediate redirect to the default controller's index page
    """
    redirect(URL('default', 'index'))
    return dict()


def user():
    """
    Immediate redirect to the auth controller's sign in page
    """
    redirect(URL('auth', 'sign_in', vars=request.vars))
    return dict()


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
        db.auth_user.insert(username=registration_form.vars.username,
                            password=registration_form.vars.password,
                            email=registration_form.vars.email)

        if authenticate(registration_form.vars.username, registration_form.vars.password):
            session.flash = (T('Hi ' + registration_form.vars.username + '! '
                               + 'Welcome to CollectShare.'), 'success')
            redirect_to_next()
    elif registration_form.errors:
        pass
    else:
        pass
    
    return dict(form=registration_form)


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
            redirect_to_next()
        else:
            sign_in_form.errors.username_email = ' '
            sign_in_form.errors.password = ('Sign in failed. Please ensure that your username and password '
                                            + 'have been entered correctly.')
    elif sign_in_form.errors:
        pass
    else:
        pass

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
