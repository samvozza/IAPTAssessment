# -*- coding: utf-8 -*-

# Trade routes


@auth.requires_login()
def index():
    #Prepare: my unsent trade proposals
    response.prepare = db((db.trade.sender == auth.user_id) & (db.trade.status == STATUS_PREPARE)).select()
    #Sent: proposals I am involved in that were most recently edited by me
    response.sent = db(((db.trade.sender == auth.user_id) & (db.trade.status == STATUS_OFFERED))
                       | ((db.trade.receiver == auth.user_id) & (db.trade.status == STATUS_ACTIVE))).select()
    #Received: proposals I am involved in that were most recently edited by the other user
    response.received = db(((db.trade.sender == auth.user_id) & (db.trade.status == STATUS_ACTIVE))
                           | ((db.trade.receiver == auth.user_id) & (db.trade.status == STATUS_OFFERED))).select()
    #Accepted: proposals I am involved in that are now accepted
    response.accepted = db(((db.trade.sender == auth.user_id) | (db.trade.receiver == auth.user_id))
                           & (db.trade.status == STATUS_ACCEPTED)).select()
    #Rejected: proposals I am involved in that are now rejected
    response.rejected = db(((db.trade.sender == auth.user_id) | (db.trade.receiver == auth.user_id))
                           & (db.trade.status == STATUS_REJECTED)).select()
    #Cancelled: proposals I am involved in that are now cancelled
    response.cancelled = db(((db.trade.sender == auth.user_id) | (db.trade.receiver == auth.user_id))
                            & (db.trade.status == STATUS_CANCELLED)).select()

    add_breadcrumb('My Trades')
    return dict()


def view():
    response.trade = db(db.trade.id == request.args(0)).select().first()
    response.receiver = db(db.auth_user.id == response.trade.receiver).select().first()
    response.sender = db(db.auth_user.id == response.trade.sender).select().first()
    trade_item_links = db(db.trade_contains_object.trade == response.trade.id).select()
    trade_items = [db(db.object.id == link.object).select().first() for link in trade_item_links]
    response.sender_items = [item for item in trade_items if item.owner == response.sender.id]
    response.receiver_items = [item for item in trade_items if item.owner == response.receiver.id]
    is_sender = response.sender.username == auth.user.username

    trading_with = response.receiver.username if is_sender else response.sender.username
    add_breadcrumb('My Trades', URL('trade', 'index'))
    add_breadcrumb(DIV('with user ', STRONG(trading_with)))
    response.title = response.trade.title
    return dict()


@auth.requires_login()
def new():
    response.users = []
    other_users = db(db.auth_user.id != auth.user.id).select()

    for user in other_users:
        users_collections_count = db((db.collection.owner == user.id)
                                     & (db.collection.public == True)).count()
        if users_collections_count > 0:
            response.users.append(user)

    add_breadcrumb('My Trades', URL('trade', 'index'))
    add_breadcrumb('New Trade')
    return dict()


@auth.requires_login()
def new_proposal():
    # Short-circuit if a proposal has been specified
    if request.vars['proposal'] != None:
        redirect(URL('trade', 'edit_proposal', args=request.args, vars=request.vars))

    if request.vars['with'] == None and request.vars['receiver'] == None:
        raise EX(500, 'No user has been specified to trade with '
                      + '(use the \'with\' or \'receiver\' parameters).')

    if request.vars['with'] != None:
        receiver = db(db.auth_user.id == request.vars['with']).select().first()
    else:
        receiver = db(db.auth_user.username == request.vars['receiver']).select().first()

    if receiver == None:
        raise EX(500, 'The specified user cannot be found.')

    # Check that the user is not trying to open a proposal with themselves
    if auth.user.id == receiver.id:
        raise EX(500, 'You are trying to open a trade with yourself.')

    # Create a new proposal
    proposal_id = db.trade.insert(receiver=receiver.id)

    # Set the 'trade' parameter switch to the edit_proposal controller
    request.vars['proposal'] = proposal_id
    redirect(URL('trade', 'edit_proposal', args=request.args, vars=request.vars))


@auth.requires_login()
def edit_proposal():
    if request.vars['proposal'] == None:
        raise EX(500, 'No proposal has been specified to edit '
                      + '(use the \'proposal\' parameter).')
    current_proposal = db(db.trade.id == request.vars['proposal']).select().first()

    if current_proposal == None:
        raise EX(500, 'The specified proposal cannot be found.')

    # Check that the logged in user is a participant in the proposal
    if auth.user.id != current_proposal.sender and auth.user.id != current_proposal.receiver:
        raise EX(403, 'You are not involved in this proposal.')

    # Check that the proposal is in the correct state for the user to edit it
    if (not (current_proposal.status == STATUS_PREPARE and auth.user.id == current_proposal.sender)
        and not (current_proposal.status == STATUS_ACTIVE and auth.user.id == current_proposal.sender)
        and not (current_proposal.status == STATUS_OFFERED and auth.user.id == current_proposal.receiver)):
        raise EX(403, 'You are not able to edit this proposal at present.')

    # If the proposal's status id 'OFFERED' then this is a counter-proposal
    # So switch the meaning of the 'receiver' of the proposal
    if current_proposal.status == STATUS_OFFERED:
        receiver = db(db.auth_user.id == current_proposal.sender).select().first()
    else:
        receiver = db(db.auth_user.id == current_proposal.receiver).select().first()

    # If the 'user' parameter isn't specified, default to the receiver
    if request.vars['user']:
        selected_user = db(db.auth_user.id == request.vars['user']).select().first()
    else:
        selected_user = receiver

    selected_users_collections = db((db.collection.owner == selected_user.id)
                                    & (db.collection.public == True)).select()

    # Check that the selected user has at least one collection
    if selected_users_collections.first() == None:
        raise EX(500, 'The selected user doesn\'t have any public collections.')

    # Get the currently displayed collection
    # This defaults to the selected user's first collection
    if request.vars['collection']:
        selected_collection = db(db.collection.id == request.vars['collection']).select().first()
    else:
        selected_collection = selected_users_collections.first()

    # Check that a collection has been selected
    if selected_collection == None:
        raise EX(500, 'The selected collection cannot be found, or does not exist.')

    selected_users_settings = db(db.user_settings.user == selected_user.id).select().first()

    # Get the current search term, if there is one
    search = request.vars['search'] or ''

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

    # Handle adding an item to the trade
    if request.vars['add']:
        quantity = int(request.vars['quantity']) if request.vars['quantity'] else 1
        item = db(db.object.id == request.vars['add']).select().first()
        add_item_to_proposal(current_proposal, item, quantity)
    # Handle removing an item from the trade
    elif request.vars['remove']:
        quantity = int(request.vars['quantity']) if request.vars['quantity'] else 1
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


    add_breadcrumb('My Trades', URL('trade', 'index'))
    add_breadcrumb('Edit Trade Proposal', None)
    response.title = 'Editing Trade Proposal \'' + current_proposal.title + '\''
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


def set_proposal_title():
    if request.vars['proposal'] == None:
        raise EX(500, 'No proposal has been specified (use the \'proposal\' parameter).')
    elif request.vars['title'] == None:
        raise EX(500, 'No title has been specified (use the \'title\' parameter).')

    db(db.trade.id == request.vars['proposal']).update(title=request.vars['title'])


def set_proposal_message():
    if request.vars['proposal'] == None:
        raise EX(500, 'No proposal has been specified (use the \'proposal\' parameter).')
    elif request.vars['message'] == None:
        raise EX(500, 'No message has been specified (use the \'message\' parameter).')

    db(db.trade.id == request.vars['proposal']).update(message=request.vars['message'])


def set_proposal_item_quantity():
    if request.vars['proposal'] == None:
        raise EX(500, 'No proposal has been specified (use the \'proposal\' parameter).')
    elif request.vars['item'] == None:
        raise EX(500, 'No item has been specified (use the \'item\' parameter).')
    elif request.vars['quantity'] == None:
        raise EX(500, 'No quantity has been specified (use the \'quantity\' parameter).')

    trade_item_link_query = db((db.trade_contains_object.trade == request.vars['proposal'])
                               & (db.trade_contains_object.object == request.vars['item']))
    trade_item_link = trade_item_link_query.select().first()

    if trade_item_link:
        trade_item_link_query.update(quantity=request.vars['quantity'])
    else:
        db.trade_contains_object.insert(trade=request.vars['proposal'],
                                        object=request.vars['item'],
                                        quantity=request.vars['quantity'])


def send_proposal():
    proposal_query = db(db.trade.id == request.args(0))
    proposal = proposal_query.select().first()

    # Check that the item quantities are valid
    trade_item_links = db(db.trade_contains_object.trade == request.args(0)).select()
    for trade_item_link in trade_item_links:
        item = db(db.object.id == trade_item_link.object).select().first()
        available_quantity = get_available_quantity(item)
        
        if trade_item_link.quantity > available_quantity:
            raise EX(500, 'You are trying to trade more of this item than is '
                     + 'available.')
        if trade_item_link.quantity < 0:
            raise EX(500, 'You are trying to trade a negative amount of an item.')
        elif trade_item_link.quantity == 0:
            db((db.trade_contains_object.trade == request.args(0))
               & (db.trade_contains_object.object == item.id)).delete()

    if proposal.status == STATUS_OFFERED:
        new_status = STATUS_ACTIVE
    else:
        new_status = STATUS_OFFERED

    proposal_query.update(status=new_status)
    redirect(URL('trade', 'index'))


def accept_proposal():
    db(db.trade.id == request.args(0)).update(status=STATUS_ACCEPTED)
    redirect(URL('trade', 'index'))


def reject_proposal():
    db(db.trade.id == request.args(0)).update(status=STATUS_REJECTED)
    redirect(URL('trade', 'index'))


def cancel_proposal():
    db(db.trade.id == request.args(0)).update(status=STATUS_CANCELLED)
    redirect(URL('trade', 'index'))




# Helper Functions

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

    if new_quantity > quantity_limit:
        raise EX(500, 'The item quantity requested exceeds the available '
                      + 'quantity of this item.')

    if trade_item_link:
        trade_item_link_query.update(quantity=new_quantity)
    else:
        db.trade_contains_object.insert(trade=proposal.id, object=item.id, quantity=new_quantity)


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
    if trade_item_link == None:
        raise EX(500, 'The requested item is not in the current trade '
                      + 'proposal, and so cannot be removed.')

    new_quantity = trade_item_link.quantity - quantity if trade_item_link else quantity

    if new_quantity < 0:
        raise EX(500, 'You have requested to remove more than the '
                      + 'quantity in the current trade proposal.')

    if new_quantity == 0 or remove_entirely:
        trade_item_link_query.delete()
    else:
        trade_item_link_query.update(quantity=new_quantity)
