def view():
    response.collection = db(db.collection.id == request.args[0]).select().first()
    response.q = request.vars.q if request.vars.q != None else ''
    response.collections = db(db.collection.owner == response.collection.owner).select(orderby=db.collection.name)
    response.objects = db((db.object.collection == response.collection.id) & (db.object.name.like('%' +response.q+'%'))).select(orderby=db.object.name)
    response.tradable = db((db.object.collection == response.collection.id) &  (db.object.name.like('%' +response.q+'%')) & (db.object.tradable_quantity > 0)).select(orderby=db.object.name)
    response.wanted = db((db.object.collection == response.collection.id) & (db.object.name.like('%' +response.q+'%')) & (db.object.wanted_quantity > 0)).select(orderby=db.object.name)
    response.owned = db((db.object.collection == response.collection.id) & (db.object.name.like('%' +response.q+'%')) & (db.object.quantity > 0)).select(orderby=db.object.name)
    response.owner = db(db.auth_user.id == response.collection.owner).select().first()
    response.datalist = db(db.object.collection == response.collection.id).select(db.object.name,distinct=True)

    return dict(message=T('Welcome to web2py!'))

@auth.requires_login()

def create():
    if(not auth.is_logged_in()):
        redirect(URL('default', 'index'))
        return
    form=FORM(
              DIV(DIV(LABEL('Name'),_class='col-sm-12 col-md-12 col-lg-12'),
                  DIV(INPUT(_id='name', _class='form-control', _name='name',
                            requires=[IS_NOT_EMPTY(error_message='Please pick a name'),
                            IS_NOT_IN_DB(db(db.collection.owner==auth.user_id), 'collection.name',
                            error_message=('This collection already exists. '
                            + 'Please try a different name.'))]),
                            _class='col-sm-6 col-md-6 col-lg-6'),
                            DIV(P('Enter a name for your collection',
                                _class='form-field-description'),
                                _class='col-sm-8 col-md-8 col-lg-8'),
                                _class='form-group row'),

              DIV(DIV(LABEL('Public'),_class='col-sm-12 col-md-12 col-lg-12'),
                  DIV(SELECT(OPTION('No', _value = False),OPTION('Yes', _value = True), _id='public-field', _class='form-control', _name='public'),
                      _class='col-sm-6 col-md-6 col-lg-6'),
                      DIV(P('This determines if other users can see the objects in your collection ',
                          _class='form-field-description'),
                          _class='col-sm-8 col-md-8 col-lg-8'),
                          _class='form-group row'),

              DIV(DIV(INPUT(_type='button', _value='Back', _onclick='window.location=\'%s\';;return false'
              % URL('collection','my'), _class='btn btn-primary pull-right'),
                            _class='col-sm-5 col-md-5 col-lg-5')),

                    DIV(INPUT(_id='submit-button', _name='Submit', _type='submit',
                     _value='Create', _class='btn btn-primary pull-right'),
                     _class='col-sm-1 col-md-1 col-lg-1'),
              )

    form.vars.owner = auth.user_id

    if form.accepts(request,session):
            response.flash = 'Collection created.'
            if(form.vars.public == 'No'):
                db.collection.insert(name=form.vars.name, public= False)
            else:
                db.collection.insert(name=form.vars.name, public= True)
            redirect(URL('my'))


    elif form.errors:
        response.flash = "We couldn't process your form because it contain errors. Check below for more detail."

    else:
        response.flash = 'Use the form below to create a new collection.'

    return  dict(form=form)

@auth.requires_login()
def edit():
    if(not auth.is_logged_in()):
        redirect(URL('default', 'index'))
        return

    collection = db(db.collection.id == request.args[0]).select().first()
    form=FORM(
              DIV(DIV(LABEL('Name'),_class='col-sm-12 col-md-12 col-lg-12'),
                  DIV(INPUT(_id='name-field', _class='form-control', _name='name', _value= collection.name,
                            requires=[IS_NOT_EMPTY(error_message='Please pick a name'),
                            IS_NOT_IN_DB(db((db.collection.owner==auth.user_id) & (db.collection.name != collection.name)), 'collection.name',
                            error_message=('This collection already exists. '
                            + 'Please try a different name.'))]),
                            _class='col-sm-6 col-md-6 col-lg-6'),
                            DIV(P('Enter a name for your collection',
                                _class='form-field-description'),
                                _class='col-sm-8 col-md-8 col-lg-8'),
                                _class='form-group row'),

              DIV(DIV(LABEL('Public'),_class='col-sm-12 col-md-12 col-lg-12'),
                  DIV(SELECT(OPTION('Yes', _value = True, _selected=True),OPTION('No', _value = False, _selected=False), _id='public-field',
                   _class='form-control', _name='public', value = collection.public),
                      _class='col-sm-6 col-md-6 col-lg-6'),
                      DIV(P('This determines if other users can see the objects in your collection ',
                          _class='form-field-description'),
                          _class='col-sm-8 col-md-8 col-lg-8'),
                          _class='form-group row'),

              DIV(DIV(INPUT(_type='button', _value='Back', _onclick='window.location=\'%s\';;return false' %
              URL('collection','my'), _class='btn btn-primary pull-right'),
                            _class='col-sm-5 col-md-5 col-lg-5')),

                    DIV(INPUT(_id='submit-button', _name='Submit', _type='submit',
                     _value='Update', _class='btn btn-primary pull-right'),
                     _class='col-sm-1 col-md-1 col-lg-1'),
              )

    form.vars.owner = auth.user_id

    if form.accepts(request,session):
            response.flash = 'Your collection updated.'
            if(form.vars.public == 'No'):
                db(db.collection.id == collection.id).update(name=form.vars.name , public= False)
            else:
                db(db.collection.id == collection.id).update(name=form.vars.name , public= True)
            redirect(URL('my'))

    elif form.errors:
        response.flash = "We couldn't process your form because it contain errors. Check below for more detail."

    else:
        response.flash = 'Use the form below to update a collection.'

    return  dict(form=form)

def delete():

    collection = db(db.collection.id == request.args[0]).select().first()
    default_collection = db((db.collection.name == 'Default') & (db.collection.owner == auth.user)).select().first()

    if(not auth.is_logged_in()):
        redirect(URL('default', 'index'))
        return

    if(collection.id == default_collection.id):
        redirect(URL('collection', 'my'))
        return

    form = FORM(DIV(P('Are you sure you want to delete ' + collection.name + '?')),
                LABEL(),
                DIV(DIV(INPUT(_type='button', _value='No', _onclick='window.location=\'%s\';;return false' %
                URL('collection','my'), _class='btn btn-primary pull-left'),
                                _class='col-sm-0 col-md-0 col-lg-0')),
                DIV(DIV(INPUT(_type='submit', _value='Yes', _class='btn btn-danger pull-left'),
                            _class='col-sm-1 col-md-1 col-lg-1')),
               )

    if form.accepts(request,session):
            response.flash = collection.name + ' has been deleted.'

            for row in db(db.object.collection == collection.id).select():
                row.update_record(collection = default_collection)
            db(db.collection.id == collection.id).delete()
            redirect(URL('my'))

    return dict(form=form)

@auth.requires_login()
def my():
    response.col = db(db.collection.owner == auth.user_id).select().first()
    redirect(URL('collection', 'view', args=[response.col.id]))

def user():
    response.col = db((db.collection.owner == request.args[0]) & (db.collection.public == 'T')).select().first()
    redirect(URL('collection', 'view', args=[response.col.id]))

def getit():
    item = db(db.object.id == request.args(0)).select().first()
    redirect(URL('trade', 'new_proposal', vars={'with': item.owner, 'collection': item.collection, 'add': item.id}));

def wantit():
    o = db(db.object.id == request.args[0]).select().first()
    new_item = db.object.insert(**db.object._filter_fields(o))
    db(db.object.id == new_item).update(owner = auth.user_id)
    default = db((db.collection.owner == auth.user_id) & (db.collection.name=='Default')).select().first()
    db(db.object.id == new_item).update(collection = default.id)
    db(db.object.id == new_item).update(wanted_quantity = 1)
    if request.vars.url:
        redirect(request.vars.url+('?' if '?' not in request.vars.url else '&')+"message=wantit")
    else:
        redirect(URL('default', 'index'))
