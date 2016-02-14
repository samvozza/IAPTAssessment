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
    redirect(URL('auth', 'sign_in'))
    return dict()


def register():
    """
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """

    username_field    = DIV(DIV(LABEL('Username'),
                                _class='col-sm-12 col-md-12 col-lg-12'),
                            DIV(INPUT(_id='username-field', _class='form-control', _name='username',
                                      requires=[IS_NOT_EMPTY(error_message='Please pick a username'),
                                                IS_NOT_IN_DB(db, 'auth_user.username',
                                                             error_message=('This username has already been taken. '
                                                                            + 'Please try a different username.'))]),
                                _class='col-sm-6 col-md-6 col-lg-6'),
                            DIV(P('This is the name which other users will use to identify your collections, '
                                  + 'and will be used to identify you in trades.'),
                                _class='col-sm-6 col-md-6 col-lg-6'),
                            _class='form-group row')

    email_field       = DIV(DIV(LABEL('Email Address'),
                                _class='col-sm-12 col-md-12 col-lg-12'),
                            DIV(INPUT(_id='email-field', _class='form-control', _name='email',
                                      requires=[IS_NOT_EMPTY(error_message='Please enter your email address'),
                                                IS_EMAIL(error_message=('This does not appear to be a valid email address. '
                                                                        + 'Email addresses should be in the form:'
                                                                        + 'your-name@email-provider.com')),
                                                IS_NOT_IN_DB(db, 'auth_user.email',
                                                             error_message=('An account with this email address already '
                                                                            + 'exists.'))]),
                                _class='col-sm-6 col-md-6 col-lg-6'),
                            DIV(P('Your email address. We will use this if we need to contact you.'),
                                _class='col-sm-6 col-md-6 col-lg-6'),
                            _class='form-group row')

    password_field    = DIV(DIV(LABEL('Password'),
                                _class='col-sm-12 col-md-12 col-lg-12'),
                            DIV(INPUT(_id='password-field', _class='form-control', _name='password',
                                      _type='password',
                                      requires=[IS_NOT_EMPTY(error_message='Please pick a password'),
                                                IS_STRONG(min=8, special=0, upper=0,
                                                          error_message=('Please enter a stronger password. '
                                                                         + '')),
                                                CRYPT(),
                                                IS_EQUAL_TO(request.vars.password_confirm, error_message=' ')]),
                                _class='col-sm-6 col-md-6 col-lg-6'),
                            DIV(P('This is the password you will use to access the site. '
                                  + 'Passwords must contain at least 8 characters, and should have a mix of lower-case '
                                  + 'and upper-case letters, numbers and symbols.'),
                                _class='col-sm-6 col-md-6 col-lg-6'),
                            _class='form-group row')

    confirm_field     = DIV(DIV(LABEL('Confirm Password'),
                                _class='col-sm-12 col-md-12 col-lg-12'),
                            DIV(INPUT(_id='password-confirm-field', _class='form-control', _name='password_confirm',
                                      _type='password',
                                      requires=[IS_NOT_EMPTY(error_message='Please confirm your password'),
                                                IS_EQUAL_TO(request.vars.password,
                                                            error_message='The two passwords did not match')]),
                                _class='col-sm-6 col-md-6 col-lg-6'),
                            DIV(P('Please re-enter your password to confirm.'),
                                _class='col-sm-6 col-md-6 col-lg-6'),
                            _class='form-group row')

    register_button   = DIV(DIV(INPUT(_id='register-button', _name='register', _type='submit',
                                   _value='Register', _class='btn btn-primary pull-right'),
                                _class='col-sm-6 col-md-6 col-lg-6'),
                            DIV(_class='col-sm-6 col-md-6 col-lg-6'))

    registration_form = FORM(username_field, email_field, password_field, confirm_field, register_button,
                             _id='registration-form', _role='form')

    if registration_form.accepts(request, session):
        db.auth_user.insert(username=registration_form.vars.username,
                            password=registration_form.vars.password,
                            email=registration_form.vars.email)
        
        redirect(URL('default', 'index'))
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
        if not authenticate(sign_in_form.vars.username_email,
                            sign_in_form.vars.password):
            sign_in_form.errors.username_email = ' '
            sign_in_form.errors.password = ('Sign in failed. Please ensure that your username and password '
                                            + 'have been entered correctly.')
        else:
            redirect(URL('default', 'index'))
    elif sign_in_form.errors:
        pass
    else:
        pass

    return dict(form=sign_in_form)


def authenticate(username_or_email, password):
    # Treat username_or_email as a username
    user = auth.login_bare(username_or_email, password)
    if not user:
        # username_or_email may be an email, so check if it is in auth_user
        users_with_email = db(db.auth_user.email == username_or_email).select()

        if len(users_with_email) > 0:
            user = auth.login_bare(users_with_email[0].username, password)

    if user:
        auth.user = user

    return user
