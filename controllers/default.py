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
    #db.executesql("INSERT INTO category(name) VALUES ('Advertising and brand'), ('Architectural'), ('Books'), ('Magazines and paper'), ('Clothing, fabric and textiles'), ('Coins, currency, stamps'), ('Film and television'), ('Glass and pottery'), ('Household items'), ('Memorabilia'), ('Music'), ('Nature and animals'),('Sports'),('Technology'), ('Themed'), ('Toys and games');")
    #db.executesql("INSERT INTO collection(name, owner, public) VALUES ('Collection 1', 1, 'T'), ('Collection 2', 1, 'T'), ('Collection 3', 1, 'F'), ('Collection 4', 1, 'F')")

    db.category.insert(name='Advertising and brand')
    db.category.insert(name='Architectural')
    db.category.insert(name='Books')
    db.category.insert(name='Magazines and paper')

    db.collection.insert(name='Collection 1', owner=1, public='T')
    db.collection.insert(name='Collection 2', owner=1, public='T')
    db.collection.insert(name='Collection 3', owner=1, public='F')
    db.collection.insert(name='Collection 4', owner=1, public='F')

    db.object.insert(name="Object1",collection=1,price=1, category=1,quantity=9, tradable_quantity=4, wanted_quantity=0,description='1asdfa sdfhadhfja dfha dfjah sjd fahd fja dfja sdjf')
    db.object.insert(name="Object2",collection=1,price=2.2, category=2,quantity=8, tradable_quantity=4, wanted_quantity=0, description='2asdfa sdfhadhfja dfha dfjah sjd fahd fja dfja sdjf')
    db.object.insert(name="Object3",collection=1,price=3.33, category=3,quantity=7, tradable_quantity=4, wanted_quantity=0, description='3asdfa sdfhadhfja dfha dfjah sjd fahd fja dfja sdjf')
    db.object.insert(name="Object4",collection=1,price=44, category=4,quantity=6, tradable_quantity=4, wanted_quantity=0, description='4asdfa sdfhadhfja dfha dfjah sjd fahd fja dfja sdjf')
    db.object.insert(name="Object5",collection=1,price=55.5, category=1,quantity=5, tradable_quantity=4, wanted_quantity=0, description='5asdfa sdfhadhfja dfha dfjah sjd fahd fja dfja sdjf')
    db.object.insert(name="Object6",collection=1,price=66.66, category=2,quantity=4, tradable_quantity=4, wanted_quantity=0, description='6asdfa sdfhadhfja dfha dfjah sjd fahd fja dfja sdjf')
    db.object.insert(name="Object7",collection=1,price=777, category=3,quantity=3, tradable_quantity=0, wanted_quantity=0, description='7asdfa sdfhadhfja dfha dfjah sjd fahd fja dfja sdjf')
    db.object.insert(name="Object8",collection=1,price=888.8, category=4,quantity=2, tradable_quantity=0, wanted_quantity=1, description='8asdfa sdfhadhfja dfha dfjah sjd fahd fja dfja sdjf')
    db.object.insert(name="Object9",collection=1,price=999.99, category=1,quantity=1, tradable_quantity=0, wanted_quantity=2, description='9asdfa sdfhadhfja dfha dfjah sjd fahd fja dfja sdjf')
    db.object.insert(name="ObjectX",collection=1,price=111, category=1,quantity=0, tradable_quantity=0, wanted_quantity=1, description='9asdfa sdfhadhfja dfha dfjah sjd fahd fja dfja sdjf')
    db.object.insert(name="ObjectX",collection=1,price=222, category=1,quantity=0, tradable_quantity=0, wanted_quantity=2, description='9asdfa sdfhadhfja dfha dfjah sjd fahd fja dfja sdjf')

    return dict()
