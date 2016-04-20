def view():
    response.collection = db(db.collection.id == request.args[0]).select().first()
    
    # Check that the collection exists
    if response.collection == None:
        raise EX(500, 'This collection does not exist.')
    
    # Check that the logged in user is the collection's owner, or that the collection is public
    if auth.user and auth.user.id != response.collection.owner and not response.collection.public:
        raise EX(403, 'You do not have access to this collection.')
    
    response.q = request.vars.q if request.vars.q != None else ''
    if auth.user and response.collection.owner == auth.user.id:
        collections = db(db.collection.owner == response.collection.owner).select(orderby=db.collection.name)
        default_collection = db((db.collection.name == 'Default') & (db.collection.owner == auth.user)).select().first()
        other_collections = [collection for collection in collections if collection.id != default_collection.id]
        response.collections = [default_collection]
        response.collections.extend(other_collections)
    else:
        response.collections = db((db.collection.owner == response.collection.owner) & (db.collection.public == 'T')).select(orderby=db.collection.name)
    response.objects = db((db.object.collection == response.collection.id) & (db.object.name.like('%' +response.q+'%'))).select(orderby=db.object.name)
    response.tradable = db((db.object.collection == response.collection.id) &  (db.object.name.like('%' +response.q+'%')) & (db.object.tradable_quantity > 0)).select(orderby=db.object.name)
    response.wanted = db((db.object.collection == response.collection.id) & (db.object.name.like('%' +response.q+'%')) & (db.object.wanted_quantity > 0)).select(orderby=db.object.name)
    response.owned = db((db.object.collection == response.collection.id) & (db.object.name.like('%' +response.q+'%')) & (db.object.quantity > 0)).select(orderby=db.object.name)
    response.owner = db(db.auth_user.id == response.collection.owner).select().first()
    response.datalist = db(db.object.collection == response.collection.id).select(db.object.name,distinct=True)

    name = 'My' if auth.user and response.owner.id == auth.user.id else response.owner.username + '\'s'
    add_breadcrumb(name + ' Collections', URL('collection', 'user', args=[response.owner.id]))
    add_breadcrumb(response.collection.name)
    return dict()

@auth.requires_login()
def create():
    form = SQLFORM(db.collection, fields=['name'])
    form.vars.owner = auth.user_id
    form.vars.public = True if request.vars.public == 'Yes' else False
    form.custom.widget.name['requires'] = [IS_UNIQUE_PER_USER(form.vars.owner,
                                                              error_message="You already have a collection with this name."),
                                           IS_LENGTH(64, error_message="Please limit the collection name to 64 characters."),
                                           IS_NOT_EMPTY(error_message="Please enter a collection name.")]
    if form.process(keepvalues=True).accepted:
        redirect(URL('collection', 'view', args=[form.vars.id], vars=dict(message='new_collection')))

    add_breadcrumb('My Collections', URL('collection', 'my'))
    add_breadcrumb('New Collection')
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
    form.custom.widget.name['requires'] = [IS_STRING_OR(IS_UNIQUE_PER_USER(form.vars.owner,
                                                                           error_message="You already have a collection with this name."),
                                                        response.collection.name),
                                           IS_LENGTH(64, error_message="Please limit the collection name to 64 characters."),
                                           IS_NOT_EMPTY(error_message="Please enter a collection name.")]
    if form.process(keepvalues=True).accepted:
        redirect(URL('collection', 'view', args=[form.vars.id], vars=dict(message='edit_collection')))

    add_breadcrumb('My Collections', URL('collection', 'my'))
    add_breadcrumb('Edit Collection')
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

    add_breadcrumb('My Collections', URL('collection', 'my'))
    add_breadcrumb('Delete Collection')
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

@auth.requires_login()
def wantit():
    o = db(db.object.id == request.args[0]).select().first()
    force = request.vars['force'] == 'true'
    items_with_same_name = db((db.object.owner == auth.user.id)
                              & (db.object.wanted_quantity > 0)
                              & (db.object.name == o.name)).select()
    default = db((db.collection.owner == auth.user.id) & (db.collection.name=='Default')).select().first()

    if len(items_with_same_name) == 0 or force:
        new_item = db.object.insert(**db.object._filter_fields(o))
        db(db.object.id == new_item).update(owner = auth.user.id)
        db(db.object.id == new_item).update(collection = default.id,
                                            quantity = 0,
                                            tradable_quantity = 0,
                                            wanted_quantity = 1)
        if request.vars.url:
            redirect(request.vars.url + ('?' if '?' not in request.vars.url else '&') + 'message=wantit')
        else:
            redirect(URL('collection', 'view', args=[default.id], vars=dict(message='wantit')))
    else:
        redirect(URL('object', 'view', args=[o.id], vars=dict(message='item_already_wanted')))




class IS_UNIQUE_PER_USER(object):
    def __init__(self, user, error_message="error"):
        self.user = user
        self.error_message = error_message

    def __call__(self, value):
        users_collections = db(db.collection.owner == self.user).select()

        for collection in users_collections:
            if collection.name == value:
                return (value, self.error_message)

        return (value, None)
