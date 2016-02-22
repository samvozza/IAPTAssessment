@auth.requires_login()
def viewtradestatus():
##Login user as a sender.
#select trade(active), login user as a sender, status == STATUS_PREPARE
	trd_act_s0 = db((db.trade.sender == auth.user_id) & (db.trade.status == 0))._select(db.trade.id)
	act_trade_snder0 = db((db.trade_contains_object.trade.belongs(trd_act_s0)) & (db.trade.id.belongs(trd_act_s0))).select()	
#select trade(active), login user as a sender, status == STATUS_ACTIVE
	trd_act_s1 = db((db.trade.sender == auth.user_id) & (db.trade.status == 1))._select(db.trade.id)
	act_trade_snder1 = db((db.trade_contains_object.trade.belongs(trd_act_s1)) & (db.trade.id.belongs(trd_act_s1))).select()
#select trade(active), login user as a sender, status == STATUS_OFFERED 
	trd_act_s2 = db((db.trade.sender == auth.user_id) & (db.trade.status == 2))._select(db.trade.id)
	act_trade_snder2 = db((db.trade_contains_object.trade.belongs(trd_act_s2)) & (db.trade.id.belongs(trd_act_s2))).select()
#select trade(close), login user as a sender, status ==  STATUS_ACCEPTED
	trd_act_s3 = db((db.trade.sender == auth.user_id) & (db.trade.status == 3))._select(db.trade.id)
	act_trade_snder3 = db((db.trade_contains_object.trade.belongs(trd_act_s3)) & (db.trade.id.belongs(trd_act_s3))).select()
#select trade(close), login user as a sender, status ==  STATUS_REJECTED
	trd_act_s4 = db((db.trade.sender == auth.user_id) & (db.trade.status == 4))._select(db.trade.id)
	act_trade_snder4 = db((db.trade_contains_object.trade.belongs(trd_act_s4)) & (db.trade.id.belongs(trd_act_s4))).select()
#select trade(close), login user as a sender, status ==  STATUS_CANCELLED
	trd_act_s5 = db((db.trade.sender == auth.user_id) & (db.trade.status == 5))._select(db.trade.id)
	act_trade_snder5 = db((db.trade_contains_object.trade.belongs(trd_act_s5)) & (db.trade.id.belongs(trd_act_s5))).select()
	
##Login user as a receiver.	
#select trade(active), login user as a receiver, status == STATUS_ACTIVE
	trd_act_r1 =  db((db.trade.receiver == auth.user_id) & (db.trade.status == 1))._select(db.trade.id)
	act_trade_rcver1 = db((db.trade_contains_object.trade.belongs(trd_act_r1)) & (db.trade.id.belongs(trd_act_r1))).select()
#select trade(active), login user as a receiver, status == STATUS_OFFERED
	trd_act_r2 =  db((db.trade.receiver == auth.user_id) & (db.trade.status == 2))._select(db.trade.id)
	act_trade_rcver2 = db((db.trade_contains_object.trade.belongs(trd_act_r2)) & (db.trade.id.belongs(trd_act_r2))).select()	
#select trade(close), login user as a receiver, status == STATUS_ACCEPTED
	trd_act_r3 =  db((db.trade.receiver == auth.user_id) & (db.trade.status == 3))._select(db.trade.id)
	act_trade_rcver3 = db((db.trade_contains_object.trade.belongs(trd_act_r3)) & (db.trade.id.belongs(trd_act_r3))).select()
#select trade(close), login user as a receiver, status == STATUS_REJECTED
	trd_act_r4 =  db((db.trade.receiver == auth.user_id) & (db.trade.status == 4))._select(db.trade.id)
	act_trade_rcver4 = db((db.trade_contains_object.trade.belongs(trd_act_r4)) & (db.trade.id.belongs(trd_act_r4))).select()
#select trade(close), login user as a receiver, status == STATUS_CANCELLED
	trd_act_r5 =  db((db.trade.receiver == auth.user_id) & (db.trade.status == 5))._select(db.trade.id)
	act_trade_rcver5 = db((db.trade_contains_object.trade.belongs(trd_act_r5)) & (db.trade.id.belongs(trd_act_r5))).select()
	
	return dict(act_trade_snder0 = act_trade_snder0, act_trade_snder1 = act_trade_snder1, act_trade_snder2 = act_trade_snder2,
				act_trade_snder3 = act_trade_snder3, act_trade_snder4 = act_trade_snder5, act_trade_snder5 = act_trade_snder5,
				act_trade_rcver1 = act_trade_rcver1, act_trade_rcver2 = act_trade_rcver2, act_trade_rcver3 = act_trade_rcver3,
				act_trade_rcver4 = act_trade_rcver4, act_trade_rcver5 = act_trade_rcver5)
