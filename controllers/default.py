# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    return dict(message=T('Welcome to web2py!'))

def search():
    response.q = request.vars.q if request.vars.q else ''
    response.min = request.vars.min if request.vars.min else ''
    response.max = request.vars.max if request.vars.max else ''
    response.u = request.vars.u if request.vars.u else ''

    response.users = db().select(db.auth_user.ALL, orderby=db.auth_user.username)
    response.results = []
    if response.q == '' and response.min == '' and response.max == '' and response.u == '':
        response.r = None
    else:
        query = ((db.object.collection == db.collection.id)  & (db.collection.public == 'T'))
        query &= db.object.name.like('%' + response.q + '%')
        if response.min != '':
            query &= db.object.price >= response.min
        if response.max != '':
            query &= db.object.price <= response.max
        if response.u != '':
            userx = db(db.auth_user.username == response.u).select().first()
            #response.results =  db(((db.object.price >= response.min) | ).select()

        response.results = db(query).select()
        response.r = ''

    return dict();

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()

def prepare():
    #THIS IS FOR TESTING PURPOSES
    #DELETES THE ENTIRE DATABASE
    #####MAKE SURE YOU HAVE SIGNED OUT BEFORE RUNNING!
    import shutil
    import os
    shutil.rmtree(os.path.abspath(os.path.dirname(__file__)+'/../databases'))
    os.makedirs(os.path.abspath(os.path.dirname(__file__)+'/../databases'))
    #redirect(URL('setup'))

def setup():
    #SET UP WHATEVER INITIAL DATA YOU NEED
    #db.executesql("INSERT INTO category(name) VALUES ('Advertising and brand'), ('Architectural'), ('Books'), ('Magazines and paper'), ('Clothing, fabric and textiles'), ('Coins, currency, stamps'), ('Film and television'),
    #('Glass and pottery'), ('Household items'), ('Memorabilia'), ('Music'), ('Nature and animals'),('Sports'),('Technology'), ('Themed'), ('Toys and games');")
    #db.executesql("INSERT INTO collection(name, owner, public) VALUES ('Collection 1', 1, 'T'), ('Collection 2', 1, 'T'), ('Collection 3', 1, 'F'), ('Collection 4', 1, 'F')")

    db.category.insert(name='Advertising and brand')
    db.category.insert(name='Architectural')
    db.category.insert(name='Books')
    db.category.insert(name='Magazines and paper')
    db.category.insert(name='Clothing, fabric and textiles')
    db.category.insert(name='Coins, currency, stamps')
    db.category.insert(name='Film and television')
    db.category.insert(name='Galass and pottery')
    db.category.insert(name='Household items')
    db.category.insert(name='Music')
    db.category.insert(name='Nature and animals')
    db.category.insert(name='Sports')
    db.category.insert(name='Technology')
    db.category.insert(name='Themed')
    db.category.insert(name='Toyes and Games')

    return dict()




# Error handling

def error_handler():
    """
    This is a catch-all route which acts as the destination for all server errors.
    Use:
    raise HTTP(403)
    raise HTTP(404)
    raise HTTP(500)

    To have such errors handled appropriately.

    Any other exception will cause a generic 'there was a problem' message to
    be displayed.

    A more detailed error can be displayed by setting 'session.error_message'.
    """
    error_title = 'Oops ...'
    error_details = ('Somewhere in the universe, a butterfly has spread it\'s wings '
                     + 'and leapt into the world. As a result, our servers seem to be '
                     + 'misbehaving. Hopefully, refreshing the page will magically kick '
                     + 'our servers back into action. If that doesn\'t resolve the issue, '
                     + 'you can use the link below to get back to safety.')
    recovery_link = URL('default', 'index')

    code = request.vars.code
    if code == '403':
        error_title = 'You Don\'t Have Permission'
        error_details = ('Uh oh - you shouldn\'t have ended up here. '
                         + 'But that\'s OK - we can help you get back to '
                         + 'wherever you needed to be.')
    elif code == '404':
        error_title = 'You Look A Little Lost'
        error_details = ('You seem to have wandered off the beaten path. '
                         + 'But that\'s OK - everyone ends up here at some point.')
    elif code == '500':
        pass

    if session.error_message:
        error_details = error_details + ' See the message below for more details.'

    return dict(error_title=error_title,
                error_details=error_details,
                recovery_link=recovery_link)
