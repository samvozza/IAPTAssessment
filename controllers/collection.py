def view():
    response.collection = db(db.collection.id == request.args[0]).select().first()
    response.q = request.vars.q if request.vars.q != None else ''
    if response.collection.owner == auth.user.id:
        response.collections = db(db.collection.owner == response.collection.owner).select(orderby=db.collection.name)
    else:
        response.collections = db((db.collection.owner == response.collection.owner) & (db.collection.public == 'T')).select(orderby=db.collection.name)
    response.objects = db((db.object.collection == response.collection.id) & (db.object.name.like('%' +response.q+'%'))).select(orderby=db.object.name)
    response.tradable = db((db.object.collection == response.collection.id) &  (db.object.name.like('%' +response.q+'%')) & (db.object.tradable_quantity > 0)).select(orderby=db.object.name)
    response.wanted = db((db.object.collection == response.collection.id) & (db.object.name.like('%' +response.q+'%')) & (db.object.wanted_quantity > 0)).select(orderby=db.object.name)
    response.owned = db((db.object.collection == response.collection.id) & (db.object.name.like('%' +response.q+'%')) & (db.object.quantity > 0)).select(orderby=db.object.name)
    response.owner = db(db.auth_user.id == response.collection.owner).select().first()
    response.datalist = db(db.object.collection == response.collection.id).select(db.object.name,distinct=True)

    return dict()

@auth.requires_login()
def create():
    form = SQLFORM(db.collection, fields=['name'])
    form.vars.owner = auth.user_id
    form.vars.public = True if request.vars.public == 'Yes' else False
    if form.process(keepvalues=True).accepted:
        redirect(URL('collection', 'view', args=[form.vars.id], vars=dict(message='new_collection')))
    return dict(form=form)


@auth.requires_login()
def edit():
    response.collection = db(db.collection.id == request.args[0]).select().first()
    default_collection = db((db.collection.name == 'Default') & (db.collection.owner == auth.user)).select().first()

    if(response.collection.id == default_collection.id):
        redirect(URL('collection', 'my'))
        return

    form = SQLFORM(db.collection, response.collection, fields=['name'])
    form.vars.owner = auth.user_id
    form.vars.public = True if request.vars.public == 'Yes' else False
    if form.process(keepvalues=True).accepted:
        redirect(URL('collection', 'view', args=[form.vars.id], vars=dict(message='edit_collection')))
    return dict(form=form)

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
