from functools import wraps
from threading import Thread

from geopy.geocoders import Nominatim
from django.contrib.gis.geoip2 import GeoIP2
from django.contrib.gis.geoip2 import GeoIP2Exception

from django.conf import settings
from .models import Address
from .models import Visit


def AxisToAddress(latitude, longitude):
    geolocator = Nominatim()
    locstring = "{0}, {1}".format(latitude, longitude)
    print(locstring)
    location = geolocator.reverse(locstring)
    return location.address


def GeoIPtoDB(f):

    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def geoip2db(request):
        try:
            g = GeoIP2(path=settings.BASE_DIR)
            ip = get_client_ip(request)
            # ip = "202.37.242.54"
            city_info = g.city(ip)
            address = AxisToAddress(city_info['latitude'],
                                    city_info['longitude'])

            ipaddr, _ = Address.objects.update_or_create(ip=ip,
                                            defaults = {
                                                "city": city_info['city'],
                                                "address": address
                                            })

            visit = Visit.objects.create(ip=ipaddr,
                                         path=request.get_full_path(),
                                         UA=request.META['HTTP_USER_AGENT'])
            visit.save()

        except GeoIP2Exception as e:
            print(e)

    @wraps(f)
    def req(request, *args, **kwargs):
        Thread(target=geoip2db, args=(request,)).start()
        return f(request, *args, **kwargs)

    return req
