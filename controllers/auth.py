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
    
    registration_form = FORM(DIV(LABEL('Username'),
                                 INPUT(_id='username-field', _class='form-control', _name='username',
                                       requires=[IS_NOT_EMPTY(error_message='Please pick a username'),
                                                 IS_NOT_IN_DB(db, 'auth_user.username',
                                                              error_message=('This username has already been taken. '
                                                                             + 'Please try a different username.'))]),
                                 _class='form-group'),
                             DIV(LABEL('Email Address'),
                                 INPUT(_id='email-field', _class='form-control', _name='email',
                                       requires=[IS_NOT_EMPTY(error_message='Please enter your email address'),
                                                 IS_EMAIL(error_message=('This does not appear to be a valid email address. '
                                                                         + 'Email addresses should be in the form:'
                                                                         + 'your-name@email-provider.com')),
                                                 IS_NOT_IN_DB(db, 'auth_user.email',
                                                              error_message=('An account with this email address already '
                                                                             + 'exists.'))]),
                                 _class='form-group'),
                             DIV(LABEL('Password'),
                                 INPUT(_id='password-field', _class='form-control', _name='password',
                                       _type='password',
                                       requires=[IS_NOT_EMPTY(error_message='Please pick a password'),
                                                 IS_EQUAL_TO(request.vars.password_confirm, error_message=' '),
                                                 IS_STRONG(min=8, special=0, upper=0,
                                                           error_message=('Please enter a stronger password. '
                                                                          + 'Passwords should contain at least 8 characters, '
                                                                          + 'and should be a mix of lower-case and '
                                                                          + 'upper-case letters, numbers and symbols')),
                                                 CRYPT()]),
                                 _class='form-group'),
                             DIV(LABEL('Confirm Password'),
                                 INPUT(_id='password-confirm-field', _class='form-control', _name='password_confirm',
                                       _type='password',
                                       requires=[IS_NOT_EMPTY(error_message='Please confirm your password'),
                                                 IS_EQUAL_TO(request.vars.password,
                                                             error_message='The two passwords did not match')]),
                                 _class='form-group'),
                             INPUT(_id='register-button', _name='register', _type='submit',
                                   _value='Register', _class='btn btn-primary'),
                             _id='registration_form', _role='form')
    
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
