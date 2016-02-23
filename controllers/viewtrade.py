@auth.requires_login()
def viewtradestatus():
#Get the id from the user who trades with login user.
	trade_with_receiver = db.auth_user(request.args(0))
	trade_with_sender = db.auth_user(request.args(0))

##Login user as a sender.
	sender_query = (db.trade.sender == auth.user_id) & (db.trade.receiver == trade_with_receiver)	
#select trade, login user as a sender, status == STATUS_PREPARE	
	act_trade_snder0 = db(sender_query & (db.trade.status == '0')).select()
#select trade, login user as a sender, status == STATUS_ACTIVE
	act_trade_snder1 = db(sender_query & (db.trade.status == '1')).select()
#select trade, login user as a sender, status == STATUS_OFFERED
	act_trade_snder2 = db(sender_query & (db.trade.status == '2')).select()	
#select trade, login user as a sender, status ==  STATUS_ACCEPTED
	act_trade_snder3 = db(sender_query & (db.trade.status == '3')).select()
#select trade, login user as a sender, status ==  STATUS_REJECTED
	act_trade_snder4 = db(sender_query & (db.trade.status == '4')).select()
#select trade, login user as a sender, status ==  STATUS_CANCELLED
	act_trade_snder5 = db(sender_query & (db.trade.status == '5')).select()
	
##Login user as a receiver.	
	receiver_query = (db.trade.sender == trade_with_receiver) & (db.trade.receiver == auth.user_id)
#select trade, login user as a receiver, status == STATUS_ACTIVE
	act_trade_rcver1 = db(receiver_query & (db.trade.status == '1')).select()
#select trade, login user as a receiver, status == STATUS_OFFERED
	act_trade_rcver2 = db(receiver_query & (db.trade.status == '2')).select()	
#select trade, login user as a receiver, status == STATUS_ACCEPTED
	act_trade_rcver3 = db(receiver_query & (db.trade.status == '3')).select()
#select trade, login user as a receiver, status == STATUS_REJECTED
	act_trade_rcver4 = db(receiver_query & (db.trade.status == '4')).select()
#select trade, login user as a receiver, status == STATUS_CANCELLED
	act_trade_rcver5 = db(receiver_query & (db.trade.status == '5')).select()
	
	return dict(act_trade_snder0 = act_trade_snder0, act_trade_snder1 = act_trade_snder1, act_trade_snder2 = act_trade_snder2,
				act_trade_snder3 = act_trade_snder3, act_trade_snder4 = act_trade_snder4, act_trade_snder5 = act_trade_snder5,
				act_trade_rcver1 = act_trade_rcver1, act_trade_rcver2 = act_trade_rcver2, act_trade_rcver3 = act_trade_rcver3,
				act_trade_rcver4 = act_trade_rcver4, act_trade_rcver5 = act_trade_rcver5)


#The function fetches the information of a trade.
#It returns the details of the trade in db.trade, objects from the sender and objects from the receiver.
def tradesummary():
#get the corresponding trade.id
	trade_id = db.trade(request.args(0))
	trade_record = db(db.trade.id == trade_id).select()
	sender_id = db(db.trade.id == trade_id)._select(db.trade.sender)
	receiver_id = db(db.trade.id == trade_id)._select(db.trade.receiver)	
	trade_items = db(db.trade_contains_object.trade == trade_id).select()
	group_trade_items = []
	[group_trade_items.append(each.object) for each in trade_items]
	sender_items = db(db.object.id.belongs(group_trade_items) & db.object.owner.belongs(sender_id)).select()
	receiver_items = db(db.object.id.belongs(group_trade_items) & db.object.owner.belongs(receiver_id)).select()	
	return dict(trade_record = trade_record, sender_items = sender_items, receiver_items = receiver_items)

