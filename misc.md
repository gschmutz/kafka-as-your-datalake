# Kafka as your Data Lake - is it feasible?


## Demo 3 - Drill


## Demo 4 - Hive

```
docker exec -ti hive-metastore hive
```

```
CREATE EXTERNAL TABLE truck_position
  (`timestamp` bigint , `eventType` string,  `latitude` double, 
  longitude double)
  ROW FORMAT SERDE 
  'org.apache.hadoop.hive.kafka.KafkaSerDe'
  STORED BY 'org.apache.hadoop.hive.kafka.KafkaStorageHandler'
  TBLPROPERTIES
  ("kafka.topic" = "truck_position", 
  "kafka.bootstrap.servers"="kafka-1:19092",
  "oracle.kafka.table.key.type"="string"
  );
```

does not work (tried to use in Presto):

```
CREATE EXTERNAL TABLE truck_position
  (`timestamp` bigint , `eventType` string,  `latitude` double, 
  longitude double)
  ROW FORMAT SERDE 
  'org.apache.hadoop.hive.kafka.KafkaSerDe'
  STORED AS INPUTFORMAT 'org.apache.hadoop.hive.kafka.KafkaInputFormat'
       OUTPUTFORMAT 'org.apache.hadoop.hive.kafka.KafkaOutputFormat'
  TBLPROPERTIES
  ("kafka.topic" = "truck_position", 
  "kafka.bootstrap.servers"="kafka-1:19092",
  "oracle.kafka.table.key.type"="string"
  );
```


Next let's query the data from Presto. Connect to the Presto CLI using

```
presto --server localhost:28081 --catalog kafka-hive --schema default
```

## Twitter Example

### Create Twitter Source

```
docker exec -ti kafka-1 kafka-topics --create --zookeeper zookeeper-1:2181 --topic tweet-raw-v1 --replication-factor 3 --partitions 8
```


User Ids to follow: 82564066,18898576,9462812,126226388,2342011352,1287555762,2827342884,24692013, 24692013, 1562518867, 1185290384634601472, 880123724694822913,925124076666007558,2496849162, 1086342103876161536, 904997437,3315687506

Robin Moffatt: 82564066
Guido Schmutz: 18898576
Jay Kreps: 126226388
Apache Kafka: 1287555762
Gunnar Morling: 2342011352
Gwen Shapira: 9462812
Kai Waehner: 207673942
Tim Berglund: 14211984
Ricardo Ferreira: 1287555762
Confluent Inc: 2827342884
Victor Gamov: 24692013
Databricks: 1562518867
ksqlDB: 1185290384634601472
Kafka Streams: 880123724694822913
Starbrustdata: 925124076666007558
Prestodb: 2496849162
Prestosql: 1086342103876161536
Apache Drill: 904997437
Dremio: 3315687506


```
connector.class=com.github.jcustenborder.kafka.connect.twitter.TwitterSourceConnector
process.deletes=false
### filter.keywords=#kafka,#ksqldb,#ksql,#eventsorucing,#streamprocessing,#datalake,#datahub,#streamanalytics
filter.userids=82564066,18898576,9462812,126226388,2342011352,1287555762,2827342884,24692013, 24692013, 1562518867, 1185290384634601472, 880123724694822913,925124076666007558,2496849162, 1086342103876161536, 904997437,3315687506 
kafka.status.topic=tweet-raw-v1
tasks.max=1
twitter.oauth.consumerKey=2cUwkAhSQnFMGFU0pB2OcNQZV
twitter.oauth.consumerSecret=wi1DmS07hQfPvJH0eU7kC8oOOzUN8RLuRLVLpxNaZpPBfehXSY
twitter.oauth.accessToken=18898576-nym8SGZkCMQmoZJxJuNyfk87JBi5tfmN8D7ZVKQhb
twitter.oauth.accessTokenSecret=18898576-nym8SGZkCMQmoZJxJuNyfk87JBi5tfmN8D7ZVKQhb


# do not use transform currently
transforms.createKey.type=org.apache.kafka.connect.transforms.ValueToKey
transforms=createKey,extractInt
transforms.extractInt.type=org.apache.kafka.connect.transforms.ExtractField$Key
transforms.extractInt.field=Id
transforms.createKey.fields=Id
```
