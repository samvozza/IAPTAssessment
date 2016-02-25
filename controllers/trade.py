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


@auth.requires_login()
def new_proposal():
    if request.vars['with'] == None:
        raise Exception('No user has been specified to trade with (use the \'with\' parameter).')
    
    # Get request parameters
    # Selected user defaults to the user being traded with
    # Search defaults to '' (i.e. all items)
    receiver_id = request.vars['with']
    selected_user_id = (request.vars['user'] if request.vars['user'] else receiver_id)
    search = request.vars['search'] or ''
    
    receiver = db(db.auth_user.id == receiver_id).select().first()
    selected_user = db(db.auth_user.id == selected_user_id).select().first()
    
    selected_users_collections = db((db.collection.owner == selected_user.id)
                                    & (db.collection.public == True)).select()
    
    if request.vars['collection']:
        selected_collection = db(db.collection.id == request.vars['collection']).select().first()
    else:
        selected_collection = selected_users_collections.first()
    
    selected_users_settings = db(db.user_settings.user == selected_user.id).select().first()
    
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
    
    current_proposal = get_active_proposal(receiver)
    
    if request.vars['add']:
        quantity = (request.vars['quantity'] if request.vars['quantity'] else 1)
        link = db((db.trade_contains_object.trade == current_proposal.id)
                  & (db.trade_contains_object.object == request.vars['add']))
        link_results = link.select()

        if len(link_results) > 0:
            new_quantity = link_results.first().quantity + quantity
            link.update(quantity=new_quantity)
        else:
            db.trade_contains_object.insert(trade=current_proposal.id,
                                            object=request.vars['add'],
                                            quantity=quantity)
    
    if request.vars['remove']:
        quantity = (request.vars['quantity'] if request.vars['quantity'] else 1)
        link = db((db.trade_contains_object.trade == current_proposal.id)
                  & (db.trade_contains_object.object == request.vars['remove']))
        new_quantity = link.select().first().quantity - quantity

        assert new_quantity >= 0

        if new_quantity > 0:
            link.update(quantity=new_quantity)
        else:
            db((db.trade_contains_object.trade == current_proposal.id)
               & (db.trade_contains_object.object == request.vars['remove'])).delete()

    all_proposal_items = get_items_in_proposal(current_proposal)

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


def send_proposal():
    db(db.trade.id == request.args(0)).update(status=STATUS_OFFERED)
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
    
    for proposal in session.proposals:
        if proposal.receiver == receiver.id:
            return proposal
    
    new_proposal_id = db.trade.insert(receiver=receiver.id,
                                      title='Trade with ' + receiver.username)
    new_proposal = db(db.trade.id == new_proposal_id).select().first()
    
    session.proposals.append(new_proposal)
    
    return new_proposal


def remove_active_proposal(proposal_id):
    if session.proposals:
        session.proposals = [proposal for proposal in session.proposals if str(proposal.id) != proposal_id]


def get_items_in_proposal(proposal, selected_user=None, selected_users_settings=None):
    trade_item_links = db(db.trade_contains_object.trade == proposal.id).select()

    items = {}
    for link in trade_item_links:
        item = db(db.object.id == link.object).select().first()

        if selected_user and (selected_user.id == auth.user.id or selected_users_settings.trade_non_tradable_items):
            quantity_limit = db(db.object.id == item.id).select().first().quantity
        else:
            quantity_limit = db(db.object.id == item.id).select().first().tradable_quantity

        items[item] = (link.quantity, quantity_limit)
    
    return items
