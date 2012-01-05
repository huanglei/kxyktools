#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import db
import datetime
import time

taxrate = ((0, 0.03, 0),
           (1500, 0.10, 105),
           (4500, 0.20, 555),
           (9000, 0.25, 1005),
           (35000, 0.30, 2755),
           (55000, 0.35, 5505),
           (80000, 0.45, 13505))

def calcTax(pre_tax):
    taxed_salary = pre_tax - 3500
    if(taxed_salary <= 0):
        return 0
    else:
        for i in range(len(taxrate) - 1, -1, -1):
            if taxed_salary > taxrate[i][0]:
                return taxed_salary * taxrate[i][1] - taxrate[i][2]

class TaxVersion(db.Model):
    version_id = db.StringProperty(required=True)
    is_valid = db.BooleanProperty(required=True)
    start_date = db.DateProperty(required=True)
    end_date = db.DateProperty(required=True)
    threshold_mainland = db.IntegerProperty(required=True)
    threshold_foreign = db.IntegerProperty(required=True)
    remark = db.StringProperty()
    update_time = db.DateTimeProperty()
    update_user = db.EmailProperty()

class TaxRate(db.Model):
    version_id = db.StringProperty(required=True)
    start_from = db.IntegerProperty(required=True)
    end_to = db.IntegerProperty(required=True)
    rate = db.FloatProperty(required=True)
    quick_calc_num = db.IntegerProperty(required=True)
    remark = db.StringProperty()

class ProvinceData(db.Model):
    version_id = db.StringProperty(required=True)
    province = db.StringProperty(required=True)
    max_fundbase = db.IntegerProperty(required=True)

def addTaxVersion():
    vid = time.strftime('%Y%m%d%H%M%S', time.localtime())
    tv = TaxVersion(version_id=vid,
                    is_valid=True,
                    start_date=datetime.datetime.now().date(),
                    end_date=datetime.datetime.now().date())
    tv.put()

def showTaxVersion():
    return db.GqlQuery("SELECT * FROM TaxVersion WHERE is_valid = :1", True)

