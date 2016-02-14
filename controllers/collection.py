def view():
    response.flash = T("Hello World")
    return dict(message=T('Welcome to web2py!'))


def new_collection():

    form=FORM(TABLE(TR("Name",INPUT(_type="text",_name="name",requires=IS_NOT_EMPTY())),
                TR("Public",INPUT(_type="checkbox",_name="name")),
                TR("",INPUT(_type="submit",_value="SUBMIT"))))

    if form.accepts(request,session):
        response.flash = 'form accepted'
        redirect(URL('view' ))

    elif form.errors:
        response.flash = 'form has errors'

    else:
        response.flash = 'please fill the form'

    return  dict(form=form)

def edit_collection():

    form=FORM(TABLE(TR("Name",INPUT(_type="text",_name="name",requires=IS_NOT_EMPTY())),
                TR("Public",INPUT(_type="checkbox",_name="name")),
                TR("",INPUT(_type="submit",_value="SUBMIT"))))

    if form.accepts(request,session):
        response.flash = 'form accepted'

    elif form.errors:
        response.flash = 'form has errors'

    else:
        response.flash = 'please fill the form'

    return  dict(form=form)
