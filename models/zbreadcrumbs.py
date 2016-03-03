# Breadcrumbs are represented as a 3-tuple:
# (<text>, <link>, <title>)
#
# <text>  -> the text to display in the breadcrumb
# <link>  -> the link to use for the breadcrumb if this is not
#            set, the breadcrumb will not be given a hyperlink
# <title> -> the page title
#            if this is not set, the title defaults to the
#            breadcrumb's text


class Breadcrumb(object):
    def __init__(self, text, link=None, title=None):
        self._text = text
        self._link = link
        self._title = title or text

    def title(self):
        return self._title
    
    def make_link(self, active=False):
        if active:
            return LI(self._text, _class='active')
        elif self._link == None:
            return LI(self._text)
        else:
            return LI(A(self._text, _href=self._link))


def start_breadcrumbs():
    if response.breadcrumbs == None:
        response.breadcrumbs = [Breadcrumb('Home', URL('default', 'index'))]


def add_breadcrumb(text, link=None, title=None):
    start_breadcrumbs()
    breadcrumb = Breadcrumb(text, link, title)
    response.breadcrumbs.append(breadcrumb)


def page_title():
    start_breadcrumbs()
    return response.breadcrumbs[-1].title()


def make_breadcrumbs():
    start_breadcrumbs()
    
    breadcrumbs = []
    for breadcrumb in response.breadcrumbs[:-1]:
        breadcrumbs.append(breadcrumb.make_link())
    
    breadcrumbs.append(response.breadcrumbs[-1].make_link(True))
    return breadcrumbs
