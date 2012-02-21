# -*- coding: utf-8 -*-
from google.appengine.api import users
from google.appengine.ext import blobstore, webapp, db
from google.appengine.ext.webapp import blobstore_handlers, template
import os
import urllib

class Apps(db.Model):
    appName = db.StringProperty(required=True)
    appPackage = db.StringProperty(required=True)
    appVersionNum = db.IntegerProperty(required=True)
    appNewestVersionCode = db.IntegerProperty(required=True)
    appNewestVersionName = db.StringProperty(required=True)
     
class AppVersions(db.Model):
    appName = db.StringProperty(required=True)
    appPackage = db.StringProperty(required=True)
    versionCode = db.IntegerProperty(required=True)
    versionName = db.StringProperty(required=True)
#    recentChanges = db.StringProperty()
    appFileName = db.StringProperty()
    appFileSize = db.IntegerProperty()
    appFileBlobInfo = blobstore.BlobReferenceProperty()
    
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
            apps = AppVersions.gql("where appPackage = :1 order by versionCode desc", params)
            self.response.out.write(template.render(path, {'apps':apps}))
        elif(len(params) == 2):
            app = AppVersions.gql("where appPackage = :1 and versionCode = :2 order by versionCode desc", str(params[0]), int(params[1])).get()
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
    def get(self, appkey):
        params = {}
        if(appkey):
            app = AppVersions.get(appkey)
            if(app):
                defaultAppName = app.appName
                defaultAppPackage = app.appPackage
                defaultVersionCode = app.versionCode
                defaultVersionName = app.versionName
                params = {'defaultAppName':defaultAppName, 'defaultAppPackage':defaultAppPackage, 'defaultVersionCode':defaultVersionCode, 'defaultVersionName':defaultVersionName}
        path = os.path.join(os.path.dirname(__file__), 'android_add.html')
        self.response.out.write(template.render(path, params)) 

class AndroidAdminApi(webapp.RequestHandler):
    def get(self):
        apps = showAllApps()
        path = os.path.join(os.path.dirname(__file__), 'android_api.html')
        self.response.out.write(template.render(path, {'apps':apps})) 
        
class AndroidAdminDel(webapp.RequestHandler):
    def post(self):
        appkey = self.request.get('appkey')
        app = AppVersions.get(appkey)
        result = deleteApp(app)
        self.response.out.write("{\"result\":\"" + str(result) + "\"}")

class AndroidAdminDelApp(webapp.RequestHandler):
    def post(self):
        appkey = self.request.get('appkey')
        app = Apps.get(appkey)
        if(app.appVersionNum == 0):
            app.delete()
            result = 'True'
        else:
            result = 'please delete AppVersions'
        self.response.out.write("{\"result\":\"" + str(result) + "\"}")
                             
class AndroidAdminAddFile(blobstore_handlers.BlobstoreUploadHandler):
    def post(self, key):
        appkey = self.request.get('appkey')
        app = AppVersions.get(appkey)
        upload_files = self.get_uploads('file')
        blob_info = upload_files[0]
        if(app):
            app.appFileBlobInfo = blob_info
            app.appFileName = blob_info.filename
            app.appFileSize = blob_info.size
            app.put()
        self.redirect('/admin/android/' + app.appPackage)
    def get(self, key):
        upload_url = blobstore.create_upload_url('/admin/android/add_file/')
        path = os.path.join(os.path.dirname(__file__), 'android_add_file.html')
        self.response.out.write(template.render(path, {'upload_url':upload_url, 'appkey':key}))
        
class AndroidAdminEditFile(blobstore_handlers.BlobstoreUploadHandler):
    def post(self, key):
        appkey = self.request.get('appkey')
        app = AppVersions.get(appkey)
        upload_files = self.get_uploads('file')
        blob_info = upload_files[0]
        if(app):
            if(app.appFileBlobInfo):
                app.appFileBlobInfo.delete()
            app.appFileBlobInfo = blob_info
            app.appFileName = blob_info.filename
            app.appFileSize = blob_info.size
            app.put()
        self.redirect('/admin/android/' + app.appPackage)
    def get(self, key):
        upload_url = blobstore.create_upload_url('/admin/android/edit_file/')
        path = os.path.join(os.path.dirname(__file__), 'android_add_file.html')
        self.response.out.write(template.render(path, {'upload_url':upload_url, 'appkey':key}))
              
class AndroidDownloader(blobstore_handlers.BlobstoreDownloadHandler):
    """apk下载统一入口"""
    def get(self, resource):
        resource = str(urllib.unquote(resource)).rstrip("/")
        blob_info = None;
        if(resource.find("/") >= 0):
            params = resource.split("/")
            if(len(params) == 2):
                appPackage = params[0]
                appVersion = params[1]
                blob_info = getAppBlobInfo(appPackage, appVersion)
        else:
            blob_key = resource
            blob_info = blobstore.BlobInfo.get(blob_key)
        if(blob_info):
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
        self.redirect('/admin/android/')
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'android_edit.html')
        self.response.out.write(template.render(path, {}))  

class AndroidVersionCode(webapp.RequestHandler):
    def get(self, package):
        versionCode = getCurrentVersionCode(package)
        self.response.out.write(versionCode)

class AndroidInfo(webapp.RequestHandler):
    def get(self, package):
        result = {'versionCode':'0', 'appFileSize':'0'}
        newestApp = getNewestAppVersion(package)
        if(newestApp):
            versionCode = newestApp.versionCode
            appFileSize = newestApp.appFileSize
            result = {'versionCode':str(versionCode), 'appFileSize':str(appFileSize)}
        self.response.out.write(result)
        
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
        for app in AppVersions.all():
            if(app.appFileBlobInfo):
                app.appFileBlobInfo.delete()
            app.delete()
        for app in Apps.all():
            app.delete()
        addApp(u"佛咒", "com.ss.fozhou", 1, "1.0.0")
        addApp(u"佛咒", "com.ss.fozhou", 2, "1.0.1")
        addApp(u"佛咒", "com.ss.fozhou", 3, "1.0.2")
        addApp(u"佛咒", "com.ss.fozhou", 4, "1.1.0")
        addApp(u"个税计算器", "info.kxyk.taxcalc", 1, "1.0.0")
        addApp(u"汇率计算器", "info.kxyk.erc", 1, "1.0.0")
        addApp(u"汇率计算器", "info.kxyk.erc", 2, "1.0.1")
        addApp(u"汇率计算器", "info.kxyk.erc", 3, "1.0.2")
        

   
def showAllApps():
    return Apps.gql(" order by appPackage desc")

def getCurrentVersionCode(appPackage):
    app = AppVersions.gql("where appPackage = :1 order by versionCode desc", appPackage).get()
    if(app):
        return app.versionCode
    else:
        return 0
    

def addApp(appName, appPackage, versionCode, versionName):
    app = Apps.gql("where appName = :1 and appPackage = :2 ", appName, appPackage).get()
    if(not app):
        app = Apps(appName=appName, appPackage=appPackage, appVersionNum=0, appNewestVersionCode=0, appNewestVersionName="0")
        app.put()
    appVersion = AppVersions(parent=app, appName=appName, appPackage=appPackage, versionCode=versionCode, versionName=versionName)
    appVersion.put()
    refreshApps(app, 'add')

def refreshApps(app, actionType):
    currentNewestAppVersion = getNewestAppVersion(app.appPackage)
    if(currentNewestAppVersion):
        app.appNewestVersionCode = currentNewestAppVersion.versionCode
        app.appNewestVersionName = currentNewestAppVersion.versionName
    else:
        app.appNewestVersionCode = 0
        app.appNewestVersionName = "0"
    if(actionType == 'add'):
        app.appVersionNum = app.appVersionNum + 1
    elif(actionType == 'del'):
        app.appVersionNum = app.appVersionNum - 1 
    else:
        None
    app.put()
        
def delApp(appPackage, versionCode):
    app = AppVersions.gql("where appPackage = :1 and versionCode = :2 ", appPackage, versionCode).get()
    deleteApp(app)
        
def deleteApp(app):
    if(app and app.is_saved()):
        if(app.appFileBlobInfo):
                app.appFileBlobInfo.delete()
        parent = app.parent()
        app.delete()
        refreshApps(parent, 'del')
        return True
        
def getAppBlobInfo(appPackage, versionName):
    app = None
    if(versionName == "latest" or versionName == "newest"):
        app = AppVersions.gql("where appPackage = :1 order by versionCode desc", appPackage).get()
    else:    
        app = AppVersions.gql("where appPackage = :1 and versionName = :2 order by versionCode desc", appPackage, versionName).get()
    if(app):
        return app.appFileBlobInfo
    return None

def getNewestAppVersion(appPackage):
    return AppVersions.gql("where appPackage = :1 order by versionCode desc", appPackage).get()
