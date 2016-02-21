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
    
    if auth.user.id or selected_users_settings.trade_non_tradable_items:
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
        db.trade_contains_object.insert(trade=current_proposal.id,
                                        object=request.vars['add'],
                                        quantity=1)
    
    if request.vars['remove']:
        db((db.trade_contains_object.trade == current_proposal.id)
           & (db.trade_contains_object.object == request.vars['remove'])).delete()
    
    all_propoal_items = get_items_in_proposal(current_proposal)
    proposal_items_from_sender = all_propoal_items.find(lambda item: item.owner == auth.user.id)
    proposal_items_from_receiver = all_propoal_items.find(lambda item: item.owner == receiver.id)
    
    return dict(search=search,
                receiver=receiver,
                selected_user=selected_user,
                selected_users_collections=selected_users_collections,
                selected_collection=selected_collection,
                all_collection_items=all_collection_items,
                selected_items=selected_items,
                all_propoal_items=all_propoal_items,
                proposal_items_from_sender=proposal_items_from_sender,
                proposal_items_from_receiver=proposal_items_from_receiver)




# Helper Functions

def get_active_proposal(receiver):
    """
    Gets the active proposal with the receiver.
    
    If there isn't an active trade with the receiver a new proposal
    is created.
    """
    if not session.proposals or receiver.id not in session.proposals:
        if not session.proposals:
            session.proposals = {}
        
        if receiver.id not in session.proposals:
            session.proposals[receiver.id] = []
        
        new_proposal_id = db.trade.insert(receiver=receiver.id,
                                          title='Trade with ' + receiver.username)
        new_proposal = db(db.trade.id == new_proposal_id).select().first()
        
        session.proposals[receiver.id].append(new_proposal)
    
    return session.proposals[receiver.id][0]


def get_items_in_proposal(proposal):
    trade_object_links = db(db.trade_contains_object.trade == proposal.id).select()
    
    object_ids = []
    [object_ids.append(link.object) for link in trade_object_links]
    
    return db(db.object.id.belongs(object_ids)).select()
