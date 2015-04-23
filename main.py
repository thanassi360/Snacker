import os
import jinja2
import urllib
import webapp2
import base64, re


from uuid import uuid4
from google.appengine.api import images, files
from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers




jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class User(ndb.Model):
    userid = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    index = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    description = ndb.StringProperty()
    joined = ndb.DateTimeProperty(auto_now_add=True, indexed=False)

    def tojson(self):
        return '{"user": "%s",' \
               '"name": "%s", ' \
               '"email": "%s", ' \
               '"description": "%s", ' \
               '"joindate": "%s"}' % (self.userid,
                                      self.name,
                                      self.email,
                                      self.description,
                                      self.joined.strftime("%d/%m/%Y"))


class Photo(ndb.Model):
    blob_key = ndb.BlobKeyProperty()
    photoid = ndb.StringProperty(required=True)
    userid = ndb.KeyProperty(kind=User, required=True)
    tags = ndb.StringProperty(repeated=True)
    description = ndb.StringProperty()
    uploaded = ndb.DateTimeProperty(auto_now_add=True)

    def tojson(self, username):
        return '{"src": "%s",' \
               '"username": "%s",' \
               ' "user_id": "%s",' \
               ' "description": "%s",' \
               ' "photoid": "%s"' \
               ' "uploaded": "%s"}' % (self.blob_key,
                                       username,
                                       self.userid,
                                       self.description,
                                       self.photoid,
                                       self.uploaded.strftime("%d/%m/%Y"))



class Comment(ndb.Model):
    photoid = ndb.KeyProperty(kind=Photo, required=True)
    userid = ndb.KeyProperty(kind=User, required=True)
    content = ndb.StringProperty(required=True)
    timestamp = ndb.DateTimeProperty(auto_now_add=True)

    def tojson(self, username):
        return '{"username" : "%s",' \
               ' "content" : "%s",' \
               '"timestamp" : "%s"' % (username,
                                       self.content,
                                       self.timestamp.strftime("%d/%m/%Y"))


class HomeHandler(webapp2.RequestHandler):
    def get(self):
        currentuser = users.get_current_user()
        if currentuser:
            find = User.query(User.userid == currentuser.user_id()).fetch()
            if find:
                print("User Exists!")
            else:
                guid = str(uuid4())
                user = User(userid=currentuser.user_id(),
                            email=currentuser.email(),
                            name=guid,
                            index=guid.lower())
                user.key = ndb.Key(User, currentuser.user_id())
                user.put()
            template = jinja_environment.get_template('index.html')
            self.response.write(template.render())

        else:
            self.redirect(users.create_login_url('/'))


class CurrentHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user().user_id()
        callback = self.request.get("callback")
        self.request.headers["Content-Type"] = 'application/json'
        current = User.query(User.userid == user)
        sresponse = ""
        json = None
        for user in current:
            sresponse += user.tojson()

            if callback is '':
                json = sresponse

            else:
                json = callback+"("+sresponse+")"

        self.response.write(json)


class StreamHandler(webapp2.RequestHandler):
    def get(self):
        callback = self.request.get("callback")
        self.response.headers["Content-Type"] = 'application/json'
        pictures = Photo.query().order(-Photo.uploaded).fetch()
        sresponse = ""
        json = None
        for picture in pictures:
            username = picture.userid.get().name
            sresponse += picture.tojson(username)[:-1] + ', "comments" : ['
            comments = Comment.query(picture.key == Comment.photoid).fetch()
            for comment in comments:
                commenter = comment.userid.get().name
                sresponse += comment.tojson(commenter) + '},'[:-1]

            sresponse += ']},'
            if callback is '':
                json = "[" + sresponse[:-1] + "]"
            else:
                json = callback+"([" + sresponse[:-1] + "])"

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
        self.response.headers["Access-Control-Allow-Origin"] = "*"

        currentuser = users.get_current_user()
        if currentuser:
            uploader = ndb.Key(User, users.get_current_user().user_id()).get()

            upload_files = self.request.get("blob")
            data_to_64 = re.search(r'base64,(.*)', upload_files).group(1)
            decoded = data_to_64.decode('base64')


            saved = files.blobstore.create(mime_type='image/png')
            with files.open(saved, 'a') as f:
                f.write(decoded)
            files.finalize(saved)

            key = files.blobstore.get_blob_key(saved)

            description = self.request.get("description")

            photo = Photo(userid=uploader.key,photoid = str(key),blob_key= key, description=description)
            photo.key = ndb.Key(Photo, str(key))
            photo.put()
        else:
            return "user logged out"


class ServeHandler(webapp2.RequestHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))

        '#Server side image manipulation using google images api and pil library for python.'
        '#Fetch Blob from blobstore'
        img = images.Image(blob_key=resource)

        '#Resize to required size'
        img.resize(width=500, height=500)

        '#Google+ enhancment filter'
        img.im_feeling_lucky()

        '#Execture transformations on selected blob'
        image = img.execute_transforms(output_encoding=images.JPEG)

        '#Set HTTP Content Type'
        self.response.headers['Content-Type'] = "image/jpeg"

        '#Respond with image'
        self.response.out.write(image)


class ThumbHandler(webapp2.RequestHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))

        '#Server side image manipulation using google images api and pil library for python.'
        '#Fetch Blob from blobstore'
        img = images.Image(blob_key=resource)

        '#Resize to required size'
        img.resize(width=200, height=200)

        '#Google+ enhancment filter'
        img.im_feeling_lucky()

        '#Execture transformations on selected blob'
        thumbnail = img.execute_transforms(output_encoding=images.JPEG)

        '#Set HTTP Content Type'
        self.response.headers['Content-Type'] = "image/jpeg"

        '#Respond with image'
        self.response.out.write(thumbnail)


class UserHandler(webapp2.RequestHandler):
    def get(self, resource):
        callback = self.request.get("callback")
        resource = str(urllib.unquote(resource))
        json = None
        sresponse = ""
        userid = ""
        username = ""
        if resource is '':
            json = '{"error":"User is Query is Blank"}'

        else:
            qry = User.query(User.index == resource.lower())
            results = qry.fetch()
            if len(results) < 1:
                json = '{"error":"User ' + resource + ' Not Found"}'
            else:
                for user in results:
                    sresponse = user.tojson()[:-1] + ', "images":['
                    userid = user.key
                    username = user.name

                pictures = Photo.query(Photo.userid == userid).fetch()
                for picture in pictures:
                    sresponse += picture.tojson(username) + ','
                    if callback is '':
                        json = sresponse[:-1] + "]}"
                    else:
                        json = callback+"([" + sresponse[:-1] + "]}])"

        self.response.write(json)

    def post(self):
        name = self.request.get("name")
        user = users.get_current_user()
        currentuser = User.query(User.userid == user.user_id()).fetch()
        checkavail = User.query(User.index == name.lower()).fetch()
        if checkavail is '':
            currentuser[0].name = name
            currentuser[0].index = name.lower()
        else:
            self.response.write("Name Taken!")

class SearchHandler(webapp2.RequestHandler):
    def get(self, url):
        search = self.request.get("search")
        self.response.write(search)


class CommentHandler(webapp2.RequestHandler):
    def post(self):
        photoid = ndb.Key(urlsafe=self.request.get("photoid"))
        content = self.request.get("comment")
        user = urllib.unquote(self.request.get("user"))
        userid = ndb.Key(User, user)
        comment = Comment(photoid=photoid, content=content, userid=userid)
        comment.put()


app = webapp2.WSGIApplication([
    ('/', HomeHandler),
    ('/currentuser', CurrentHandler),
    ('/user/(.*)', UserHandler),
    ('/stream', StreamHandler),
    ('/upload', UploadHandler),
    ('/url', UrlHandler),
    ('/comment', CommentHandler),
    ('/search(.*)', SearchHandler),
    ('/serve/(.*)', ServeHandler),
    ('/thumb/(.*)', ThumbHandler),
    ], debug=True)
