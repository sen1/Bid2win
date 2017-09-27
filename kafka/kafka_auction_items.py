import random
import sys
import six
import time
from datetime import datetime
from kafka.client import SimpleClient
from kafka.producer import KeyedProducer
from pytz import timezone

#load item lists
inputfile = open('products.txt','r')
inputlines = inputfile.readlines()
item_lists = [item.strip() for item in inputlines]

class Producer(object):

    def __init__(self, addr):
        self.client = SimpleClient(addr)
        self.producer = KeyedProducer(self.client)
        self.timezone = timezone('EST')

    def name_generator(self):
        return ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWZ') for i in range(random.randint(3,9)))

    def item_generator(self):
       global item_lists
       return random.choice(item_lists)

    def produce_msgs(self):
        msg_cnt = 0
        auction_id=0
        while True:
            auction_id += 1
            #Create time EST time
            create_time = datetime.now(self.timezone).strftime("%Y-%m-%d %H:%M:%S")
            #Auctioner ID
            auctioner_id = random.randint(0,100000)  
            #Expiry: 2 hours to 4 days
            auction_type = random.randint(2,96) 
            #Starting price: 1 cent to $100 
            starting_price = random.uniform(0.01, 100.0)
            #Auctioner name generator
            auctioner_name = self.name_generator()
            #Item generator
            item = self.item_generator()

            str_fmt = "{};{};{};{};{};{};{}"
            message_info = str_fmt.format(auction_id,
                                          create_time,
                                          auctioner_id,
                                          auction_type,
                                          round(starting_price,2),
                                          auctioner_name,
                                          item)
            print message_info
            self.producer.send_messages('auctions', str(random.randint(0,4)), message_info)
            msg_cnt += 1
            #time.sleep(1)

if __name__ == "__main__":
    args = sys.argv
    ip_addr = str(args[1])
    #print item_lists
    prod = Producer(ip_addr)
    prod.produce_msgs()
