from android import AndroidAdmin, AndroidAdminAdd, AndroidAdminDetail
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
def main():
    urls = [('/admin/android', AndroidAdmin),
            ('/admin/android/add',AndroidAdminAdd),
            ('/admin/android/(.*)', AndroidAdminDetail),
#            ('/admin/android/edit',AndroidAdminEdit),
            ]
    application = webapp.WSGIApplication(urls, debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()