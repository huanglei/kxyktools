# -*- coding: utf-8 -*-
from google.appengine.api import users
from google.appengine.ext import blobstore, webapp, db
from google.appengine.ext.webapp import blobstore_handlers, template
from google.appengine.ext.blobstore import BlobInfo
import os
import urllib

#android应用管理页面
class AndroidAdmin(webapp.RequestHandler):
    def post(self):
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
class AndroidAdminDetail(webapp.RequestHandler):
    def get(self, param):
        param_str = str(urllib.unquote(param))
        param_str = param_str.rstrip("/")
        params = param_str.split("/")
        if(len(params) == 1):
            path = os.path.join(os.path.dirname(__file__), 'android_detail.html')
            apps = App.gql("where appPackage = :1 order by versionCode desc", params)
            self.response.out.write(template.render(path, {'apps':apps}))
        elif(len(params) == 2):
            app = App.gql("where appPackage = :1 and versionCode = :2 order by versionCode desc", str(params[0]), int(params[1])).get()
            if(app):
                self.response.out.write(app.appName + "\n" + app.versionName)
            else:
                self.response.out.write("no app:[" + params[0] + "],[" + params[1] + "]")
        else:
            self.response.out.write("param:" + param)
               
class AndroidAdminAdd(webapp.RequestHandler):
    def post(self):
        appName = self.request.get('appName')
        appPackage = self.request.get('appPackage')
        versionCode = int(self.request.get('versionCode'))
        versionName = self.request.get('versionName')
        addApp(appName, appPackage, versionCode, versionName)
        self.redirect('/admin/android')
    def get(self):
#        appkey = self.request.get('appkey')
#        params = {}
#        if(appkey):
#            app = App.get(appkey)
#            if(app):
#                defaultAppName = app.appName
#                defaultAppPackage = app.appPackage
#                defaultVersionCode = app.versionCode
#                defaultVersionName = app.versionName
#                params = {'defaultAppName':defaultAppName, 'defaultAppPackage':defaultAppPackage, 'defaultVersionCode':defaultVersionCode, 'defaultVersionName':defaultVersionName}
        path = os.path.join(os.path.dirname(__file__), 'android_add.html')
        self.response.out.write(template.render(path, {})) 

class AndroidAdminDel(webapp.RequestHandler):
    def post(self):
        appkey = self.request.get('appkey')
        app = App.get(appkey)
        result = deleteApp(app)
        self.response.out.write("{\"result\":\"" + str(result) + "\"}")
                     
class AndroidAdminAddFile(blobstore_handlers.BlobstoreUploadHandler):
    def post(self, key):
        appkey = self.request.get('appkey')
        app = App.get(appkey)
        upload_files = self.get_uploads('file')
        blob_info = upload_files[0]
        if(app):
            app.appFileBlobKey = str(blob_info.key())
            app.appFileName = blob_info.filename
            app.appFileSize = blob_info.size
            app.put()
        self.redirect('/admin/android')
    def get(self, key):
        upload_url = blobstore.create_upload_url('/admin/android/add_file/')
        path = os.path.join(os.path.dirname(__file__), 'android_add_file.html')
        self.response.out.write(template.render(path, {'upload_url':upload_url, 'appkey':key}))
        
class AndroidAdminEditFile(blobstore_handlers.BlobstoreUploadHandler):
    def post(self, key):
        appkey = self.request.get('appkey')
        app = App.get(appkey)
        upload_files = self.get_uploads('file')
        blob_info = upload_files[0]
        if(app):
            if(app.appFileBlobKey and BlobInfo.get(app.appFileBlobKey)):
                BlobInfo.get(app.appFileBlobKey).delete()
            app.appFileBlobKey = str(blob_info.key())
            app.appFileName = blob_info.filename
            app.appFileSize = blob_info.size
            app.put()
        self.redirect('/admin/android')
    def get(self, key):
        upload_url = blobstore.create_upload_url('/admin/android/edit_file/')
        path = os.path.join(os.path.dirname(__file__), 'android_add_file.html')
        self.response.out.write(template.render(path, {'upload_url':upload_url, 'appkey':key}))
              
class AndroidDownloader(blobstore_handlers.BlobstoreDownloadHandler):
    """apk下载统一入口"""
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_key = None;
        if(resource.find("/") >= 0):
            params = resource.split("/")
            if(len(params) == 2):
                appPackage = params[0]
                appVersion = params[1]
                blob_key = getAppBlobKey(appPackage, appVersion)
        else:
            blob_key = resource
        if(blob_key):
            blob_info = blobstore.BlobInfo.get(blob_key)
            self.send_blob(blob_info, 'application/vnd.android.package-archive', True)
        else:
            self.error(404)
            
class Downloader(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info, None, True)        
             
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
        
class AndroidAdminInit(webapp.RequestHandler):
    def post(self):
        for app in App.all():
            app.delete()
        addApp(u"佛咒","com.ss.fozhou",1,"1.0.0")
        addApp(u"佛咒","com.ss.fozhou",2,"1.0.1")
        addApp(u"佛咒","com.ss.fozhou",3,"1.0.2")
        addApp(u"佛咒","com.ss.fozhou",4,"1.1.0")
        addApp(u"个税计算器","info.kxyk.taxcalc",1,"1.0.0")
        addApp(u"汇率计算器","info.kxyk.erc",1,"1.0.0")
        addApp(u"汇率计算器","info.kxyk.erc",2,"1.0.1")
        addApp(u"汇率计算器","info.kxyk.erc",3,"1.0.2")
        
class App(db.Model):
    appName = db.StringProperty(required=True)
    appPackage = db.StringProperty(required=True)
    versionCode = db.IntegerProperty(required=True)
    versionName = db.StringProperty(required=True)
#    recentChanges = db.StringProperty()
    appFileName = db.StringProperty()
    appFileSize = db.IntegerProperty()
    appFileBlobKey = db.StringProperty()
   
def showAllApps():
    return App.gql(" order by appPackage,versionCode desc")

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
    if(app and app.is_saved()):
        if(app.appFileBlobKey and BlobInfo.get(app.appFileBlobKey)):
                BlobInfo.get(app.appFileBlobKey).delete()
        app.delete()
        
def deleteApp(app):
    if(app and app.is_saved()):
        if(app.appFileBlobKey and BlobInfo.get(app.appFileBlobKey)):
                BlobInfo.get(app.appFileBlobKey).delete()
        app.delete()
        return True
        
def getAppBlobKey(appPackage, versionName):
    app = None
    if(versionName == "latest" or versionName == "newest"):
        app = App.gql("where appPackage = :1 order by versionCode desc", appPackage).get()
    else:    
        app = App.gql("where appPackage = :1 and versionName = :2 order by versionCode desc", appPackage, versionName).get()
    if(app):
        return app.appFileBlobKey
    return None
    
