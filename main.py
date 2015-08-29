import invitation
import webapp2
import jinja2
import json
import urllib2
import os
from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext import deferred
from google.appengine.api import mail
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app

class UserPhoto(ndb.Model):
  blob_key = ndb.BlobKeyProperty()

class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user is None:
          login_url = users.create_login_url(self.request.path)
          self.redirect(login_url)
          return
        upload_url = blobstore.create_upload_url('/sending')
        template_vars = {'upload_url': upload_url}
        template = jinja2_environment.get_template('templates/enter.html')
        self.response.write(template.render(template_vars))

class SendingEmailHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload = self.get_uploads()[0]
        photo = UserPhoto(blob_key=upload.key())
        photo.put()
        blob_reader = blobstore.BlobReader(upload.key())
        blob_info = blobstore.BlobInfo.get(upload.key())
        value = blob_reader.read()
        user = users.get_current_user()
        to_addr = self.request.get('email')
        to_addr2 = self.request.get('email2')
        if not mail.is_email_valid(to_addr):
            return 'error can\'t send message'
            pass
        message = mail.EmailMessage()
        message.sender = user.email()
        message.to = to_addr
        message.body = self.request.get('message')
        email_delay_string = self.request.get('email_delay')
        attachments=[(blob_info.filename, value)]
        email_delay = int(email_delay_string)
        #getting the gif
        selection_name = self.request.get('user_selection')
        url = "http://api.giphy.com/v1/gifs/random?api_key=dc6zaTOxFJmzC&tag=" + selection_name
        string = urllib2.urlopen(url)
        bigdicitonary = json.loads(string.read())
        selection_url = bigdicitonary['data']['image_url']
        word = {'selection_url': selection_url, 'selection_name': selection_name}
        #sending the email
        deferred.defer(invitation.send_invitation, message.sender, message.to, message.body, attachments, _countdown = email_delay)
        deferred.defer(invitation.send_invitation, message.sender, to_addr2 , message.body, attachments, _countdown = email_delay )
        #getting the gif
        page = jinja2_environment.get_template('templates/gif.html')
        self.response.write(page.render(word))


jinja2_environment = jinja2.Environment(loader=
    jinja2.FileSystemLoader(os.path.dirname(__file__)))


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/sending', SendingEmailHandler)
], debug=True)
