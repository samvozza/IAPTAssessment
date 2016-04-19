# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

import operator


def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    
    recent_trades = []
    top_collections = []
    
    if auth.user:
        trades_query = db((db.trade.sender == auth.user.id) 
                           | ((db.trade.receiver == auth.user.id) & (db.trade.status != STATUS_PREPARE))
                           & (db.trade.status != STATUS_CANCELLED))
        recent_trades = trades_query.select(orderby=~db.trade.time_modified, limitby=(0, 5))
        
        collections = []
        for collection in db(db.collection.owner == auth.user.id).select():
            item_count = db(db.object.collection == collection.id).count()
            collections.append((collection, item_count))
            
        collections.sort(key=operator.itemgetter(1), reverse=True)
        top_collections = collections[:5]
    
    return dict(recent_trades=recent_trades,
                top_collections=top_collections)

def search():
    response.q = request.vars.q if request.vars.q else ''
    response.min = request.vars.min if request.vars.min else ''
    response.max = request.vars.max if request.vars.max else ''
    response.u = request.vars.u if request.vars.u else ''
    response.c = request.vars.c if request.vars.c else ''

    response.users = db().select(db.auth_user.ALL, orderby=db.auth_user.username)
    response.categories = db().select(db.category.ALL, orderby=db.category.id)
    response.results = []
    if response.q == '' and response.min == '' and response.max == '' and response.u == '' and response.c == '':
        response.r = None
    else:
        query = ((db.object.collection == db.collection.id)  & (db.collection.public == 'T'))
        if response.q.endswith('s'):
            query &= db.object.name.like('%' + response.q[:-1] + '%')
        else:
            query &= db.object.name.like('%' + response.q + '%')
        if response.min != '':
            query &= db.object.price >= response.min
        if response.max != '':
            query &= db.object.price <= response.max
        if response.u != '':
            userx = db(db.auth_user.username == response.u).select().first()
            query &= db.object.owner == userx.id
        if response.c != '':
            category = db(db.category.id == response.c).select().first()
            query &= db.object.category == category.id
        response.results = db(query).select(join=db.auth_user.on(db.object.owner == db.auth_user.id))
        response.r = ''

    if response.r == None or response.r == '':
        add_breadcrumb('Search')
    else:
        add_breadcrumb('Search', URL('default', 'search'))
        add_breadcrumb(response.r)
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

    db.category.insert(name='Advertising and Brand')
    db.category.insert(name='Architectural')
    db.category.insert(name='Books')
    db.category.insert(name='Magazines and Paper')
    db.category.insert(name='Clothing, Fabric and Textiles')
    db.category.insert(name='Coins, Currency and Stamps')
    db.category.insert(name='Film and Television')
    db.category.insert(name='Glass and Pottery')
    db.category.insert(name='Household Items')
    db.category.insert(name='Music')
    db.category.insert(name='Nature and Animals')
    db.category.insert(name='Sports')
    db.category.insert(name='Technology')
    db.category.insert(name='Themed')
    db.category.insert(name='Toys and Games')

    return dict()




# Error handling

def error_handler():
    """
    This is a catch-all route which acts as the destination for all server errors.

    Use:
    raise EX(status_code, message)
    To ensure that exceptions are handled appropriately.
    """
    error_title = 'Oops ...'
    error_details = ('Somewhere in the universe, a butterfly has spread it\'s wings '
                     + 'and leapt into the world. As a result, our servers seem to be '
                     + 'misbehaving. Hopefully, refreshing the page will magically kick '
                     + 'our servers back into action. If that doesn\'t resolve the issue, '
                     + 'you can use the link below to get back to safety.')
    recovery_link = URL('default', 'index')

    code = request.vars.code or 500
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

    error_title = str(code) + ' - ' + error_title
    
    error_message = session.error_message
    session.error_message = None

    add_breadcrumb(error_title)
    return dict(error_title=error_title,
                error_details=error_details,
                recovery_link=recovery_link,
                error_message=error_message)
