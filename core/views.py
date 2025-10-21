from django.shortcuts import render
from django.http import HttpResponse
from .utils import geocode_location

def home(request):
    return HttpResponse("Welcome to Vibe Scraper SaaS!")

def test_geocode(request):
    address = request.GET.get('address', 'New York')
    lat, lng = geocode_location(address)
    return HttpResponse(f"Address: {address}<br>Lat: {lat}<br>Lng: {lng}")

# Create your views here.
