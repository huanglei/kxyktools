from google.appengine.ext import db

class HomeloanRate(db.Model):
    start_date = db.DateProperty(required=True)
    rate_type = db.StringProperty(required=True, choices=set(["fund", "mercantile"]))
    rate1to5 = db.IntegerProperty(required=True)
    rate5plus = db.IntegerProperty(required=True)

def addRate(rate):
    rate.put()

def delRate():
    return ""

def getCurrRate(rate_type):
    return HomeloanRate.all().filter('rate_type =', rate_type).order('-start_date').get()

def getCurrFundRate():
    return getCurrRate("fund")

def getCurrMerRate():
    return getCurrRate("mercantile")
