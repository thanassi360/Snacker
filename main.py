import os
import jinja2
import urllib
import webapp2
import cgi

from uuid import uuid4
from google.appengine.api import images
from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers


class User(ndb.Model):
    userid = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    index = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    description = ndb.StringProperty()
    joined = ndb.DateTimeProperty(auto_now_add=True, indexed=False)

    def tojson(self):
        return '{"user": "%s","name": "%s", "description": "%s", "timestamp": "%s"}' % (self.userid, self.name,
                                                                                        self.description, self.joined.strftime("%H:%M"))


class Photo(ndb.Model):
    blob_key = ndb.BlobKeyProperty()
    user = ndb.StringProperty(required=True)
    username = ndb.StringProperty()
    tags = ndb.StringProperty(repeated=True)
    description = ndb.StringProperty()
    uploaded = ndb.DateTimeProperty(auto_now_add=True)

    def tojson(self):
        return '{"src": "%s","username": "%s", "user_id": "%s", "description": "%s", "uploaded": "%s"}' % (self.blob_key, self.username, self.user,
                                                                                                           self.description,self.uploaded.strftime("%H:%M"))

class Follower(ndb.Model):
    user = ndb.StringProperty()
    follower = ndb.StringProperty()


class Likes(ndb.Model):
    photo_key = ndb.StringProperty()
    user = ndb.StringProperty()


class HomeHandler(webapp2.RequestHandler):
    def get(self):
        currentuser = users.get_current_user()
        if currentuser:
            find = User.get_by_id(currentuser.user_id())
            if find:
                print("User Exists")
            else:
                guid = str(uuid4())
                user = User(userid=currentuser.user_id(),
                            email=currentuser.email(),
                            name=guid,
                            index=guid.lower())
                user.key = ndb.Key(User, currentuser.user_id())
                user.put()
        else:
            self.redirect(users.create_login_url('/'))


class StreamHandler(webapp2.RequestHandler):
    def get(self):
        callback = self.request.get("callback")
        self.response.headers["Content-Type"] = 'application/json'
        images = Photo.query().fetch()
        strResponse = ""
        json = ""
        for image in images:
            strResponse += image.tojson() + ','
            if callback=='':
                json = "[" + strResponse[:-1] + "]"
            else:
                json = callback+"([" + strResponse[:-1] + "])"


        self.response.write(json)


class UrlHandler(webapp2.RequestHandler):
    def get(self):
        callback = self.request.get("callback")
        url = blobstore.create_upload_url("/upload")
        self.response.headers["Content-Type"] = 'application/json'
        if callback == '':
            upload = "[{'url': '%s'}]" % str(url)
        else:
            upload = callback+"([{'url': '%s'}])" % str(url)
        self.response.out.write(upload)


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        currentuser = users.get_current_user()
        upload_files = self.get_uploads("blob")
        description = self.request.get("description")
        blob = upload_files[0]
        photo = Photo(user=currentuser.user_id(), blob_key=blob.key(), description=description)
        photo.put()


class ServeHandler(webapp2.RequestHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        img = images.Image(blob_key=resource)
        img.resize(width=500, height=500)
        img.im_feeling_lucky()
        image = img.execute_transforms(output_encoding=images.JPEG)
        self.response.headers['Content-Type'] = "image/jpeg"
        self.response.out.write(image)


class ThumbHandler(webapp2.RequestHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        img = images.Image(blob_key=resource)
        img.resize(width=200, height=200)
        img.im_feeling_lucky()
        thumbnail = img.execute_transforms(output_encoding=images.JPEG)
        self.response.headers['Content-Type'] = "image/jpeg"
        self.response.out.write(thumbnail)


app = webapp2.WSGIApplication([
    ('/login', HomeHandler),
    ('/stream', StreamHandler),
    ('/upload', UploadHandler),
    ('/url', UrlHandler),
    ('/serve/(.*)', ServeHandler),
    ('/thumb/(.*)', ThumbHandler),
    ], debug=True)

"""
class UserHandler(webapp2.RequestHandler):
    def get(self, resource):
        currentuser = users.get_current_user()
        upload_url = blobstore.create_upload_url('/upload')
        resource = str(urllib.unquote(resource))
        qry = User.query(User.index == resource.lower())
        results = qry.fetch()
        strResponse = ""
        for user in results:
            strResponse += user.toJSON()
        self.response.write(strResponse)
"""

"""
    def post(self, resource):
        currentuser = users.get_current_user().user_id()
        name = cgi.escape(self.request.get('name'))
        qry = User.query(User.index == name.lower())
        results = qry.fetch()
        if results:
            self.response.write("TAKEN")

        else:
            user = User.get_by_id(currentuser)
            user.name = name
            user.index = name.lower()
            user.put()
            self.redirect('/%s' % name)


class CaptureHandler(webapp2.RequestHandler):
    def get(self):
        currentuser = users.get_current_user()
        username = User().getcurrentuser()
        upload_url = blobstore.create_upload_url('/upload')

        if currentuser:
            greeting = "<a href='%s'>Log out</a>" % users.create_logout_url('/')

        else:
            greeting = "<a href='%s'>Log In </a>" % users.create_login_url('/')

        template_values = {
            "upload_url": upload_url,
            "check": currentuser,
            "username": username,
            "log": greeting,
        }

        if currentuser:
            template = jinja_environment.get_template('templates/capture.html')
            self.response.write(template.render(template_values))
        else:
            self.redirect(users.create_login_url('/'))
"""
"""
class ImageHandler(webapp2.RequestHandler):
    def get(self):
        pass
class IDHandler(ndb.Model):
    def get(self, user):
        user_id = User.query(User.email == user)
        for id in user_id:
            self.response.write(id.toJSON())

"""

