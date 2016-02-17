def view():
    response.collection = db(db.collection.id == request.args[0]).select().first()
    response.q = request.vars.q if request.vars.q != None else ''
    response.collections = db(db.collection.owner == response.collection.owner).select()
    response.objects = db((db.object.collection == response.collection.id) & (db.object.name.like('%' +response.q+'%'))).select()
    response.tradable = db((db.object.collection == response.collection.id) &  (db.object.name.like('%' +response.q+'%')) & (db.object.tradable_quantity > 0)).select()
    response.wanted = db((db.object.collection == response.collection.id) & (db.object.name.like('%' +response.q+'%')) & (db.object.wanted_quantity > 0)).select()
    response.owned = db((db.object.collection == response.collection.id) & (db.object.name.like('%' +response.q+'%')) & (db.object.quantity > 0)).select()
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
              % URL('collection','view', args=[request.args[0]]), _class='btn btn-primary pull-right'),
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
              URL('collection','view', args=[collection.id]), _class='btn btn-primary pull-right'),
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

@auth.requires_login()
def my():
    response.col = db(db.collection.owner == auth.user_id).select().first()
    redirect(URL('collection', 'view', args=[response.col.id]))

def user():
    response.col = db((db.collection.owner == request.args[0]) & (db.collection.public == 'T')).select().first()
    redirect(URL('collection', 'view', args=[response.col.id]))
