@auth.requires_login()
def index():
    response.active = db((db.trade.sender == auth.user_id) & (db.trade.status == db.trade.STATUS_ACTIVE)).select()
    response.prepare = db((db.trade.sender == auth.user_id) & (db.trade.status == db.trade.STATUS_PREPARE).select()
    response.sent = db((db.trade.sender == auth.user_id) & (db.trade.status == db.trade.STATUS_SENT).select()
    response.accepted = db((db.trade.sender == auth.user_id) & (db.trade.status == db.trade.STATUS_ACCEPTED).select()
    response.rejected = db((db.trade.sender == auth.user_id) & (db.trade.status == db.trade.STATUS_REJECTED).select()
    response.cancelled = db((db.trade.sender == auth.user_id) & (db.trade.status == db.trade.STATUS_CANCELLED).select()
    return dict()
