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
    response.flash = T("Hello World")
    return dict(message=T('Welcome to web2py!'))


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
    db.executesql("INSERT INTO type(name) VALUES ('Advertising and brand'), ('Architectural'), ('Books'), ('Magazines and paper'), ('Clothing, fabric and textiles'), ('Coins, currency, stamps'), ('Film and television'), ('Glass and pottery'), ('Household items'), ('Memorabilia'), ('Music'), ('Nature and animals'),('Sports'),('Technology'), ('Themed'), ('Toys and games')")
    db.executesql("INSERT INTO collection(name, owner, public) VALUES ('Collection 1', 1, 'T'), ('Collection 2', 1, 'T'), ('Collection 3', 1, 'F'), ('Collection 4', 1, 'F')")
    db.object.insert(name="Object1",collection=1,price=33, type=2,quantity=5, tradable_quantity=4,description='asdfa sdfhadhfja dfha dfjah sjd fahd fja dfja sdjf');
    db.object.insert(name="Object1",collection=1,price=33, type=2,quantity=5, tradable_quantity=4,description='asdfa sdfhadhfja dfha dfjah sjd fahd fja dfja sdjf');
    db.object.insert(name="Object1",collection=1,price=33, type=2,quantity=5, tradable_quantity=4,description='asdfa sdfhadhfja dfha dfjah sjd fahd fja dfja sdjf');
    db.object.insert(name="Object1",collection=1,price=33, type=2,quantity=5, tradable_quantity=4,description='asdfa sdfhadhfja dfha dfjah sjd fahd fja dfja sdjf');
    db.object.insert(name="Object1",collection=1,price=33, type=2,quantity=5, tradable_quantity=4,description='asdfa sdfhadhfja dfha dfjah sjd fahd fja dfja sdjf');
    db.object.insert(name="Object1",collection=1,price=33, type=2,quantity=5, tradable_quantity=4,description='asdfa sdfhadhfja dfha dfjah sjd fahd fja dfja sdjf');
    db.object.insert(name="Object1",collection=1,price=33, type=2,quantity=5, tradable_quantity=4,description='asdfa sdfhadhfja dfha dfjah sjd fahd fja dfja sdjf');
    db.object.insert(name="Object1",collection=1,price=33, type=2,quantity=5, tradable_quantity=4,description='asdfa sdfhadhfja dfha dfjah sjd fahd fja dfja sdjf');
    db.object.insert(name="Object1",collection=1,price=33, type=2,quantity=5, tradable_quantity=4,description='asdfa sdfhadhfja dfha dfjah sjd fahd fja dfja sdjf');

    return dict()
