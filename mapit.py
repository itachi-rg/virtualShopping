import os
import urllib
import cgi
import jinja2
import webapp2
import logging
import time
import random

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import mail

import storage

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

	
class MainPage(webapp2.RequestHandler):
	def get(self):
			user = users.get_current_user();
			usershops = [];
			usershoplist = [];
			eachshop = [];
			
			if user:
				url = users.create_logout_url(self.request.uri);
				url_linktext = 'Logout';
				usershops = storage.Shop.query(storage.Shop.userid==user.user_id()).fetch();
				i=0;
				for shops in usershops:
					shopdet = storage.ShopDetails.query(storage.ShopDetails.shop==shops.key).fetch();
					usershoplist.append([shops,shopdet[0]]);
					i=i+1;
				
			else:
				url = users.create_login_url(self.request.uri)
				url_linktext = 'Login'
				
			shoplist = storage.Shop.query().fetch();
			i=0;
			for shops in shoplist:
					shopdet = storage.ShopDetails.query(storage.ShopDetails.shop==shops.key).fetch();
					eachshop.append([shops,shopdet[0]]);
					i=i+1;
			
			template_values = {
				'shoplist': shoplist,
				'shopdetails':eachshop,
				'usershops':usershoplist,
				'user':user,
				'url': url,
				'url_linktext': url_linktext,
			}	
			template = JINJA_ENVIRONMENT.get_template('main.html')
			self.response.write(template.render(template_values))


class CoverPage(webapp2.RequestHandler):
	def get(self):
			user = users.get_current_user();
			usershops = []
			shoplist = storage.Shop.query().fetch();
			total = len(shoplist);
			
			if (total > 0) :
				index = random.randrange(0,total);
			else:
				index = 0;
			shop = shoplist[index];
			shopkey = shop.key;
			
			
			itemlist = storage.Item.query(storage.Item.itemshop==shopkey).fetch();
			itempositionlist = storage.ItemPosition.query(storage.ItemPosition.shop==shopkey).fetch();
			itemlocationlist = [];
			
			
			for itempos in itempositionlist:
				itemlocationlist.append(storage.ItemLocation.query(storage.ItemLocation.lat == itempos.lati,storage.ItemLocation.lng == itempos.longi).fetch());
				
			shopinfo = storage.ShopDetails.query(storage.ShopDetails.shop==shopkey).fetch();
			curren = shopinfo[0].currency;
			
			if user:
				url = users.create_logout_url(self.request.uri);
				url_linktext = 'Logout';
				usershops = storage.Shop.query(storage.Shop.userid==user.user_id()).fetch();
			else:
				url = users.create_login_url(self.request.uri)
				url_linktext = 'Login'
				
			
			template_values = {
				'itemlist' : itemlist,
				'itempositionlist' : itempositionlist,
				'itemlocationlist' : itemlocationlist,
				'shopkey' : shopkey.urlsafe(),
				'shop' : shop,
				'shopinfo' : shopinfo,
				'currency' : curren,
				'shoplist': shoplist,
				'usershops':usershops,
				'user':user,
				'url': url,
				'url_linktext': url_linktext
			}	
			template = JINJA_ENVIRONMENT.get_template('cover.html')
			self.response.write(template.render(template_values))
			
			
			
class VirtualShop(webapp2.RequestHandler):
	def get(self):
			shopkey = ndb.Key(urlsafe=self.request.get('shopkey'));
			shop = shopkey.get();
			
			itemlist = storage.Item.query(storage.Item.itemshop==shopkey).fetch();
			itempositionlist = storage.ItemPosition.query(storage.ItemPosition.shop==shopkey).fetch();
			itemlocationlist = [];
			
			
			for itempos in itempositionlist:
				itemlocationlist.append(storage.ItemLocation.query(storage.ItemLocation.lat == itempos.lati,storage.ItemLocation.lng == itempos.longi).fetch());
				
			shopinfo = storage.ShopDetails.query(storage.ShopDetails.shop==shopkey).fetch();
			curr = shopinfo[0].currency;
			
			#for i in itemlist :
				#logging.warning(i.item)
				#logging.warning(i.price)
				
			for i in itempositionlist :
				logging.warning(i.lati)
				logging.warning(i.longi)
				
				
			logging.warning(len(itemlocationlist))
			
			
			template_values = {
				'itemlist' : itemlist,
				'itempositionlist' : itempositionlist,
				'itemlocationlist' : itemlocationlist,
				'shopkey' : shopkey.urlsafe(),
				'shop' : shop,
				'shopinfo' : shopinfo,
				'currency' : curr
			}	
			template = JINJA_ENVIRONMENT.get_template('virtualshop.html')
			self.response.write(template.render(template_values))


			
class AddItem(webapp2.RequestHandler):
		def post(self):
			logging.warning("In addItem")
			
			itemname = self.request.get('name');
			itemprice = float(self.request.get('price'));
			lati = float(self.request.get('lati'));
			longi = float(self.request.get('longi'));
			heading = float(self.request.get('head'));
			pitchy = float(self.request.get('pitch'));
			zoomlevel = float(self.request.get('zoom'));
			shopkey = ndb.Key(urlsafe=self.request.get('shopkey'));
			
			logging.debug(itemname)
			logging.info(itemprice)
			logging.warning(lati)
			logging.warning(longi)
			logging.warning(heading)
			logging.critical(shopkey)
			
			queri = storage.Item.query(storage.Item.item == itemname,storage.Item.price == itemprice);
			existingitem  = queri.fetch(1);
			
			locqueri = storage.ItemPosition.query(storage.ItemPosition.lati == lati,storage.ItemPosition.longi == longi);
			existingloc  = locqueri.fetch(1);
			
			if not existingitem:
				logging.debug('not existing item')
				additem = storage.Item();
				additem.item = itemname;
				additem.price = itemprice;
				additem.itemshop = shopkey;
				additem.put();
			else :
				additem = existingitem[0];

			if not existingloc:
				addloc = storage.ItemPosition();
				addloc.lati = lati;
				addloc.longi = longi;
				addloc.shop = shopkey;
				addloc.put();
			else:
				addloc = existingloc[0];
			
			itemlocation = storage.ItemLocation();
			itemlocation.lat = lati;
			itemlocation.lng = longi;
			itemlocation.head = heading;
			itemlocation.pitch = pitchy;
			itemlocation.zoom = zoomlevel;
			itemlocation.item = additem.key;
			itemlocation.itemloc = addloc.key;
			itemlocation.put();
			
			
			time.sleep(0.3);
			self.redirect('/createvirtualshop?shopkey='+shopkey.urlsafe());
			
class RemoveItem(webapp2.RequestHandler):
		def post(self):
			itemname = self.request.get('citemname');
			itemprice = float(self.request.get('citemprice'));
			shopkey = ndb.Key(urlsafe=self.request.get('cshopkey'));
			
			citem = storage.Item.query(storage.Item.item == itemname,storage.Item.price == itemprice).fetch(1);
			currentitem = citem[0];
			
			itemloc = storage.ItemLocation.query(storage.ItemLocation.item == currentitem.key).fetch(1);
			itemlocation = itemloc[0];
			
			existingpos = itemlocation.itemloc;

			locas = storage.ItemLocation.query(storage.ItemLocation.lat == itemlocation.lat,storage.ItemLocation.lng == itemlocation.lng).fetch();
			numlocas = len(locas);
			
			currentitem.key.delete();
			itemlocation.key.delete();
			
			if(numlocas == 1):
				existingpos.delete();
			
			time.sleep(0.3);
			self.redirect('/createvirtualshop?shopkey='+shopkey.urlsafe());
				
class DeleteShop(webapp2.RequestHandler):
	def get(self):
			 
			user = users.get_current_user();
			shopkey = ndb.Key(urlsafe=self.request.get('shopkey'));
			shop = shopkey.get();
			
			if(user):
				userid = user.user_id();
			else:
				userid = '';
			
			if (shop.userid == userid ):	
				itemlist = storage.Item.query(storage.Item.itemshop==shopkey).fetch(keys_only=True);
				itempositionlist = storage.ItemPosition.query(storage.ItemPosition.shop==shopkey).fetch();
				itemlocationlist = [];
			
			
				for itempos in itempositionlist:
					itemloc = storage.ItemLocation.query(storage.ItemLocation.lat == itempos.lati,storage.ItemLocation.lng == itempos.longi).fetch(keys_only=True);
					ndb.delete_multi(itemloc)
				
				itempositionkeylist = storage.ItemPosition.query(storage.ItemPosition.shop==shopkey).fetch(keys_only=True);
				
				shopinfo = storage.ShopDetails.query(storage.ShopDetails.shop==shopkey).fetch(keys_only=True);
				ndb.delete_multi(shopinfo);
				ndb.delete_multi(itempositionkeylist);
				ndb.delete_multi(itemlist);
				shopkey.delete();
				
				self.redirect('/mainpage');
				
			else :
				self.error(500);
				self.response.write("<h1 align='center'>You don't have permission to delete</h1>");
				return
			
			

class SelectShop(webapp2.RequestHandler):
	def get(self):
			user = users.get_current_user();
			shoplist = storage.Shop.query().fetch();
				
			if user:	
				template_values = {
					'shoplist': shoplist,
					'useremail': user.email()
				
				}	
				template = JINJA_ENVIRONMENT.get_template('selectshop.html')
				self.response.write(template.render(template_values))
			
			else :
				self.error(500);
				self.response.write("<h1 align='center'>Please log on to create your own shop</h1>");
				return
			
class AddNewShop(webapp2.RequestHandler):
	def post(self):
			
			name = self.request.get('shopname');
			res = storage.Shop.query(storage.Shop.shopname==name).fetch();
			
			if(len(res)>0):
				self.error(500);
				self.response.write("<h1 align='center'>shopname already exists !! give a different shopname</h1>");
				return
			
			email = self.request.get('shopemail');
			stype = self.request.get('shoptype');
			saddr = self.request.get('shopaddress');
			sdesc = self.request.get('shopdesc');
			curren = self.request.get('curr');
			scheck = self.request.get('ownercb');
			user = users.get_current_user();
			userid = user.user_id();
			lati = float(self.request.get('lat'));
			longi = float(self.request.get('lng'));
			heading = float(self.request.get('head'));
			pitchy = float(self.request.get('pitch'));
			zoomlevel = float(self.request.get('zoom'));
			panid = self.request.get('panid');
			
			shoplocation = storage.Shop();
			shoplocation.userid = userid;
			shoplocation.shopname = name;
			shoplocation.panid = panid;
			shoplocation.lat = lati;
			shoplocation.lng = longi;
			shoplocation.head = heading;
			shoplocation.pitch = pitchy;
			shoplocation.zoom = zoomlevel;
			shoplocation.put();
			
			shopdetails = storage.ShopDetails();
			shopdetails.shop = shoplocation.key;
			shopdetails.shopemail = email;
			shopdetails.shoptype = stype;
			shopdetails.shopaddr = saddr;
			shopdetails.shopdesc = sdesc;
			shopdetails.currency = curren;
			shopdetails.ownercb = scheck;
			shopdetails.put();

			
			time.sleep(0.3);
			self.redirect('/mainpage');
			
			
class CreateVirtualShop(webapp2.RequestHandler):
	def get(self):
			
			user = users.get_current_user();
			shopkey = ndb.Key(urlsafe=self.request.get('shopkey'));
			shop = shopkey.get();
			
			if(user):
				userid = user.user_id();
			else:
				userid = '';
				
			if (shop.userid == userid ):
				shopkey = ndb.Key(urlsafe=self.request.get('shopkey'));
				shop = shopkey.get();
			
				itemlist = storage.Item.query(storage.Item.itemshop==shopkey).fetch();
				itempositionlist = storage.ItemPosition.query(storage.ItemPosition.shop==shopkey).fetch();
				itemlocationlist = [];
			
			
				for itempos in itempositionlist:
					itemlocationlist.append(storage.ItemLocation.query(storage.ItemLocation.lat == itempos.lati,storage.ItemLocation.lng == itempos.longi).fetch());
				
				shopinfo = storage.ShopDetails.query(storage.ShopDetails.shop==shopkey).fetch();
				curr = shopinfo[0].currency;
				template_values = {
					'itemlist' : itemlist,
					'itempositionlist' : itempositionlist,
					'itemlocationlist' : itemlocationlist,
					'shopkey' : shopkey.urlsafe(),
					'shop' : shop,
					'shopinfo': shopinfo,
					'currency':curr
				}	
			
			
				template = JINJA_ENVIRONMENT.get_template('createvirtualshop.html')
				self.response.write(template.render(template_values))
			
			else :
				self.error(500);
				self.response.write("<h1 align='center'>Please log on to create your own shop</h1>");
				return
				
				
class CheckOut(webapp2.RequestHandler):
	def get(self):
	
			shopkey = ndb.Key(urlsafe=self.request.get('shopkey'));
			shop = shopkey.get();
			
			
			shopinfo = storage.ShopDetails.query(storage.ShopDetails.shop==shopkey).fetch();
			template_values = {
				'shopkey' : shopkey.urlsafe(),
				'shop' : shop,
				'shopinfo': shopinfo
			}	
			
			
			template = JINJA_ENVIRONMENT.get_template('checkout.html')
			self.response.write(template.render(template_values))

class Contact(webapp2.RequestHandler):
	def get(self):
			template_values = {
			}	
			
			
			template = JINJA_ENVIRONMENT.get_template('contact.html')
			self.response.write(template.render(template_values))			

class SendMail(webapp2.RequestHandler):
	def post(self):
	
			shopkey = ndb.Key(urlsafe=self.request.get('shopkey'));
			shop = shopkey.get();
			
			emailadd = self.request.get('email');
				
			shopinfo = storage.ShopDetails.query(storage.ShopDetails.shop==shopkey).fetch();
			owneremail = shopinfo[0].shopemail;
			
			if not mail.is_email_valid(emailadd):
				self.error(500);
				self.response.write("<h1 align='center'>invalid email address</h1>");
				return

			else:
				name = self.request.get('name');
				address = self.request.get('address');
				city = self.request.get('city');
				state = self.request.get('state');
				phnumber = self.request.get('phnumber');
				order = self.request.get('order');
				
				
				sender_address = "g.rohan.gowda@gmail.com"
				user_address = emailadd;
				subject = "Shopping Order"
				body = """
							Customer Details:
							
							Name : %s ,
							Address : %s ,
							City : %s ,
							State : %s ,
							Contact Number : %s ,
							
							Order : %s
						""" % (name,address,city,state,phnumber,order)
					
				mail.send_mail(sender_address, user_address, subject, body)
				self.redirect('/mainpage');
			
			
application = webapp2.WSGIApplication([
    ('/', CoverPage),
	('/mainpage', MainPage),
	('/virtualshop', VirtualShop),
	('/selectshop',SelectShop),
	('/addnewshop', AddNewShop),
	('/createvirtualshop', CreateVirtualShop),
	('/additem', AddItem),
	('/removeitem', RemoveItem),
	('/deleteshop', DeleteShop),
	('/checkout', CheckOut),
	('/sendmail', SendMail),
	('/contactus', Contact)
], debug=True)
