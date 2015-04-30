import os
import jinja2
import urllib
import webapp2
import logging
import re
import json
import datetime

from uuid import uuid4
from google.appengine.api import images, files
from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext import blobstore


jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

'#Function used for outputting formatted time to main page'
def convert_timedelta(duration):
    days, seconds = duration.days, duration.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    if hours > 0:
        if hours == 1:
            return str(hours) + " Hour ago"
        else:
            return str(hours) + " Hours ago"
    else:
        if minutes == 1:
            return str(minutes) + " Minute ago"
        else:
            return str(minutes) + " Minutes ago"


"#User model new user created each time a new user logs in via google"
"#User Id is treated as the primary key, in the sense that it is used to link the user to other models"


class User(ndb.Model):
    userid = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    index = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    description = ndb.StringProperty()
    joined = ndb.DateTimeProperty(auto_now_add=True, indexed=False)
    "#Convers the data inside of the model to a json string. Method is used for outputting json."
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


"#Photo model relates to a photo entity or a photo uploaded by the user."
"#blob_key relates to a blob stored within the blobstore"
"#the photo id is used as a primary key in order to link photos with other entities."


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
               ' "photoid": "%s",' \
               ' "uploaded": "%s"}' % (self.blob_key,
                                       username,
                                       self.userid,
                                       self.description,
                                       self.photoid,
                                       self.uploaded.strftime("%d/%m/%Y"))

"#Comments take the photoid and userid as foreign keys"


class Comment(ndb.Model):
    photoid = ndb.KeyProperty(kind=Photo, required=True)
    userid = ndb.KeyProperty(kind=User, required=True)
    content = ndb.StringProperty(required=True)
    timestamp = ndb.DateTimeProperty(auto_now_add=True)

"#servers the index page as default page"
"#redirects a user to google loggin if not logged in"
"#queries the user table in order to dertmine whether a user exists"
"#If no user exists creates a new user"


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

"#Sends a copy of the users details as a json string to be stored in local storage."
"#This is used when navigating the website whilst offline"


class CurrentHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user().user_id()
        callback = self.request.get("callback")
        self.request.headers["Content-Type"] = 'application/json'
        current = User.query(User.userid == user)
        sresponse = ""
        jsonop = None
        for user in current:
            sresponse += user.tojson()

            if callback is '':
                jsonop = sresponse

            else:
                jsonop = callback+"("+sresponse+")"

        self.response.write(jsonop)

"#provides all of the content contained within the timeline page"






class StreamHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers["Content-Type"] = 'application/json'
        "#queires the image table to obtain images."
        pictures = Photo.query().order(-Photo.uploaded).fetch()
        imglist = []
        for picture in pictures:
            "#uses the image userid in order to get the users name"
            name = picture.userid.get().name
            sresponse = {
                'src': str(picture.blob_key),
                'username': name,
                'description': picture.description,
                'uploaded': picture.uploaded.strftime("%H:%M %d/%B/%Y"),
                'comments': [],
            }
            "#also queries for related comments"
            comments = Comment.query(picture.key == Comment.photoid).order(Comment.timestamp)
            results = comments.fetch()
            for comment in results:
                if comment.timestamp.date() == datetime.datetime.now().date():
                    timestamp = datetime.datetime.now() - comment.timestamp
                    output = convert_timedelta(timestamp)
                else:
                    output = comment.timestamp.strftime("%d/%B")
                commenter = comment.userid.get().name
                c = {
                    'username': commenter,
                    'content': comment.content,
                    'timestamp': output,
                }
                "#dictionary is then pushed into a list which is then converted to json"
                sresponse['comments'].append(c)
            imglist.append(sresponse)

        self.response.write(json.dumps(imglist))

"#facilatates user uploads"




class UploadHandler(webapp2.RequestHandler):
    def post(self):
        logging.getLogger().setLevel(logging.DEBUG)
        currentuser = users.get_current_user()
        if currentuser:
            try:
                uploader = ndb.Key(User, users.get_current_user().user_id()).get()
                "#parses json string sent from client"
                data = json.loads(self.request.body)
                "#base64 string retrieved from json"
                upload_files = data['blob']
                print(upload_files)
                "#base64 string parsed to remove unwanted data"
                data_to_64 = re.search(r'base64,(.*)', upload_files).group(1)
                "#base64 decoded"
                decoded = data_to_64.decode('base64')

                "#creates a blobstore space for a jpg image"
                saved = files.blobstore.create(mime_type='image/jpg')
                "#writes the images to the blobstore space"
                with files.open(saved, 'a') as f:
                    f.write(decoded)
                "#finally saves the decoded image into the blobstore"
                files.finalize(saved)
                "#retrieves blob key from the newly saved image"
                key = files.blobstore.get_blob_key(saved)
                description = data['description']
                "#parses hashtags unimplemented feature"
                tags = re.findall(r"#(\w+)", description)
                "#creates a new photo entity"
                photo = Photo(userid=uploader.key, photoid=str(key), blob_key=key, description=description, tags=tags)
                "#sets key of entity"
                photo.key = ndb.Key(Photo, photo.photoid)
                "#entity is stored in datastore"
                photo.put()
            except Exception, e:
                print e
                return 404
        else:
            return "user logged out"

"#Serves images from blobstore using images API"


class ServeHandler(webapp2.RequestHandler):
    def get(self, resource):

        resource = str(urllib.unquote(resource))
        '#Server side image manipulation using google images api and pil library for python.'
        '#Fetch Blob from blobstore'
        img = images.Image(blob_key=resource)

        '#Resize to required size'
        img.resize(width=500, height=500)

        '#Google+ enhancement filter'
        img.im_feeling_lucky()

        '#Execture transformations on selected blob'
        image = img.execute_transforms(output_encoding=images.JPEG)

        '#Set HTTP Content Type'
        self.response.headers['Content-Type'] = "image/jpeg"
        self.response.headers.add_header("Expires", "%s" % str(datetime.datetime.now().date() + datetime.timedelta(days=30)))
        self.response.headers.add_header("Cache-Control", "public, max-age=315360000")
        '#Respond with image'
        self.response.out.write(image)

"#Serves images from blobstore using images API"


class ThumbHandler(webapp2.RequestHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))

        '#Server side image manipulation using google images api and pil library for python.'
        '#Fetch Blob from blobstore'
        img = images.Image(blob_key=resource)

        '#Resize to required size'
        img.resize(width=200, height=200)

        '#Google+ enhancement filter'
        img.im_feeling_lucky()

        '#Execture transformations on selected blob'
        thumbnail = img.execute_transforms(output_encoding=images.JPEG)

        '#Set HTTP Content Type'
        self.response.headers['Content-Type'] = "image/jpeg"
        self.response.headers.add_header("Expires", "%d" % datetime.datetime.now().date() + datetime.timedelta(days=30))
        self.response.headers.add_header("Cache-Control", "public, max-age=315360000")

        '#Respond with image'
        self.response.out.write(thumbnail)

"#Finds and outputs user details as json"


class UserHandler(webapp2.RequestHandler):
    def get(self, resource):
        callback = self.request.get("callback")
        resource = str(urllib.unquote(resource))
        jsonop = None
        sresponse = ""
        userid = ""
        username = ""
        if resource is '':
            jsonop = '{"error":"User is Query is Blank"}'
        else:
            "#queries users table to find user"
            qry = User.query(User.index == resource.lower())
            results = qry.fetch()
            if len(results) < 1:
                jsonop = '{"error":"User ' + resource + ' Not Found"}'
            else:
                "#outputs the users details"
                for user in results:
                    sresponse = user.tojson()[:-1] + ', "images":['
                    userid = user.key
                    username = user.name
                "#fetches all related pictures to the user"
                pictures = Photo.query(Photo.userid == userid).order(-Photo.uploaded).fetch()
                for picture in pictures:
                    sresponse += picture.tojson(username) + ','
                    if callback is '':
                        jsonop = sresponse[:-1] + "]}"
                    else:
                        jsonop = callback+"([" + sresponse[:-1] + "]}])"
        "#outputs json"
        self.response.write(jsonop)

"#used for updating user records"


class UpdateHandler(webapp2.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        name = data["username"]
        min_len = 4
        max_len = 15
        pattern = r"^(?i)[a-z0-9_-]{%s,%s}$" % (min_len, max_len)
        user = users.get_current_user().user_id()
        currentuser = User.get_by_id(user)
        description = data["description"]
        "#seraches for the desired user name to avoid duplicates"
        checkavail = User.query(User.index == name.lower()).fetch()
        if checkavail:
            print "Taken"
            "#If user name is taken but the description has content save the description content"
            if len(description) > 0:
                currentuser.description = description
                currentuser.put()
        else:
            "#regular expression to ensure that the username entered is valid"
            if re.match(pattern, name):
                "#replaces name and index with selected name"
                currentuser.name = name
                "#index is used as a way of querying without worrying about case."
                currentuser.index = name.lower()
            else:
                print "invalid characters"

            "#changes description"
            currentuser.description = description
            "#saves changes to user"
            currentuser.put()

"#used to parse json comments"


class CommentHandler(webapp2.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        "#gets photo id"
        photo = data['photoid']
        photoid = ndb.Key(Photo, photo)
        "#gets comment content"
        content = data['comment']
        "#gets the current user"
        user = users.get_current_user().user_id()
        "#ensures that a comment has been entered"
        if len(content) < 1:
            print "no comment"
        else:
            "#creates a new comment entity"
            userid = ndb.Key(User, user)
            comment = Comment(photoid=photoid, content=content, userid=userid)
            comment.put()


app = webapp2.WSGIApplication([
    ('/', HomeHandler),
    ('/currentuser', CurrentHandler),
    ('/user/(.*)', UserHandler),
    ('/stream', StreamHandler),
    ('/upload', UploadHandler),
    ('/comment', CommentHandler),
    ('/serve/(.*)', ServeHandler),
    ('/thumb/(.*)', ThumbHandler),
    ('/update', UpdateHandler),
    ], debug=True)
