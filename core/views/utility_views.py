from django.shortcuts import render
from django.http import HttpResponse
from ..utils import geocode_location


def home(request):
    return render(request, 'home.html')


def test_geocode(request):
    address = request.GET.get('address', 'New York')
    lat, lng = geocode_location(address)
    return HttpResponse(f"Address: {address}<br>Lat: {lat}<br>Lng: {lng}")