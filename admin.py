#!/usr/bin/env python
# -*- coding: utf-8 -*-
from android import AndroidAdmin, AndroidAdminAdd, AndroidAdminDetail, \
    AndroidAdminAddFile, AndroidAdminEditFile, AndroidAdminDel, AndroidAdminInit
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
def main():
    urls = [('/admin/android', AndroidAdmin),
            ('/admin/android/add', AndroidAdminAdd),
            ('/admin/android/add_file/(.*)', AndroidAdminAddFile),
            ('/admin/android/edit_file/(.*)', AndroidAdminEditFile),
            ('/admin/android/del', AndroidAdminDel),
            ('/admin/android/init', AndroidAdminInit),
            ('/admin/android/(.*)', AndroidAdminDetail),
#            ('/admin/android/edit',AndroidAdminEdit),
            ]
    application = webapp.WSGIApplication(urls, debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()