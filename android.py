# -*- coding: utf-8 -*-
from google.appengine.api import users
from google.appengine.ext import webapp, db
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import blobstore_handlers
import os
import logging
import urllib

#android应用管理页面
class AndroidAdmin(webapp.RequestHandler):
    def post(self):
#        action = self.request.get('action')
#        if(action == 'add'):
#            appName = self.request.get('appName')
#            appPackage = self.request.get('appPackage')
#            versionCode = int(self.request.get('versionCode'))
#            versionName = self.request.get('versionName')
#            addApp(appName, appPackage, versionCode, versionName)
        apps = showAllApps()   
        path = os.path.join(os.path.dirname(__file__), 'android.html')
        isAdmin = users.is_current_user_admin()
        if isAdmin:
            loginlogoutText = 'Logout'
            loginlogoutUrl = users.create_logout_url('/')
        else:
            loginlogoutText = 'Login'
            loginlogoutUrl = users.create_login_url()
        self.response.out.write(template.render(path, {'apps':apps, 'loginlogoutText':loginlogoutText, 'loginlogoutUrl':loginlogoutUrl}))
    def get(self):
        self.post()
        
class AndroidAdminAdd(webapp.RequestHandler):
    def post(self):
        appName = self.request.get('appName')
        appPackage = self.request.get('appPackage')
        versionCode = int(self.request.get('versionCode'))
        versionName = self.request.get('versionName')
        addApp(appName, appPackage, versionCode, versionName)
        self.redirect('/admin/android')
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'android_add.html')
        self.response.out.write(template.render(path, {})) 
             
class AndroidAdminAddFile(blobstore_handlers.BlobstoreUploadHandler):
    def post(self, key):
        appkey = self.request.get('appkey')
        app = App.get(appkey)
        upload_files = self.get_uploads('file')
        blob_info = upload_files[0]
#        blob_key = str(blob_info.key())
        if(app):
            app.appFileBlobKey = str(blob_info.key())
            app.appFileName = blob_info.filename
            app.appFileSize = blob_info.size
            app.put()
        self.redirect('/admin/android')
#        self.redirect('/serve/%s' % blob_info.key())
    def get(self, key):
        upload_url = blobstore.create_upload_url('/admin/android/add_file/')
        path = os.path.join(os.path.dirname(__file__), 'android_add_file.html')
        self.response.out.write(template.render(path, {'upload_url':upload_url, 'appkey':key}))
          
class AndroidDownloader(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info,'application/vnd.android.package-archive',str(blob_info.filename()))
         
class AndroidAdminEdit(webapp.RequestHandler):
    def post(self):
        appName = self.request.get('appName')
        appPackage = self.request.get('appPackage')
        versionCode = int(self.request.get('versionCode'))
        versionName = self.request.get('versionName')
        addApp(appName, appPackage, versionCode, versionName)
        self.redirect('/admin/android')
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'android_edit.html')
        self.response.out.write(template.render(path, {}))  

class AndroidVersionCode(webapp.RequestHandler):
    def get(self, package):
        versionCode = getCurrentVersionCode(package)
        self.response.out.write(versionCode)
        
class AndroidApps(webapp.RequestHandler):
    def post(self, action):
        path = os.path.join(os.path.dirname(__file__), 'android_edit.html')
        self.response.out.write(template.render(path, {}))  
    def get(self, action):
        if(action == 'all' or action == ''):
            suff = ''
        else:
            suff = '_' + action
        path = os.path.join(os.path.dirname(__file__), 'android' + suff + '.html')
        self.response.out.write(template.render(path, {}))  
                                   
class App(db.Model):
    appName = db.StringProperty(required=True)
    appPackage = db.StringProperty(required=True)
    versionCode = db.IntegerProperty(required=True)
    versionName = db.StringProperty(required=True)
    recentChanges = db.StringProperty()
    appFileName = db.StringProperty()
    appFileSize = db.IntegerProperty()
    appFileBlobKey = db.StringProperty()
    
def showAllApps():
    return App.all()

def getCurrentVersionCode(appPackage):
    app = App.gql("where appPackage = :1 order by versionCode desc", appPackage).get()
    if(app):
        return app.versionCode
    else:
        return 0
    

def addApp(appName, appPackage, versionCode, versionName):
    app = App(appName=appName, appPackage=appPackage, versionCode=versionCode, versionName=versionName)
    app.put()
    
def delApp(appPackage, versionCode):
    app = App.gql("where appPackage = :1 and versionCode = :2 ", appPackage, versionCode).get()
    if(app & app.is_saved()):
        app.delete();
    
