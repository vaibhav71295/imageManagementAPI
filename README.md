Dependencies:

-Python 2.7.x

Change INSTALLED_APPS

INSTALLED_APPS = [
    ...
    'rest_framework',
    'rest_framework_jwt',
]

&

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}

Virtual Environment Setup:


-Setup tribe virtualenv : "virtualenv -p python doselect-env"

-Move to virtualenv and activate its environment

Dependency Setup:

-Install requirements: "pip install -r requirements.txt".

Running Project

-Change directory to doselect

-Run command :"python manage.py runserver port"

-In the browser open "http://127.0.0.1:(your port)/imageManagement/post/"

-Use Postman to test

- First generate a token by hitting "http://127.0.0.1:(your port)/imageManagement/generateToken/"

- Copy the returned payload and use it in the header as Authorization : paste the payload


Frontend :

-simple_upload.html

in all the ajax requests port has been hard coded as 8060
change it accordingly
Authorization header is also hard coded generate a token and then paste it in the html

API Information :

- "http://127.0.0.1:(your port)/imageManagement/generateToken/"

uses JWT to generate an access token
generates an access token using a rondom string of length 5 with SECRET KEY = 'bhandari'
save this token and send in the header of every other request

- "http://127.0.0.1:(your port)/imageManagement/post/"

Headers needed -
Authorization : access token
Body -
either one of the header or both
image_file = image that has to be uploaded on the server
image_url = image url that has to be uploaded on the server

will append access token and time stamp to the image name
access token is appended to keep track which access token has which image
timestamp is appended if an image of same name is uploaded again , already existing image will not be deleted
will compress and  save the image in the media folder
if sent without the Body and Header will render an html page from where all the APIs can be tested

- "http://127.0.0.1:(your port)/imageManagement/getImage/<image_name>"

Headers needed -
Authorization : access token

will return the image with given image name and linked to the access token provided in the header
if multiple images with same name but different timestamp will return them all

- "http://127.0.0.1:(your port)/imageManagement/getImages/"

Headers needed -
Authorization : access token

will return all the images linked to the access token provided in the header
if multiple images with same name but different timestamp will return them all

- "http://127.0.0.1:(your port)/imageManagement/delete/<image_name>"

Headers needed -
Authorization : access token

will delete the image with given image name and linked to the access token provided in the header
if multiple images with same name but different timestamp will delete them all
and returns a message 'deleted'

- "http://127.0.0.1:(your port)/imageManagement/patch/<image_name_delete>"

Headers needed -
Authorization : access token
Body -
image_file = image that has to be uploaded on the server

will delete the image with given image_name_delete and linked to the access token provided in the header
if multiple images with same name but different timestamp will delete them all
then
will compress and save the image to provided in the body to the media folder