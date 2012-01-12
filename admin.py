from android import AndroidAdmin, AndroidAdminAdd, AndroidApps,AndroidAdminAddFile
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
def main():
    urls = [('/admin/android', AndroidAdmin),
            ('/admin/android/add',AndroidAdminAdd),
#            ('/admin/android/edit',AndroidAdminEdit),
            ('/admin/android/apps/(.*)',AndroidApps),
            ('/admin/android/add_file/(.*)',AndroidAdminAddFile)
            ]
    application = webapp.WSGIApplication(urls, debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()