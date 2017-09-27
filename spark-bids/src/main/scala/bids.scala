import kafka.serializer.StringDecoder
import org.apache.spark.streaming._
import org.apache.spark.streaming.kafka._
import org.apache.spark.SparkConf
import org.apache.spark.rdd.RDD
import org.apache.spark.SparkContext
import org.apache.spark.sql._
import org.apache.spark.rdd.JdbcRDD
import java.sql.{Connection, DriverManager, ResultSet}
import unicredit.spark.hbase._
import org.apache.spark.sql.functions._
import org.apache.hadoop.hbase.client.Put
import org.apache.hadoop.hbase.client._
import org.apache.hadoop.hbase.util.Bytes
import org.apache.hadoop.fs.Path
import org.apache.hadoop.hbase.{CellUtil, HBaseConfiguration, TableName}
import org.apache.hadoop.conf.Configuration
import org.apache.hadoop.hbase.io.ImmutableBytesWritable
import org.apache.spark.sql.execution.datasources.hbase._
import org.apache.spark.sql.functions.{row_number, max, broadcast}
import org.apache.spark.sql.expressions.Window
import org.apache.spark.sql.functions.udf

object BidDataStreaming {
  def main(args: Array[String]) {

    val brokers = "ec2-34-235-37-82.compute-1.amazonaws.com:9092"
    val topics = "auction_bids"
    val topicsSet = topics.split(",").toSet

    // Create context with 2 second batch interval
    val sparkConf = new SparkConf().setAppName("auction_bids")
    val ssc = new StreamingContext(sparkConf, Seconds(10))

    // Create direct kafka stream with brokers and topics
    val kafkaParams = Map[String, String]("metadata.broker.list" -> brokers)
    val messages = KafkaUtils.createDirectStream[String, String, StringDecoder, StringDecoder](ssc, kafkaParams, topicsSet)


    implicit val config = HBaseConfig()
    val conf : Configuration = HBaseConfiguration.create()
    val connection = ConnectionFactory.createConnection(conf)
    val table = connection.getTable(TableName.valueOf( Bytes.toBytes("bidtable") ) )

    def find_old_price(bid:Int):Double = { 
    	  val get = new Get(Bytes.toBytes(bid)); 
    	  var result = table.get(get); 
    	  var value = result.getValue(Bytes.toBytes("bid_info"), Bytes.toBytes("bid_price"));  
	  if (value==null) return 0
    	  return Bytes.toDouble(value) 
     }
   
    def schema = s"""{
       |"table":{"namespace":"default", "name":"bidtable", "versions":5},
       |"rowkey":"key",
       |"columns":{
         |"bid_item":{"cf":"rowkey", "col":"key", "type":"int"},
         |"bid_time":{"cf":"bid_info", "col":"bid_time", "type":"string"},
         |"bider_id":{"cf":"bid_info", "col":"bider_id", "type":"int"},
         |"bid_price":{"cf":"bid_info","col":"bid_price", "type":"double"}
       |}
     |}""".stripMargin


    // Get the lines and show results
    messages.foreachRDD { rdd =>

        val sqlContext = SQLContextSingleton.getInstance(rdd.sparkContext)
        import sqlContext.implicits._
        val lines = rdd.map(_._2)
        val ticksDF = lines.map( x => {
                                  val tokens = x.split(";")
                                  Tick(tokens(0).toInt, tokens(1), tokens(2).toInt, tokens(3).toDouble)} ).toDF()

        //Get old prices of the items
        val old_prices = ticksDF.collect().map( t => (t.getAs[Int]("bid_item"),find_old_price(t.getAs[Int]("bid_item")) )).toList.toDF("bid_item","latest_price")
        old_prices.show()

        //Validate the bids
        val joined_df = ticksDF.as("d1").join(old_prices.as("d2"), $"d1.bid_item"===$"d2.bid_item" && $"d1.bid_price">$"d2.latest_price", "inner").select($"d1.*")
        joined_df.show()

        //Only register the highest bidder
        val sortedDF = Window.partitionBy($"bid_item").orderBy($"bid_price".desc)
        val dfTop = joined_df.withColumn("rn", row_number.over(sortedDF)).where($"rn" === 1).drop("rn")
        dfTop.show()

        //Write to HBase
        dfTop.write.options(Map(HBaseTableCatalog.tableCatalog -> schema, HBaseTableCatalog.newTable -> "4")).format("org.apache.spark.sql.execution.datasources.hbase").save()

    }

    // Start the computation
    ssc.start()
    ssc.awaitTermination()
  }
}

case class Tick(bid_item: Int, bid_time: String, bider_id: Int, bid_price: Double )

/** Lazily instantiated singleton instance of SQLContext */
object SQLContextSingleton {

  @transient  private var instance: SQLContext = _

  def getInstance(sparkContext: SparkContext): SQLContext = {
    if (instance == null) {
      instance = new SQLContext(sparkContext)
    }
    instance
  }
}
