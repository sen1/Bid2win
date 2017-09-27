#spark-submit --class BidDataStreaming --master spark://ip-10-0-0-4:7077 --jars target/scala-2.11/auction_bids-assembly-1.0.jar target/scala-2.11/auction_bids-assembly-1.0.jar > out.txt 2>&1 &

#spark-shell --master spark://ip-10-0-0-4:7077 --packages com.hortonworks:shc-core:1.1.1-2.1-s_2.11 --repositories http://repo.hortonworks.com/content/groups/public/ --files /usr/local/hbase/conf/hbase-site.xml --jars target/scala-2.11/auction_bids-assembly-1.0.jar target/scala-2.11/auction_bids-assembly-1.0.jar


spark-submit --class BidDataStreaming --master spark://ip-10-0-0-4:7077 --packages com.hortonworks:shc-core:1.1.1-2.1-s_2.11 --repositories http://repo.hortonworks.com/content/groups/public/ --files /usr/local/hbase/conf/hbase-site.xml --jars target/scala-2.11/auction_bids-assembly-1.0.jar target/scala-2.11/auction_bids-assembly-1.0.jar > out.txt 2>&1 &

#spark-submit --class BidDataStreaming --master spark://ip-10-0-0-4:7077 --packages com.hortonworks:shc-core:1.1.1-2.1-s_2.11 --repositories http://repo.hortonworks.com/content/groups/public/ --files /home/ubuntu/spark-bids/hbase-site.xml --jars target/scala-2.11/auction_bids-assembly-1.0.jar target/scala-2.11/auction_bids-assembly-1.0.jar
