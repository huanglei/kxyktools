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
import re
import os
import csv
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from urllib import urlopen

def getComboInfo():
    url = 'http://finance.yahoo.com/d/quotes.csv?s=ASIA+USDCNY=X&f=l1d1'
    data = csv.reader(urlopen(url))
    stockInfo = data.next()
    stock = stockInfo[0]
    date = stockInfo[1]
    exRate = data.next()[0]
    return [date,stock,exRate]

class MainHandler(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, {}))
        
class TaxHandler(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'tax.html')
        self.response.out.write(template.render(path, {}))

class AilkHandler(webapp.RequestHandler):
    def post(self):
        template_values = {}
        try:
            shares = int(self.request.get('shares','0'))
            ailkshares = int(shares * 26832731/408648658) #联创总股票数:408,648,658.合并交易股票对价:26,832,731
            comboInfo = getComboInfo()
            tradeDate = comboInfo[0]
            stock = float(comboInfo[1])
            exRate = round(float(comboInfo[2]),3)
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
class AilkAjaxHandler(webapp.RequestHandler):
    def post(self):
        template_values = {}
        try:
            shares = int(self.request.get('shares','0'))
            ailkshares = int(shares * 26832731/408648658) #联创总股票数:408,648,658.合并交易股票对价:26,832,731
           # comboInfo = getComboInfo()
           # tradeDate = 
            stock = 8.31
            exRate = 6.398
            money = round(stock * exRate * ailkshares, 2)

            template_values = {
                'shares': str(shares),
                'ailkshares': str(ailkshares),
               # 'tradeDate': tradeDate,
                'stock': str(stock),
                'exRate': str(exRate),
                'money': str(money)
                }
                           
        except (TypeError, ValueError):
            template_values = {
                'errInfo': 'Invalid inputs!'
                }
        finally:
            self.response.out.write(template_values)
    def get(self):
        self.post()
def main():
    application = webapp.WSGIApplication([
        ('/', MainHandler),
        ('/ailk',AilkHandler),
        ('/tax',TaxHandler),
        ('/ailkajax',AilkAjaxHandler),
        ],debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
