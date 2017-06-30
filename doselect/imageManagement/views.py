from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from PIL import Image
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os.path
from django.utils.crypto import get_random_string
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import json
import datetime
import urllib
from django.views.decorators.csrf import csrf_exempt


import jwt

permissions = {AllowAny, }


class Index(APIView):
    template_name = 'simple_upload.html'

    def get(self, request):
        return render(request, self.template_name)

    """
    function used for post endpoint which uploads the image 
    takes the image to be uploaded in the post data  
    first it checks the token which is sent in the header 
    if it is correct then it gets the image from the post data and extracts its extension
    if the extension is not that of an image then it returns an error
    if the extension is correct it open the FileSystemStorage and appends the access token 
    with the image name and saves the image 
    if it does then it deletes the image 
    else it throws the suitable error 
    """


    def post(self, request):
        error=''
        jwtToken = request.META['HTTP_AUTHORIZATION']
        try:
            payload = jwt.decode(jwtToken, 'bhandari', True)
            if not request.FILES.get('image_file') and not request.POST.get('image_url'):
                return HttpResponse(json.dumps({"image_url": '', "error": "Send either imahge or url"}))
            if request.FILES.get('image_file'):
                image_file = request.FILES['image_file']
                extension = os.path.splitext(image_file.name)[1]
                if not (extension == '.jpg' or extension == '.png' or extension == '.gif' or extension == '.jpeg' or extension == '.bmp'):
                    return HttpResponse(json.dumps({"image_url":'',"error":'Unsupportable type'}))
                fs = FileSystemStorage()
                filename = fs.save(jwtToken + "_"+str(datetime.datetime.now())+"_"+image_file.name, image_file)
                uploaded_file = fs.url(filename)
            if request.POST.get('image_url'):
                image_url = request.POST.get('image_url')
                image_name = image_url.rsplit('/', 1)[1]
                extension = os.path.splitext(image_name)[1]
                if not (extension == '.jpg' or extension == '.png' or extension == '.gif' or extension == '.jpeg' or extension == '.bmp'):
                    return HttpResponse(json.dumps({"image_url":'',"error":"not an image file"}))
                image_path = settings.MEDIA_ROOT + '/'
                uploaded_file_url = jwtToken + "_"+str(datetime.datetime.now())+"_"+image_name
                urllib.urlretrieve(image_url, image_path + uploaded_file_url )
                uploaded_file_url="/media/"+uploaded_file_url

        except jwt.ExpiredSignature:
            error = "Signature Expired"
        except jwt.DecodeError:
            error = "Decoding Error"
        except jwt.InvalidTokenError:
            error = "Invalid Token"
        except urllib.error.URLError:
            error = "Image not found at the given URL"



        return HttpResponse(json.dumps({"image": uploaded_file,"image_url" : uploaded_file_url,"error":error}))

"""
function used for get endpoint for both single image and all the images 
takes the image_name in the arguments if it is not given then it will return
all the images linked to the given access token 
first it checks the token which is sent in the header 
if it is correct then it checks whether the image with image_name and linked to the access token exits 
if it does then it returns the image url
if image_name is null this implies that getImages/ endpoint was used 
so it returns all the images 
else it throws the suitable error 
"""
def get_images(request, image_name=""):

    jwtToken = request.META['HTTP_AUTHORIZATION']
    images = []
    image = ""
    error = "False"
    try:
        payload = jwt.decode(jwtToken, 'bhandari', True)
        if image_name:
            fs = FileSystemStorage()
            if fs.exists(jwtToken + image_name):
                image = fs.url(jwtToken + image_name)
            else:
                image = "image not found"
        else:
            fs = FileSystemStorage()
            files = fs.listdir('')
            if not files:
                error="NO images to get"
            for f in files:
                for img in f:
                    if jwtToken in img:
                        images.append("/media/" + img)
    except jwt.DecodeError:
        error = "Decoding Error"
    except jwt.ExpiredSignature:
        error = "Signature Expired"
    except jwt.InvalidTokenError:
        error = "Invalid Token"
    return HttpResponse(json.dumps({"image": image, "images": images, "error": error}))

"""
function used for delete endpoint 
takes the image to be deleted in the url 
first it checks the token which is sent in the header 
if it is correct then it checks whether the image with image_name exits 
if it does then it deletes the image 
else it throws the suitable error 
"""
def delete(request, image_name):
    error = "False"
    msg = "Image Deleted"
    jwtToken = request.META['HTTP_AUTHORIZATION']
    try:
        payload = jwt.decode(jwtToken, 'bhandari', True)
        fs = FileSystemStorage()
        if fs.exists(jwtToken + image_name):
            fs.delete(jwtToken + image_name)
        else:
            error = "Image Not Found"
    except jwt.ExpiredSignature:
        error = "Signature Expired"
    except jwt.DecodeError:
        error = "Decoding Error"
    except jwt.InvalidTokenError:
        error = "Invalid Token"
    return HttpResponse(json.dumps({"msg": msg, "error": error}))

"""
function used for patch endpoint 
takes the image to be updated in the url and the image file in the post data
first it checks the token which is sent in the header 
if it is correct then it checks whether the image with image_name exits 
if it does then it deletes the image 
and replaces it with the new image that is sent in the post data
else it throws the suitable error
"""
@csrf_exempt
def patch(request, image_name):
    error = "False"
    uploaded_file_url = ""
    jwtToken = request.META['HTTP_AUTHORIZATION']
    try:
        payload = jwt.decode(jwtToken, 'bhandari', True)
        if request.method == 'POST' and request.FILES['image_file']:
            fs = FileSystemStorage()
            if fs.exists(jwtToken + image_name):
                fs.delete(jwtToken + image_name)
                image_file = request.FILES['image_file']
                extension = os.path.splitext(image_file.name)[1]
                if not (
                                    extension == '.jpg' or extension == '.png' or extension == '.gif' or extension == '.jpeg' or extension == '.bmp'):
                    error = "not an image file"
                fs = FileSystemStorage()
                filename = fs.save(jwtToken + image_file.name, image_file)
                uploaded_file_url = fs.url(filename)
                return HttpResponse(json.dumps({"image_url": uploaded_file_url, "error": error}))
            else:
                error = "Image Not Found"
                return HttpResponse(json.dumps({"image_url": uploaded_file_url, "error": error}))
    except jwt.ExpiredSignature:
        error = "Signature Expired"
    except jwt.DecodeError:
        error = "Decoding Error"
    except jwt.InvalidTokenError:
        error = "Invalid Token"

    return HttpResponse(json.dumps({"image_url": uploaded_file_url, "error": error}))

"""
 function used to generate the access token
 randomly generates a string of length 5 which is used to generate the token
 bhandari is the secret key
 the generated token has to be attached in the header with every request
"""
def generate_token(request):
    data = {
        'username': get_random_string(length=5)
    }

    payload = jwt.encode(data, 'bhandari', 'HS256')

    return HttpResponse(json.dumps({"payload": payload}))
