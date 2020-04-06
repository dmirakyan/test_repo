from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    response = HttpResponse()
    response.write("Rango says hey there partner! </br>")
    response.write("<a href='/rango/about/'>About</a>")
    # <a href="url">link text</a>
    return response

def about(request):
    response = HttpResponse()
    response.write('Rango says here is the about page. </br>')
    response.write("<a href='/rango/'>Index</a>")
    return response


# Create your views here.
