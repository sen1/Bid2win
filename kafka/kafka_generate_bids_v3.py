import random
import sys
import six
from datetime import datetime
from kafka.client import SimpleClient
from kafka.producer import KeyedProducer
import time
import psycopg2
import struct
import happybase
from pytz import timezone

class BidGenerator(object):
    def __init__(self, addr):
        self.timezone = timezone('EST')
        self.host = 'ec2-34-192-152-48.compute-1.amazonaws.com'
        self.auction_db = 'auctiontable'
        self.bid_db = 'bidtable'
        self.client = SimpleClient(addr)
        self.producer = KeyedProducer(self.client)  
        self.active_auctions = []
        self.conn_auction_db = None
        self.conn_bid_db = None
        self.auction_table = None
        self.bid_table = None
        self.connected_auction_db = False
        self.connected_bid_db = False

    def auction_connect(self):
        print 'Connecting to host', self.host
        try:
            self.conn_auction_db = psycopg2.connect( host=self.host, user='ubuntu', password='ubuntu', dbname='auctions' )
            self.auction_table = self.conn_auction_db.cursor()
            self.connected_auction_db = True
        except psycopg2.Error as e:
            print "Unable to connect host!", self.host
            print e.pgerror
            print e.diag.message_detail
            self.connected_auction_db = False

     
    def bid_connect(self):
        print 'Connecting to host', self.host
        self.conn_bid_db = happybase.Connection(self.host)
        self.bid_table = self.conn_bid_db.table(self.bid_db)
        self.connected_bid_db = True

    def find_active_auctions(self):
        print 'updating auction lists'
        self.active_auctions = []
        if not self.connected_auction_db:
           self.auction_connect()
        try:
           self.auction_table.execute( "SELECT auction_id FROM auction_items where expired=false")
        except psycopg2.Error as e:
           print e.pgerror
           print e.diag.message_detail
           return
        for auction_id in self.auction_table.fetchall():
           self.active_auctions.append(auction_id[0])
        print 'active auctions ', self.active_auctions

    def decode_double(self,data):
        return struct.unpack('>d', data)[0]

    def decode_int(self,data):
        return struct.unpack(">I", data)[0] 

    def decode_bool(self, data):
        return struct.unpack(">?", data)[0]

    def generate_bids(self):
        print 'Generating bids'
        msg_cnt = 1
        if not self.connected_auction_db:
           self.auction_connect()
        self.find_active_auctions()
        nitems = len(self.active_auctions)       
        while nitems>0:  
            if msg_cnt%(2*nitems+1)==0:
               if not self.connected_auction_db:
                  self.auction_connect()
               #Update the auctions list
               self.find_active_auctions()
               nitems = len(self.active_auctions)
    
            #Randomly select an auction id
            auction_id = random.choice(self.active_auctions)
            #print auction_id

            #Lets get auction item info
            self.auction_table.execute( "SELECT expired,starting_price FROM auction_items where auction_id=%i"%auction_id)
            if self.auction_table.rowcount==0:
                continue
            expired, starting_price = self.auction_table.fetchone()
            if expired:
                print 'expired', auction_id
                continue

            #Lets read the bids
            if not self.connected_bid_db:
                self.bid_connect()
            bid_row = self.bid_table.row(struct.pack(">I", auction_id))
            #
            #cell1 = self.bid_table.cells(struct.pack(">I", auction_id), "bid_info:bid_time")
            #cell2 = self.bid_table.cells(struct.pack(">I", auction_id), "bid_info:bid_price")
            #clean_cell2 = map(lambda x:self.decode_double(x), cell2)
            #print auction_id,row
            #if 'bid_info:bid_time' in bid_row: print 'time ', bid_row["bid_info:bid_time"], cell1
            #if 'bid_info:bid_price' in bid_row:print 'price ', self.decode_double(bid_row["bid_info:bid_price"]), clean_cell2
            #print self.decode_starting_price(row)
            #if msg_cnt>40: break
            #   print e.diag.message_detail
            #   time.sleep(5) #sleep 2 secs  
            #   cur = self.connect()
            #   continue
            current_price = -9999
            if 'bid_info:bid_price' in bid_row:
               current_price = self.decode_double(bid_row["bid_info:bid_price"])
            else:
               current_price = starting_price
            #Increase price by 2 cents to $10
            bid_price = current_price + random.uniform(0.02, 10.0)
            bid_price = round(bid_price,2)
            bid_time = datetime.now(self.timezone).strftime("%Y-%m-%d %H:%M:%S")
            bider_id = random.randint(0,100000)
            str_fmt = "{};{};{};{}"
            #print starting_price,expired, current_price, bid_price
            message_info = str_fmt.format(auction_id,
                                          bid_time,
                                          bider_id,
                                          bid_price)
            print message_info
            self.producer.send_messages('auction_bids', str(random.randint(0,4)), message_info)
            msg_cnt += 1
            #time.sleep(1)

    def close_connection(self):
       if self.connected_auction_db:
          self.conn_auction_db.close()    
          self.connected_auction_db = False
       if self.connected_bid_db:
          self.conn_bid_db.close()
          self.connected_bid_db = False

if __name__ == "__main__":
    args = sys.argv
    ip_addr = str(args[1])
    customer_bids = BidGenerator(ip_addr)
    customer_bids.generate_bids()
    customer_bids.close_connection()
