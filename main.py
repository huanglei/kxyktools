#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import csv
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from urllib import urlopen
from tax import calcTax
from api import genTestXml
def getComboInfo():
    url = 'http://finance.yahoo.com/d/quotes.csv?s=ASIA+USDCNY=X&f=l1d1'
    data = csv.reader(urlopen(url))
    stockInfo = data.next()
    stock = stockInfo[0]
    date = stockInfo[1]
    exRate = data.next()[0]
    return [date, stock, exRate]

class MainHandler(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, {}))
        
class TaxHandler(webapp.RequestHandler):
    def post(self):
        template_values = {}
        try:
            salary = int(self.request.get('salary', 0))
            m401k = int(self.request.get('m401k', 0))
            pre_tax = salary - m401k
            if(salary < 0 | m401k < 0 | salary < m401k):
                raise ValueError
            tax = calcTax(pre_tax)
            after_tax = pre_tax - tax
            template_values = {
                'salary': salary,
                'm401k': m401k,
                'after_tax':after_tax,
                'tax':tax
                }
        except (TypeError, ValueError):
            template_values = {
                'errInfo': 'Invalid inputs!'
                }
        finally:
            path = os.path.join(os.path.dirname(__file__), 'tax.html')
            self.response.out.write(template.render(path, template_values))
    def get(self):
        self.post()

class AilkHandler(webapp.RequestHandler):
    def post(self):
        template_values = {}
        try:
            shares = int(self.request.get('shares', 0))
            ailkshares = int(shares * 26832731 / 408648658) #联创总股票数:408,648,658.合并交易股票对价:26,832,731
            comboInfo = getComboInfo()
            tradeDate = comboInfo[0]
            stock = float(comboInfo[1])
            exRate = round(float(comboInfo[2]), 3)
            money = round(stock * exRate * ailkshares, 2)

            template_values = {
                'shares': shares,
                'ailkshares': ailkshares,
                'tradeDate': tradeDate,
                'stock': stock,
                'exRate': exRate,
                'money': money
                }
                           
        except (TypeError, ValueError):
            template_values = {
                'errInfo': 'Invalid inputs!'
                }
        finally:
            path = os.path.join(os.path.dirname(__file__), 'ailk.html')
            self.response.out.write(template.render(path, template_values))
    def get(self):
        self.post()
        
##class AilkAjaxHandler(webapp.RequestHandler):
##    def post(self):
##        template_values = {}
##        try:
##            shares = int(self.request.get('shares','0'))
##            ailkshares = int(shares * 26832731/408648658) #联创总股票数:408,648,658.合并交易股票对价:26,832,731
##	    comboInfo = getComboInfo()
##            tradeDate = comboInfo[0]
##            stock = float(comboInfo[1])
##            exRate = round(float(comboInfo[2]),3)
##            money = round(stock * exRate * ailkshares, 2)
##
##            template_values = {
##                'shares': str(shares),
##                'ailkshares': str(ailkshares),
##                'tradeDate': tradeDate,
##                'stock': str(stock),
##                'exRate': str(exRate),
##                'money': str(money)
##                }
##                           
##        except (TypeError, ValueError):
##            template_values = {
##                'errInfo': 'Invalid inputs!'
##                }
##        finally:
##            self.response.out.write(template_values)
##    def get(self):
##        self.post()

class ApiHandler(webapp.RequestHandler):
    def get(self):
        #path = os.path.join(os.path.dirname(__file__), 'index.html')
        #config_date = self.request.get('config_date', "")#后续判断是否20110904234300
        self.response.headers['Content-Type'] = 'text/xml; charset=utf-8'
        self.response.out.write(genTestXml())

from tax import addTaxVersion, showTaxVersion

class ApiHandlerTest(webapp.RequestHandler):
    def get(self):
        addTaxVersion()
        self.response.out.write('add ok')
        
class ApiHandlerTest2(webapp.RequestHandler):
    def get(self):
        tv = showTaxVersion()
        self.response.out.write('<table>')
        for t in tv:
            self.response.out.write('<tr><td>' + t.version_id + '</td><td>' + str(t.start_date) + '</td><td>' + str(t.end_date) + '</td></tr>')
        self.response.out.write('</table>')

from google.appengine.ext import db

class HomeloanRate(db.Model):
    start_date = db.DateProperty(required=True)
    rate_type = db.StringProperty(required=True, choices=set(["fund", "mercantile"]))
    rate1to5 = db.FloatProperty(required=True)
    rate5plus = db.FloatProperty(required=True)

from datetime import date,datetime

class ConfigHandler(webapp.RequestHandler):
    def printRates(self):
        query = HomeloanRate.all().order('-start_date')
        path = os.path.join(os.path.dirname(__file__), 'config.html')
        self.response.out.write(template.render(path, {'query':query}))
    def post(self):
        start_date = self.request.get('start_date')
        rate_type = self.request.get('rate_type')
        rate1to5 = float(self.request.get('rate1to5'))
        rate5plus = float(self.request.get('rate5plus'))
        time_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        hlr = HomeloanRate(start_date=time_start_date,
                           rate_type=rate_type,
                           rate1to5=rate1to5,
                           rate5plus=rate5plus)
        hlr.put()
        self.printRates()
    def get(self):
        self.printRates()
class ConfigAjaxHandler(webapp.RequestHandler):
    def post(self):
        action = self.request.get('action')
        if action == 'del':
            hlr_key = self.request.get('hlr_key')
            HomeloanRate.get(hlr_key).delete()
            self.response.out.write('true')
        else:
            self.response.out.write('false')
			
class AndroidHandler(webapp.RequestHandler):
    def get(self):
        package = self.request.get('package')
        if package == 'com.ss.fozhou':
            self.response.out.write('3')
        else:
            self.response.out.write('0')
			
def main():
    application = webapp.WSGIApplication([
        ('/', MainHandler),
        ('/ailk', AilkHandler),
        ('/tax', TaxHandler),
        ('/config', ConfigHandler),
        ('/config/ajax', ConfigAjaxHandler),
#        ('/ailkajax',AilkAjaxHandler),
        ('/api/tax/config.xml', ApiHandler), #用regex改写
		('/android', AndroidHandler),
        ], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
