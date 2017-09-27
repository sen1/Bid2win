from app import app
from flask import Flask,flash,redirect,render_template,request,session
from flask import jsonify
import psycopg2
import pprint
import json
import struct
import happybase

@app.route('/')

def index():
   return render_template('index.html')


@app.route('/all_auctions', methods = ['GET','POST'])
def all_auctions():
     records = get_all_auctions()
     print json.dumps(records, indent=2)
     return render_template('home.html', data=records)

@app.route('/google', methods = ['GET','POST'])
def google():
   return render_template('google.html')

@app.route('/query', methods = ['GET','POST'])
def query():
   return render_template('query.html')

@app.route('/auction_item', methods = ['GET','POST'])
def auction_item():
     db = connect_db()
     select_auction = request.form.get('auction_id')
     print 'auction_id selected ', (str(select_auction))
     db.execute("SELECT * FROM auction_items where auction_id=%i"%int(select_auction))
     if db.rowcount==0:
        return 'No such auction_id exists'
     val = db.fetchone()
     #return str(vals)
     conn = happybase.Connection('ec2-34-192-152-48.compute-1.amazonaws.com')
     table = conn.table('bidtable')
     bid_row = table.row(struct.pack(">I", val[0]))
     #print val, bid_row
     winning_price = -9999
     if 'bid_info:bid_price' in bid_row:
        winning_price = struct.unpack('>d',bid_row["bid_info:bid_price"])[0]
     else:
        winning_price = val[4]
     winner = -9999
     if 'bid_info:bider_id' in bid_row:
        winner = struct.unpack('>I',bid_row["bid_info:bider_id"])[0]
     last_bid_time = "N/A"
     if 'bid_info:bid_time' in bid_row:
        last_bid_time = bid_row["bid_info:bid_time"]
     val = val + (winning_price,winner,last_bid_time)
     print val
     #print winning_price, winner, last_bid_time
     data = [{"auction_id":val[0], "auctioner_id":val[2], "item":val[6], "create_time":str(val[1]), "starting_price":val[4], "auctioner_name":val[5],"winning_price":val[8], "winner":val[9], "latest_bid_time":str(val[10]), "expired":int(val[7])}]
     print json.dumps(data, indent=2)
     bid_times = table.cells(struct.pack(">I", val[0]), "bid_info:bid_time")
     print bid_times
     bid_prices = table.cells(struct.pack(">I", val[0]), "bid_info:bid_price")
     clean_bid_prices = map(lambda x:struct.unpack('>d',x)[0], bid_prices)
     print clean_bid_prices
     data2 = {"bid_time":bid_times, "bid_prices":clean_bid_prices}
     return render_template('item.html', data=data, data2=data2)

def get_all_auctions():
     db = connect_db()
     db.execute("SELECT * FROM auction_items limit 200")
     records = db.fetchall()
     response_list = []
     conn = happybase.Connection('ec2-34-192-152-48.compute-1.amazonaws.com')
     table = conn.table('bidtable')
     for val in records:
        bid_row = table.row(struct.pack(">I", val[0]))
        #print val, bid_row
	winning_price = -9999
        if 'bid_info:bid_price' in bid_row:
            winning_price = struct.unpack('>d',bid_row["bid_info:bid_price"])[0]
        else:
            winning_price = val[4]
	winner = -9999
	if 'bid_info:bider_id' in bid_row:
	    winner = struct.unpack('>I',bid_row["bid_info:bider_id"])[0]
	last_bid_time = "N/A"
        if 'bid_info:bid_time' in bid_row:
	    last_bid_time = bid_row["bid_info:bid_time"]
        val = val + (winning_price,winner,last_bid_time)
        print val
	#print winning_price, winner, last_bid_time
	response_list.append(val)  
     json_data = [{"auction_id":x[0], "auctioner_id":x[2], "item":x[6], "create_time":str(x[1]), "starting_price":x[4], "auctioner_name":x[5],"winning_price":x[8], "winner":x[9], "latest_bid_time":str(x[10]), "expired":int(x[7])} for x in response_list]
     return json_data


def connect_db():
   print 'Connecting to database'
   try:
      conn = psycopg2.connect( host='ec2-34-192-152-48.compute-1.amazonaws.com', user='ubuntu', password='ubuntu', dbname='auctions')
      return conn.cursor()
   except:
      print "Not Connected"
