def view():
    response.collections = db(db.collection.owner == '1').select()
    return dict(message=T('Welcome to web2py!'))


def create():
    if(not auth.is_logged_in()):
        redirect(URL('default', 'index'))
        return

    form=FORM(
              DIV(DIV(LABEL('Name'),_class='col-sm-12 col-md-12 col-lg-12'),
                  DIV(INPUT(_id='Name', _class='form-control', _name='Name',
                            requires=[IS_NOT_EMPTY(error_message='Please pick a name'),
                            IS_NOT_IN_DB(db, 'collection.name',
                            error_message=('This collection already exists. '
                            + 'Please try a different title.'))]),
                            _class='col-sm-6 col-md-6 col-lg-6'),
                            DIV(P('Enter a name for your collection',
                                _class='form-field-description'),
                                _class='col-sm-8 col-md-8 col-lg-8'),
                                _class='form-group row'),

              DIV(DIV(LABEL('Public'),_class='col-sm-12 col-md-12 col-lg-12'),
                  DIV(SELECT('yes', 'no', _id='title-field', _class='form-control', _name='title'),
                      _class='col-sm-6 col-md-6 col-lg-6'),
                      DIV(P('This determines if other users can see the objects in your collection ',
                          _class='form-field-description'),
                          _class='col-sm-8 col-md-8 col-lg-8'),
                          _class='form-group row'),

              DIV(DIV(INPUT(_id='submit-button', _name='Submit', _type='submit',
                     _value='Submit', _class='btn btn-primary pull-right'),
                     _class='col-sm-6 col-md-6 col-lg-6'),
                     DIV(_class='col-sm-6 col-md-6 col-lg-6')),
              )

    form.vars.owner = 1

    if form.accepts(request,session):
            response.flash = 'Collection created.'
            redirect(URL('view'))

    elif form.errors:
        response.flash = "We couldn't process your form because it contain errors. Check below for more detail."

    else:
        response.flash = 'Use the form below to create a new collection.'

    return  dict(form=form)

def edit():
    if(not auth.is_logged_in()):
        redirect(URL('default', 'index'))
        return
        
    form=FORM(
              DIV(DIV(LABEL('Name'),_class='col-sm-12 col-md-12 col-lg-12'),
                  DIV(INPUT(_id='Name', _class='form-control', _name='Name',
                            requires=[IS_NOT_EMPTY(error_message='Please pick a name')]),
                            _class='col-sm-6 col-md-6 col-lg-6'),
                            DIV(P('Enter a name for your collection',
                                _class='form-field-description'),
                                _class='col-sm-8 col-md-8 col-lg-8'),
                                _class='form-group row'),

              DIV(DIV(LABEL('Public'),_class='col-sm-12 col-md-12 col-lg-12'),
                  DIV(SELECT('yes', 'no', _id='title-field', _class='form-control', _name='title'),
                      _class='col-sm-6 col-md-6 col-lg-6'),
                      DIV(P('This determines if other users can see the objects in your collection ',
                          _class='form-field-description'),
                          _class='col-sm-8 col-md-8 col-lg-8'),
                          _class='form-group row'),

              DIV(DIV(INPUT(_id='submit-button', _name='Submit', _type='submit',
                     _value='Submit', _class='btn btn-primary pull-right'),
                     _class='col-sm-6 col-md-6 col-lg-6'),
                     DIV(_class='col-sm-6 col-md-6 col-lg-6')),
              )

    form.vars.owner = 1

    if form.accepts(request,session):
            response.flash = 'Your collection updated.'
            redirect(URL('view'))

    elif form.errors:
        response.flash = "We couldn't process your form because it contain errors. Check below for more detail."

    else:
        response.flash = 'Use the form below to update a collection.'

    return  dict(form=form)

def my():
    redirect(URL('collection', 'view', args=['1']))
