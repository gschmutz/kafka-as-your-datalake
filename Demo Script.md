# Demo for "Kafka as your Data Lake - is it feasible?"

## Preparation

### Setup platform using Docker Compose

```
# Install Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable edge"
apt-get install -y docker-ce
sudo usermod -aG docker ubuntu

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/1.26.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

# Prepare Environment Variables
export PUBLIC_IP=$(curl ipinfo.io/ip)
export DOCKER_HOST_IP=$(ip addr show eth0 | grep "inet\b" | awk '{print $2}' | cut -d/ -f1)

# needed for elasticsearch
sudo sysctl -w vm.max_map_count=262144   

# Get the project
cd /home/ubuntu 
git clone https://github.com/gschmutz/kafka-as-your-datalake-demo.git
chown -R ubuntu:ubuntu kafka-as-your-datalake-demo
cd kafka-as-your-datalake-demo/platys

# Startup Environment
sudo -E docker-compose up -d
```

Click **Connect using SSH** to open the console and enter the following command to watch the log file of the init script.

```
tail -f /var/log/cloud-init-output.log --lines 1000
```

### Create Kafka Topics

Using the `kafka-topics` CLI inside the `kafka-1` docker image create the different Kafka topics:

```
docker exec -it kafka-1 kafka-topics --zookeeper zookeeper-1:2181 --create --topic truck_position --partitions 8 --replication-factor 3
docker exec -it kafka-1 kafka-topics --zookeeper zookeeper-1:2181 --create --topic dangerous_driving_ksql --partitions 8 --replication-factor 3
docker exec -it kafka-1 kafka-topics --zookeeper zookeeper-1:2181 --create --topic dangerous_driving_and_driver_ksql --partitions 8 --replication-factor 3
docker exec -it kafka-1 kafka-topics --zookeeper zookeeper-1:2181 --create --topic truck_driver --partitions 8 --replication-factor 3 --config cleanup.policy=compact --config segment.ms=100 --config delete.retention.ms=100 --config min.cleanable.dirty.ratio=0.001
```

### Setup Database

Let's create the `driver` table in Postgresql.

```
docker exec -ti postgresql psql -d sample -U sample
```

On the command prompt, create the table `driver`.

```
DROP TABLE driver;

CREATE TABLE driver (id BIGINT, first_name CHARACTER VARYING(45), last_name CHARACTER VARYING(45), available CHARACTER VARYING(1), birthdate DATE, last_update TIMESTAMP);

ALTER TABLE driver ADD CONSTRAINT driver_pk PRIMARY KEY (id);
```

Let's add some initial data to the newly created table. 

```
INSERT INTO "driver" ("id", "first_name", "last_name", "available", "birthdate", "last_update") VALUES (10,'Diann', 'Butler', 'Y', '10-JUN-68', CURRENT_TIMESTAMP);
INSERT INTO "driver" ("id", "first_name", "last_name", "available", "birthdate", "last_update") VALUES (11,'Micky', 'Isaacson', 'Y', '31-AUG-72' ,CURRENT_TIMESTAMP);
INSERT INTO "driver" ("id", "first_name", "last_name", "available", "birthdate", "last_update") VALUES (12,'Laurence', 'Lindsey', 'Y', '19-MAY-78' ,CURRENT_TIMESTAMP);
INSERT INTO "driver" ("id", "first_name", "last_name", "available", "birthdate", "last_update") VALUES (13,'Pam', 'Harrington', 'Y','10-JUN-68' ,CURRENT_TIMESTAMP);
INSERT INTO "driver" ("id", "first_name", "last_name", "available", "birthdate", "last_update") VALUES (14,'Brooke', 'Ferguson', 'Y','10-DEC-66' ,CURRENT_TIMESTAMP);
INSERT INTO "driver" ("id", "first_name", "last_name", "available", "birthdate", "last_update") VALUES (15,'Clint','Hudson', 'Y','5-JUN-75' ,CURRENT_TIMESTAMP);
INSERT INTO "driver" ("id", "first_name", "last_name", "available", "birthdate", "last_update") VALUES (16,'Ben','Simpson', 'Y','11-SEP-74' ,CURRENT_TIMESTAMP);
INSERT INTO "driver" ("id", "first_name", "last_name", "available", "birthdate", "last_update") VALUES (17,'Frank','Bishop', 'Y','3-OCT-60' ,CURRENT_TIMESTAMP);
INSERT INTO "driver" ("id", "first_name", "last_name", "available", "birthdate", "last_update") VALUES (18,'Trevor','Hines', 'Y','23-FEB-78' ,CURRENT_TIMESTAMP);
INSERT INTO "driver" ("id", "first_name", "last_name", "available", "birthdate", "last_update") VALUES (19,'Christy','Stephens', 'Y','11-JAN-73' ,CURRENT_TIMESTAMP);
INSERT INTO "driver" ("id", "first_name", "last_name", "available", "birthdate", "last_update") VALUES (20,'Clarence','Lamb', 'Y','15-NOV-77' ,CURRENT_TIMESTAMP);
```

### Create a stream of Vehicle Tracking Information

Open two terminals windows.

In the 1st window, run IoT Truck simulator and produce messages to the `truck_position` Kafka topic:

```
docker run trivadis/iot-truck-simulator '-s' 'KAFKA' '-h' $DOCKER_HOST_IP '-p' '9092' '-f' 'JSON'
```

In the 2nd window, start a kafkacat consumer to see the messages:

```
kafkacat -b localhost -t truck_position
```

## Demo

 * [Demo 1 - Streaming Data Lake](#demo-1---streaming-data-lake)
 * [Demo 2 - Batch Processing with Spark](#demo-2---batch-processing-with-spark)
 * [Demo 3 - Batch Query with Presto](#demo-3---batch-query-with-presto)

## Demo 1 - Streaming Data Lake

This demo will show how stream processing can be used to transform raw data (events) into usage-optimised data, ready to be consumed. We will use [ksqlDB](http://ksqldb.io) as the stream processing framework, but any other would work as well.

### Connect to ksqlDB engine

Let's connect to the ksqlDB shell

```
docker exec -it ksqldb-cli ksql http://ksqldb-server-1:8088
```

#### Create Stream and SELECT from it

First drop the stream if it already exists:

```
DROP STREAM IF EXISTS truck_position_raw_s;
```

Now let's create the ksqlDB Stream

```
CREATE STREAM IF NOT EXISTS truck_position_raw_s 
  (timestamp VARCHAR, 
   truckId VARCHAR, 
   driverId BIGINT, 
   routeId BIGINT,
   eventType VARCHAR,
   latitude DOUBLE,
   longitude DOUBLE,
   correlationId VARCHAR)
  WITH (kafka_topic='truck_position',
        value_format='JSON');
```

Let's see the live data by using a `SELECT` on the Stream with the `EMIT CHANGES` clause:

```
SELECT * FROM truck_position_raw_s 
EMIT CHANGES;
```

#### Create a new "refined" stream where the data is transformed into Avro

First drop the stream if it already exists:

```
DROP STREAM IF EXISTS truck_position_refined_s;
```

And now crate the refined ksqlDB Stream:

```
CREATE STREAM IF NOT EXISTS truck_position_refined_s 
  WITH (kafka_topic='truck_position_refined',
        value_format='AVRO')
AS SELECT *
FROM truck_position_raw_s
EMIT CHANGES;
```

to check that the refined topic does in fact hold avro formatted data, let's just do a normal kafkacat on the `truck_position_refined` topic

```
docker exec -ti kafkacat kafkacat -b kafka-1 -t truck_position_refined
```

we can see that it is avro 

```
                            Normal���Q�B@ףp=
WX�$343671958179690963
1598125263176886����
                             Normal��Q��C@�p=
דW�$343671958179690963
% Reached end of topic truck_position_refined [0] at offset 367
159812526333671�ߩ�2Unsafe following distance�Q���B@���(\?W�$343671958179690963
% Reached end of topic truck_position_refined [5] at offset 353
% Reached end of topic truck_position_refined [2] at offset 324
1598125263526101����
                              Normal=
ףpE@R����V�$343671958179690963
% Reached end of topic truck_position_refined [7] at offset 355
```

we can use the `-s` and `-r` option to specify the Avro Serde and the URL of the schema registry

```
docker exec -ti kafkacat kafkacat -b kafka-1 -t truck_position_refined -s avro -r http://schema-registry-1:8081
```

#### Create a new "usage-optimized" stream with the data filered

In this new stream we are only interested in the messages where the `eventType` is not normal. First let's create a SELECT statement which performs the right result, using the ksqlDB CLI:

```
SELECT * FROM truck_position_refined_s 
WHERE eventType != 'Normal'
EMIT CHANGES;
```

Now let's create a new stream with that information. 

```
DROP STREAM IF EXISTS problematic_driving_s;

CREATE STREAM IF NOT EXISTS problematic_driving_s \
  WITH (kafka_topic='problematic_driving', \
        value_format='AVRO', \
        partitions=8) \
AS 
SELECT * 
FROM truck_position_refined_s \
WHERE eventtype != 'Normal';
```

We can see that the stream now only contains the messages filtered down to the relevant ones:

```
SELECT * FROM problematic_driving_s
EMIT CHANGES;
```

We can also see the same information by directly getting the data from the underlaying kafka topic `dangerous_driving_ksql`:

```
docker exec -ti kafkacat kafkacat -b kafka-1 -t dangerous_driving_ksql
```

## Demo 2 - Batch Processing with Spark


## Demo 3 - Batch Query with Presto

```
  presto-1:
    image: ahanaio/prestodb-sandbox
    hostname: presto-1
    container_name: presto-1
    labels:
      com.mdps.service.webui.name: Presto UI
      com.mdps.service.webui.url: http://${PUBLIC_IP}:28081
    ports:
      - 28081:8080
    volumes:
      - ./conf/presto/minio.properties:/usr/lib/presto/etc/catalog/minio.properties
      - ./conf/presto/kafka.properties:/usr/lib/presto/etc/catalog/kafka.properties
      - ./conf/presto/kafka-hive.properties:/usr/lib/presto/etc/catalog/kafka-hive.properties
      - ./scripts/presto/:/usr/lib/presto/etc/kafka/tabledesc/
      - ./conf/presto/minio.properties:/opt/presto-server/etc/catalog/minio.properties
      - ./conf/presto/kafka.properties:/opt/presto-server/etc/catalog/kafka.properties
      - ./conf/presto/kafka-hive.properties:/opt/presto-server/etc/catalog/kafka-hive.properties
      - ./scripts/presto/:/opt/presto-server/etc/kafka/tabledesc
    restart: unless-stopped
```

```
kafka.nodes=kafka-1:9092
kafka.table-names=truck_position
kafka.default-schema=logistics
kafka.hide-internal-columns=false
kafka.table-description-dir=etc/kafka/tabledesc/
```

Next let's query the data from Presto. Connect to the Presto CLI using

```
kafkacat -b localhost -t truck_position


```
presto --server localhost:28081 --catalog kafka --schema logistics
```

```
SELECT * FROM truck_position;
```

```
SELECT json_extract(_message, '$.truckId') as truck_id FROM truck_position;
```

### truck_position table

```
{
    "tableName": "truck_position",
    "schemaName": "logistics",
    "topicName": "truck_position",
    "key": {
        "dataFormat": "raw",
        "fields": [
            {
                "name": "kafka_key",
                "dataFormat": "BYTE",
                "type": "VARCHAR",
                "hidden": "false"
            }        
	]
    },
    "message": {
        "dataFormat": "json",
        "fields": [
            {
                "name": "timestamp",
                "mapping": "timestamp",
                "type": "BIGINT"
            },
            {
                "name": "truck_id",
                "mapping": "truckId",
                "type": "BIGINT"
            },
            {
                "name": "driver_id",
                "mapping": "driverId",
                "type": "BIGINT"
            },
            {
                "name": "route_id",
                "mapping": "routeId",
                "type": "BIGINT"
            },
            {
                "name": "event_type",
                "mapping": "eventType",
                "type": "VARCHAR"
            },
            {
                "name": "latitude",
                "mapping": "latitude",
                "type": "DOUBLE"
            },
            {
                "name": "longitude",
                "mapping": "longitude",
                "type": "DOUBLE"
            }       
	]
    }
}
```

### Truck Driver Table

```
{
    "tableName": "truck_driver",
    "schemaName": "logistics",
    "topicName": "truck_driver",
    "key": {
        "dataFormat": "raw",
        "fields": [
            {
                "name": "kafka_key",
                "dataFormat": "BYTE",
                "type": "VARCHAR",
                "hidden": "false"
            }        
	]
    },
    "message": {
        "dataFormat": "json",
        "fields": [
            {
                "name": "id",
                "mapping": "id",
                "type": "BIGINT"
            },
            {
                "name": "first_name",
                "mapping": "first_name",
                "type": "VARCHAR"
            },
            {
                "name": "last_name",
                "mapping": "last_name",
                "type": "VARCHAR"
            },
            {
                "name": "available",
                "mapping": "available",
                "type": "VARCHAR"
            },
            {
                "name": "birthdate",
                "mapping": "birthdate",
                "type": "BIGINT"
            },
            {
                "name": "last_update",
                "mapping": "last_update",
                "type": "BIGINT"
            }     
	]
    }
}
```

```
SELECT * 
FROM truck_driver 
WHERE (last_update) IN (SELECT LAST_VALUE(last_update) OVER (PARTITION BY id 
											ORDER BY last_update 
											RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_update 
							FROM truck_driver);
```


```
SELECT d.id, d.first_name, d.last_name, t.*
FROM truck_position t
LEFT JOIN (
	SELECT * 
	FROM truck_driver 
	WHERE (last_update) IN (SELECT LAST_VALUE(last_update) OVER (PARTITION BY id 
												ORDER BY last_update 
												RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_update 
								FROM truck_driver)	) d						
ON t.driver_id = d.id
WHERE t.event_type != 'Normal';
```



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


## Demo 2 - Stream Analytics

### Connect to KSQL engine

```
docker exec -it ksqldb-cli ksql http://ksqldb-server-1:8088
```

### Create Stream and SELECT from it

```
DROP STREAM truck_position_s;
```

if CSV

```
CREATE STREAM truck_position_s 
  (ts VARCHAR, 
   truckId VARCHAR, 
   driverId BIGINT, 
   routeId BIGINT,
   eventType VARCHAR,
   latitude DOUBLE,
   longitude DOUBLE,
   correlationId VARCHAR)
  WITH (kafka_topic='truck_position',
        value_format='DELIMITED');
```

if JSON

```
CREATE STREAM truck_position_s 
  (ts VARCHAR, 
   truckId VARCHAR, 
   driverId BIGINT, 
   routeId BIGINT,
   eventType VARCHAR,
   latitude DOUBLE,
   longitude DOUBLE,
   correlationId VARCHAR)
  WITH (kafka_topic='truck_position',
        value_format='JSON');
```


```
SELECT * FROM truck_position_s 
EMIT CHANGES;
```

```
SELECT * FROM truck_position_s 
WHERE eventType != 'Normal'
EMIT CHANGES;
```

### Create Stream and SELECT from it

```
DROP STREAM dangerous_driving_s;

CREATE STREAM dangerous_driving_s \
  WITH (kafka_topic='dangerous_driving_ksql', \
        value_format='JSON', \
        partitions=8) \
AS 
SELECT * 
FROM truck_position_s \
WHERE eventtype != 'Normal';
```

```
SELECT * FROM dangerous_driving_s
EMIT CHANGES;
```

```
kafkacat -b localhost -t dangerous_driving_ksql
```


## Demo 3 - Enrich Data

### Show driver table

```
docker exec -ti postgresql psql -d sample -U sample


SELECT * FROM driver;
```

### Run a kafkacat on `truck_driver` topic

```
kafkacat -b localhost -t truck_driver
```

### Create CDC Connector

```
curl -X "POST" "$DOCKER_HOST_IP:8083/connectors" \
     -H "Content-Type: application/json" \
     -d $'{
  "name": "jdbc-driver-source",
  "config": {
    "connector.class": "JdbcSourceConnector",
    "tasks.max": "1",
    "connection.url":"jdbc:postgresql://postgresql/sample?user=sample&password=sample",
    "mode": "timestamp",
    "timestamp.column.name":"last_update",
    "table.whitelist":"driver",
    "validate.non.null":"false",
    "topic.prefix":"truck_",
    "key.converter":"org.apache.kafka.connect.storage.StringConverter",
    "key.converter.schemas.enable": "false",
    "value.converter":"org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false",
    "name": "jdbc-driver-source",
     "transforms":"createKey,extractInt",
     "transforms.createKey.type":"org.apache.kafka.connect.transforms.ValueToKey",
     "transforms.createKey.fields":"id",
     "transforms.extractInt.type":"org.apache.kafka.connect.transforms.ExtractField$Key",
     "transforms.extractInt.field":"id"
  }
}'
```

```
curl -X "DELETE" "http://$DOCKER_HOST_IP:8083/connectors/jdbc-driver-source"
```

```
UPDATE "driver" SET "available" = 'N', "last_update" = CURRENT_TIMESTAMP  WHERE "id" = 21;
UPDATE "driver" SET "available" = 'N', "last_update" = CURRENT_TIMESTAMP  WHERE "id" = 14;
```

check with kafkacat

```
kafkacat -b localhost -t truck_driver -o beginning
```

### Create Join in KSQL

```
set 'commit.interval.ms'='5000';
set 'cache.max.bytes.buffering'='10000000';
set 'auto.offset.reset'='earliest';

DROP TABLE driver_t;

CREATE TABLE driver_t (rowkey VARCHAR PRIMARY KEY,
   id BIGINT,
   first_name VARCHAR,  
   last_name VARCHAR,  
   available VARCHAR, 
   birthdate VARCHAR)  
  WITH (kafka_topic='truck_driver', 
        value_format='JSON');
```

```
SELECT driverid, first_name, last_name, truckId, routeId ,eventType \
FROM dangerous_driving_s \
LEFT JOIN driver_t \
ON CAST (dangerous_driving_s.driverId AS VARCHAR) = driver_t.ROWKEY
EMIT CHANGES;
```

Add missing data

```
docker exec -ti postgresql psql -d sample -U sample
```

```
INSERT INTO "driver" ("id", "first_name", "last_name", "available", "birthdate", "last_update") VALUES (21,'Lila', 'Page', 'Y', '5-APR-77', CURRENT_TIMESTAMP);
INSERT INTO "driver" ("id", "first_name", "last_name", "available", "birthdate", "last_update") VALUES (22,'Patricia', 'Coleman', 'Y', '11-AUG-80' ,CURRENT_TIMESTAMP);
INSERT INTO "driver" ("id", "first_name", "last_name", "available", "birthdate", "last_update") VALUES (23,'Jeremy', 'Olson', 'Y', '13-JUN-82', CURRENT_TIMESTAMP);
INSERT INTO "driver" ("id", "first_name", "last_name", "available", "birthdate", "last_update") VALUES (24,'Walter', 'Ward', 'Y', '24-JUL-85', CURRENT_TIMESTAMP);
INSERT INTO "driver" ("id", "first_name", "last_name", "available", "birthdate", "last_update") VALUES (25,'Kristen', ' Patterson', 'Y', '14-JUN-73', CURRENT_TIMESTAMP);
INSERT INTO "driver" ("id", "first_name", "last_name", "available", "birthdate", "last_update") VALUES (26,'Jacquelyn', 'Fletcher', 'Y', '24-AUG-85', CURRENT_TIMESTAMP);
INSERT INTO "driver" ("id", "first_name", "last_name", "available", "birthdate", "last_update") VALUES (27,'Walter', '  Leonard', 'Y', '12-SEP-88', CURRENT_TIMESTAMP);
INSERT INTO "driver" ("id", "first_name", "last_name", "available", "birthdate", "last_update") VALUES (28,'Della', ' Mcdonald', 'Y', '24-JUL-79', CURRENT_TIMESTAMP);
INSERT INTO "driver" ("id", "first_name", "last_name", "available", "birthdate", "last_update") VALUES (29,'Leah', 'Sutton', 'Y', '12-JUL-75', CURRENT_TIMESTAMP);
INSERT INTO "driver" ("id", "first_name", "last_name", "available", "birthdate", "last_update") VALUES (30,'Larry', 'Jensen', 'Y', '14-AUG-83', CURRENT_TIMESTAMP);
INSERT INTO "driver" ("id", "first_name", "last_name", "available", "birthdate", "last_update") VALUES (31,'Rosemarie', 'Ruiz', 'Y', '22-SEP-80', CURRENT_TIMESTAMP);
INSERT INTO "driver" ("id", "first_name", "last_name", "available", "birthdate", "last_update") VALUES (32,'Shaun', ' Marshall', 'Y', '22-JAN-85', CURRENT_TIMESTAMP);
```


```
DROP STREAM dangerous_driving_and_driver_s;

CREATE STREAM dangerous_driving_and_driver_s \
  WITH (kafka_topic='dangerous_driving_and_driver_ksql', \
        value_format='JSON', \
        partitions=8) \
AS 
SELECT driverid, first_name, last_name, truckId, routeId ,eventType \
FROM dangerous_driving_s \
LEFT JOIN driver_t \
ON CAST (dangerous_driving_s.driverId AS VARCHAR) = driver_t.ROWKEY;
```

# Twitter Example

## Create Twitter Source

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
