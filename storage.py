import cgi
import urllib
from google.appengine.ext import ndb

class Shop(ndb.Model):
	userid = ndb.StringProperty()
	shopname = ndb.StringProperty()
	panid = ndb.StringProperty()
	lat = ndb.FloatProperty()
	lng = ndb.FloatProperty()
	head = ndb.FloatProperty()
	pitch = ndb.FloatProperty()
	zoom = ndb.FloatProperty()
	
class ShopDetails(ndb.Model):
	shop = ndb.KeyProperty(kind=Shop,required=True)
	shopemail = ndb.StringProperty()
	shoptype = ndb.StringProperty()
	shopaddr = ndb.StringProperty()
	shopdesc = ndb.StringProperty()
	currency = ndb.StringProperty()
	ownercb = ndb.StringProperty()
	
	
class Item(ndb.Model):
	item = ndb.StringProperty()
	price = ndb.FloatProperty()
	itemshop = ndb.KeyProperty(kind=Shop,required=True)
	
class ItemPosition(ndb.Model):
	lati = ndb.FloatProperty();
	longi = ndb.FloatProperty();
	shop = ndb.KeyProperty(kind=Shop,required=True)
	
class ItemLocation(ndb.Model):
	lat = ndb.FloatProperty()
	lng = ndb.FloatProperty()
	head = ndb.FloatProperty()
	pitch = ndb.FloatProperty()
	zoom = ndb.FloatProperty()
	item = ndb.KeyProperty(kind=Item,required=True)
	itemloc = ndb.KeyProperty(kind=ItemPosition,required=True)
	

	
	
	

