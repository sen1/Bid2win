name := "auction_bids"

version := "1.0"

scalaVersion := "2.11.8"
val hadoopVersion = "2.7.4"
val hbaseVersion = "1.2.6"

libraryDependencies ++= Seq(
"mysql" % "mysql-connector-java" % "5.1.29",
"postgresql" % "postgresql" % "9.1-901.jdbc4",
"org.apache.spark" %% "spark-core" % "2.1.1" % "provided",
"org.apache.spark" %% "spark-sql" % "2.1.1" % "provided",
"org.apache.spark" %% "spark-streaming" % "2.1.1" % "provided",
"org.apache.spark" %% "spark-streaming-kafka-0-8" % "2.1.1",
"org.apache.hadoop" %  "hadoop-client"   % hadoopVersion % "provided",
"org.apache.hbase"  %  "hbase-common"    % hbaseVersion,
"org.apache.hbase"  %  "hbase-server"    % hbaseVersion,
"org.apache.hbase"  %  "hbase-protocol"  % hbaseVersion,
"org.apache.hbase"  %  "hbase-client"    % hbaseVersion,
"eu.unicredit" %% "hbase-rdd" % "0.8.0",
"com.hortonworks" % "shc-core" % "1.1.1-2.1-s_2.11"
)

mergeStrategy in assembly := {
  case m if m.toLowerCase.endsWith("manifest.mf")          => MergeStrategy.discard
  case m if m.toLowerCase.matches("meta-inf.*\\.sf$")      => MergeStrategy.discard
  case "log4j.properties"                                  => MergeStrategy.discard
  case m if m.toLowerCase.startsWith("meta-inf/services/") => MergeStrategy.filterDistinctLines
  case "reference.conf"                                    => MergeStrategy.concat
  case _                                                   => MergeStrategy.first
}
