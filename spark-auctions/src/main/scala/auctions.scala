import kafka.serializer.StringDecoder
import org.apache.spark.streaming._
import org.apache.spark.streaming.kafka._
import org.apache.spark.SparkConf
import org.apache.spark.rdd.RDD
import org.apache.spark.SparkContext
import org.apache.spark.sql._
import org.apache.spark.rdd.JdbcRDD
import java.sql.{Connection, DriverManager, ResultSet}

object AuctionsDataStreaming {
  def main(args: Array[String]) {

    val brokers = "localhost:9092"
    val topics = "auctions"
    val topicsSet = topics.split(",").toSet

    // Create context with 10 second batch interval
    val sparkConf = new SparkConf().setAppName("auctions_data")
    val ssc = new StreamingContext(sparkConf, Seconds(10))

    // Create direct kafka stream with brokers and topics
    val kafkaParams = Map[String, String]("metadata.broker.list" -> brokers)
    val messages = KafkaUtils.createDirectStream[String, String, StringDecoder, StringDecoder](ssc, kafkaParams, topicsSet)

   //Class.forName("org.postgresql.Driver").newInstance
  
   def connect() = {
    println("Connecting to database..")
    try{
      DriverManager.getConnection("jdbc:postgresql://ec2-34-192-152-48.compute-1.amazonaws.com:5432/auctions","ubuntu", "ubuntu")
    }catch{
      case e: Exception  => {
        println("ERROR: No connection: " + e.getMessage)
        throw e
      }
   }
   }

    // Get the lines and show results
    messages.foreachRDD { rdd =>

        val sqlContext = SQLContextSingleton.getInstance(rdd.sparkContext)
        import sqlContext.implicits._

        val lines = rdd.map(_._2)
        val ticksDF = lines.map( x => {
                                  val tokens = x.split(";")
                                  Tick(tokens(0).toInt, tokens(1), tokens(2).toInt, tokens(3).toInt, tokens(4).toDouble, tokens(5), tokens(6), false)}).toDF()
     
        ticksDF.show()
       

        val db = connect()
        val st = db.createStatement
        //st.executeUpdate("UPDATE AUCTION_ITEMS SET expired=(create_time+(trim(' hours' from auction_type)::integer * interval '1 hour'))<now() WHERE expired=False")

        ticksDF.map( t => "INSERT INTO AUCTION_ITEMS (AUCTION_ID,CREATE_TIME,AUCTIONER_ID,AUCTION_TYPE,STARTING_PRICE,AUCTIONER_NAME,ITEM ) values (" + t.getAs[Int]("auction_id") + ",'" + t.getAs[String]("create_time") + "'," + t.getAs[Int]("auctioner_id") + "," + t.getAs[Int]("auction_type") + "," + t.getAs[Double]("starting_price") + ", '" + t.getAs[String]("auctioner_name") + "', '" + t.getAs[String]("item") + "' );" ).collect().foreach(st.executeUpdate) //println)

    }

    // Start the computation
    ssc.start()
    ssc.awaitTermination()
  }
}

case class Tick(auction_id: Int, create_time: String, auctioner_id: Int, auction_type: Int, starting_price: Double, auctioner_name: String, item: String, expired: Boolean)

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
