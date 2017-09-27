#spark-submit --class AuctionsDataStreaming --master spark://ip-10-0-0-8:7077 --jars target/scala-2.11/spark_auctions-assembly-1.0.jar target/scala-2.11/spark_auctions-assembly-1.0.jar > out.log 2>&1 &

#spark-submit --class AuctionsDataStreaming --master spark://ip-10-0-0-8:7077 --packages com.hortonworks:shc-core:1.1.1-2.1-s_2.11 --repositories http://repo.hortonworks.com/content/groups/public/ --files /usr/local/hbase/conf/hbase-site.xml --jars target/scala-2.11/spark_auctions-assembly-1.0.jar target/scala-2.11/spark_auctions-assembly-1.0.jar > out.log 2>&1 &

spark-submit --class AuctionsDataStreaming --master spark://ip-10-0-0-12:7077 --jars target/scala-2.11/spark_auctions-assembly-1.0.jar target/scala-2.11/spark_auctions-assembly-1.0.jar > out.log 2>&1 &

