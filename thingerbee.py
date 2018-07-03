#!/usr/bin/env python

# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START imports]
import os
import urllib

from google.appengine.api import app_identity
from google.appengine.api import users

from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from google.appengine.ext.webapp import blobstore_handlers

import lib.cloudstorage as gcs
import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]




class ThingerBee(webapp2.RequestHandler):
  def get(self):

    template = JINJA_ENVIRONMENT.get_template('index.html')
    upload_url = blobstore.create_upload_url('/upload')
    template_values = {
      'debug': 'basic',
      'upload_url': upload_url,
    }

    for b in blobstore.BlobInfo.all():
        self.response.out.write('<li><a href="/serve/%s' % str(b.key()) + '">' + str(b.filename) + '</a>')

    self.response.write("<img src='http://localhost:8080/serve/S-q5kGZ4j-2XCzDfVHT63A=='>")

    self.response.write(template.render(template_values))

  def post(self):
    bucket_name = app_identity.get_default_gcs_bucket_name()
    filename = "/{}/foo".format(bucket_name)

    upload_files = self.get_uploads('file')
    blob_info = upload_files[0]

    template_values = {
      'debug': blob_info,
    }

    template = JINJA_ENVIRONMENT.get_template('index.html')
    self.response.write(template.render(template_values))
# [END main_page]

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')
        blob_info = upload_files[0]
        self.redirect('/')

class Admin(webapp2.RequestHandler):
  def get(self):
    self.response.write("Admintimes")

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, blob_key):
        blob_key = str(urllib.unquote(blob_key))
        if not blobstore.get(blob_key):
            self.error(404)
        else:
            self.send_blob(blobstore.BlobInfo.get(blob_key), save_as=True)      

# [START app]
app = webapp2.WSGIApplication([
  ('/', ThingerBee),
  ('/upload', UploadHandler),
  ('/_admin', Admin),
  ('/serve/([^/]+)?', ServeHandler),
], debug=True)
# [END app]
