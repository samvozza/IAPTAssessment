# -*- coding: utf-8 -*-

# Trade routes

@auth.requires_login()
def index():
    response.active = db((db.trade.sender == auth.user_id) & (db.trade.status == STATUS_ACTIVE)).select()
    response.prepare = db((db.trade.sender == auth.user_id) & (db.trade.status == STATUS_PREPARE)).select()
    response.sent = db((db.trade.sender == auth.user_id) & (db.trade.status == STATUS_OFFERED)).select()
    response.accepted = db((db.trade.sender == auth.user_id) & (db.trade.status == STATUS_ACCEPTED)).select()
    response.rejected = db((db.trade.sender == auth.user_id) & (db.trade.status == STATUS_REJECTED)).select()
    response.cancelled = db((db.trade.sender == auth.user_id) & (db.trade.status == STATUS_CANCELLED)).select()
    return dict()


def new():
    response.users = db().select(db.auth_user.ALL)
    return dict()

@auth.requires_login()
def new_proposal():
    if request.vars['with'] == None and request.vars['receiver'] == None:
        raise Exception('No user has been specified to trade with (use the \'with\' parameter).')

    if request.vars['receiver'] != None:
        receiver_id = db(db.auth_user.username == request.vars['receiver']).select().first().id
    else:
        receiver_id = request.vars['with']

    # Get request parameters
    # Search defaults to '' (i.e. all items)
    # Selected user defaults to the user being traded with
    search = request.vars['search'] or ''
    selected_user_id = (request.vars['user'] if request.vars['user'] else receiver_id)

    receiver = db(db.auth_user.id == receiver_id).select().first()
    selected_user = db(db.auth_user.id == selected_user_id).select().first()

    selected_users_collections = db((db.collection.owner == selected_user.id)
                                    & (db.collection.public == True)).select()

    # Get the currently displayed collection
    # This defaults to the selected user's first collection
    if request.vars['collection']:
        selected_collection = db(db.collection.id == request.vars['collection']).select().first()
    else:
        selected_collection = selected_users_collections.first()

    selected_users_settings = db(db.user_settings.user == selected_user.id).select().first()

    # If the selected user is the current user, or if the selected user allows
    # trading non-tradable items, then get any items that the user has
    # Otherwise, only get items marked as tradable
    if selected_user.id == auth.user.id or selected_users_settings.trade_non_tradable_items:
        all_collection_items = db((db.object.collection == selected_collection.id)
                                  & (db.object.quantity > 0)).select()
        selected_items = db((db.object.collection == selected_collection.id)
                            & (db.object.quantity > 0)
                            & (db.object.name.like('%' + search + '%'))).select()
    else:
        all_collection_items = db((db.object.collection == selected_collection.id)
                                  & (db.object.tradable_quantity > 0)).select()
        selected_items = db((db.object.collection == selected_collection.id)
                            & (db.object.tradable_quantity > 0)
                            & (db.object.name.like('%' + search + '%'))).select()

    # Get the active proposal with the recipient
    # If a proposal doesn't exist then create one
    current_proposal = get_active_proposal(receiver)

    # Handle adding an item to the trade
    if request.vars['add']:
        quantity = request.vars['quantity'] or 1
        item = db(db.object.id == request.vars['add']).select().first()
        add_item_to_proposal(current_proposal, item, quantity)
    # Handle removing an item from the trade
    elif request.vars['remove']:
        quantity = request.vars['quantity'] or 1
        remove_entirely = request.vars['quantity'] == None
        item = db(db.object.id == request.vars['remove']).select().first()
        remove_item_from_proposal(current_proposal, item, quantity, remove_entirely)

    # Get all the items in the current proposal
    all_proposal_items = get_items_in_proposal(current_proposal)

    # Split the full dict of items into the sender's and receiver's items
    proposal_items_from_sender = {}
    proposal_items_from_receiver = {}
    for item in all_proposal_items:
        quantity = all_proposal_items[item]
        if item.owner == auth.user.id:
            proposal_items_from_sender[item] = quantity
        else:
            proposal_items_from_receiver[item] = quantity

    return dict(search=search,
                receiver=receiver,
                selected_user=selected_user,
                selected_users_collections=selected_users_collections,
                selected_collection=selected_collection,
                all_collection_items=all_collection_items,
                selected_items=selected_items,
                current_proposal=current_proposal,
                all_proposal_items=all_proposal_items,
                proposal_items_from_sender=proposal_items_from_sender,
                proposal_items_from_receiver=proposal_items_from_receiver)


def set_proposal_message():
    if request.vars['proposal'] == None:
        raise Exception('No proposal has been specified (use the \'proposal\' parameter).')
    elif request.vars['message'] == None:
        raise Exception('No message has been specified (use the \'message\' parameter).')

    proposal_id = request.vars['proposal']
    message = request.vars['message']

    db(db.trade.id == proposal_id).update(message=message)


def send_proposal():
    message = request.vars['message'] if request.vars['message'] else ''
    db(db.trade.id == request.args(0)).update(status=STATUS_OFFERED, message=message)
    remove_active_proposal(request.args(0))
    redirect(URL('trade', 'index'))


def accept_proposal():
    db(db.trade.id == request.args(0)).update(status=STATUS_ACCEPTED)
    remove_active_proposal(request.args(0))
    redirect(URL('trade', 'index'))


def reject_proposal():
    db(db.trade.id == request.args(0)).update(status=STATUS_REJECTED)
    remove_active_proposal(request.args(0))
    redirect(URL('trade', 'index'))


def cancel_proposal():
    db(db.trade.id == request.args(0)).update(status=STATUS_CANCELLED)
    remove_active_proposal(request.args(0))
    redirect(URL('trade', 'index'))




# Helper Functions

def get_active_proposal(receiver):
    """
    Gets the active proposal with the receiver.

    If there isn't an active trade with the receiver a new proposal
    is created.
    """
    if not session.proposals:
        session.proposals = []

    # If a proposal already exists then return it
    for proposal_pair in session.proposals:
        if proposal_pair[0] == receiver.id:
            return db(db.trade.id == proposal_pair[1]).select().first()

    # Otherwise create a new proposal
    proposal_id = db.trade.insert(receiver=receiver.id, title='Trade with ' + receiver.username)
    session.proposals.append((receiver.id, proposal_id))

    return db(db.trade.id == proposal_id).select().first()


def remove_active_proposal(proposal_id):
    """
    Removes a proposal from the session.
    """
    if session.proposals:
        session_proposals = []
        for proposal_pair in session.proposals:
            if str(proposal_pair[1]) != proposal_id:
                session_proposals.append(proposal_pair)


def get_available_quantity(item):
    """
    Gets the available quantity of an item.

    If the current user owns the item, or if the item's owner allows trading
    non-tradable items, this returns the item's quantity.
    Otherwise this returns the item's *tradable* quantity.
    """
    if auth.user and item.owner == auth.user.id:
            return db(db.object.id == item.id).select().first().quantity
    else:
        owners_settings = db(db.user_settings.user == item.owner).select().first()
        if owners_settings.trade_non_tradable_items:
            return db(db.object.id == item.id).select().first().quantity

    return db(db.object.id == item.id).select().first().tradable_quantity


def get_items_in_proposal(proposal):
    """
    Gets the items in the specified proposal.

    This returns a dict with the structure:
    {
    <item>: (<quantity_in_trade>, <total_quantity>)
    ...
    }
    """
    trade_item_links = db(db.trade_contains_object.trade == proposal.id).select()

    items = {}
    for link in trade_item_links:
        item = db(db.object.id == link.object).select().first()
        quantity_limit = get_available_quantity(item)
        items[item] = (link.quantity, quantity_limit)

    return items


def add_item_to_proposal(proposal, item, quantity=1):
    """
    Adds the specified item to the specified proposal.

    Checks that the quantity in the trade doesn't exceed the available
    quantity.
    """
    trade_item_link_query = db((db.trade_contains_object.trade == proposal.id)
                               & (db.trade_contains_object.object == item.id))
    trade_item_link = trade_item_link_query.select().first()
    new_quantity = trade_item_link.quantity + quantity if trade_item_link else quantity

    quantity_limit = get_available_quantity(item)

    assert new_quantity <= quantity_limit

    if trade_item_link:
        trade_item_link_query.update(quantity=new_quantity)
    else:
        db.trade_contains_object.insert(trade=proposal.id, object=item.id, quantity=quantity)


def remove_item_from_proposal(proposal, item, quantity=1, remove_entirely=False):
    """
    Removes a quantity of the specified item from the specified proposal.

    Checks that the quantity in the trade doesn't drop below zero.

    Raises an exception if the specified item isn't already in the
    specified proposal.
    """
    trade_item_link_query = db((db.trade_contains_object.trade == proposal.id)
                               & (db.trade_contains_object.object == item.id))
    trade_item_link = trade_item_link_query.select().first()

    # If the item isn't in the trade, raise an exception
    assert trade_item_link is not None

    new_quantity = trade_item_link.quantity - quantity if trade_item_link else quantity

    assert new_quantity >= 0

    if new_quantity == 0 or remove_entirely:
        trade_item_link_query.delete()
    else:
        trade_item_link_query.update(quantity=new_quantity)
