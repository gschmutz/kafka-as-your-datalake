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

Using the `kafka-topics` CLI inside the `kafka-1` docker container create the different Kafka topics:

```
docker exec -it kafka-1 kafka-topics --zookeeper zookeeper-1:2181 --create --topic truck_position --partitions 8 --replication-factor 3
docker exec -it kafka-1 kafka-topics --zookeeper zookeeper-1:2181 --create --topic dangerous_driving_ksql --partitions 8 --replication-factor 3
docker exec -it kafka-1 kafka-topics --zookeeper zookeeper-1:2181 --create --topic dangerous_driving_and_driver_ksql --partitions 8 --replication-factor 3
docker exec -it kafka-1 kafka-topics --zookeeper zookeeper-1:2181 --create --topic logisticsdb_driver --partitions 8 --replication-factor 3 --config cleanup.policy=compact --config segment.ms=100 --config delete.retention.ms=100 --config min.cleanable.dirty.ratio=0.001
```

### Setup logistics_db Postgresql Database

Let's create the `driver` table in Postgresql.

```
docker exec -ti postgresql psql -d demodb -U demo
```

On the command prompt, create the table `driver`.

```
CREATE SCHEMA IF NOT EXISTS logistics_db;

SET search_path TO logistics_db;

DROP TABLE IF EXISTS driver;

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

### Using CDC to move Postgresql driver table to Kafka topic

We will use the Kafka Connect JDBC connector to move the data from the `driver` Postgresql table to `logisticsdb_driver` Kafka topic with the same name.

```
curl -X "POST" "$DOCKER_HOST_IP:8083/connectors" \
     -H "Content-Type: application/json" \
     -d $'{
  "name": "jdbc-driver-source",
  "config": {
    "connector.class": "JdbcSourceConnector",
    "tasks.max": "1",
    "connection.url":"jdbc:postgresql://postgresql/demodb?user=demo&password=abc123!",
    "mode": "timestamp",
    "timestamp.column.name":"last_update",
    "schema.pattern":"logistics_db",
    "table.whitelist":"driver",
    "validate.non.null":"false",
    "topic.prefix":"logisticsdb_",
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

Check that all the data is successfully appended to the `logisticsdb_driver` topic:

```
docker exec -ti kafkacat kafkacat -b kafka-1 -t logisticsdb_driver
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

We can also see the same information by directly getting the data from the underlaying kafka topic `problematic_driving`:

```
docker exec -ti kafkacat kafkacat -b kafka-1 -t problematic_driving -s avro -r http://schema-registry-1:8081
```

## Demo 2 - Batch Processing with Spark

In this demo we will see how Spark can be used to access the Kafka topic from a Batch process.


## Demo 3 - Batch Query with Presto

In this demo we will show how Presto can be used to query a Kafka topic in a "batch" manner. By that you basically treat Kafka as a "table" and can perform queries on all the data stored in the topic. 

### Configure the Kafka connector

First lets configure the [Kafka connector](https://prestodb.io/docs/current/connector/kafka.html) and make the Kafka topics known to Kafka.

In order to not change the `docker-compose.yml` (it is generated) directly, we can use the `cdocker-compose.override.yml` file to overwrite settings of the various services. 

Add the following lines to `docker-compose.override.yml`:

```
version: '3.0'
services:
  presto-1:
    volumes:
      - ./conf/presto/catalog/kafka.properties:/usr/lib/presto/etc/catalog/kafka.properties
      - ./conf/presto/catlog/kafka-hive.properties:/usr/lib/presto/etc/catalog/kafka-hive.properties
      - ./scripts/presto/truck_position.json:/usr/lib/presto/default/etc/kafka/truck_position.json
      - ./plugins/presto/presto-kafka-340.jar:/usr/lib/presto/plugin/kafka/presto-kafka-340.jar
```

if using Presto DB, it would be

```
version: '3.0'
services:
  presto-1:
    volumes:
      - ./conf/presto/kafka.properties:/opt/presto-server/etc/catalog/kafka.properties
      - ./conf/presto/kafka-hive.properties:/opt/presto-server/etc/catalog/kafka-hive.properties
      - ./scripts/presto/truck_position.json:/opt/presto-server/etc/kafka/tabledesc/truck_position.json
```

Create the `kafka.properties` in folder `./conf/presto/catalog`. We can see that we register `truck_position` as a table and assign it to the `logistics` schema. 

```
kafka.nodes=kafka-1:19092
kafka.table-names=truck_position
kafka.default-schema=logistics
kafka.hide-internal-columns=false
kafka.table-description-dir=/usr/lib/presto/default/etc/kafka
```

Restart the `presto-1` service so that the configuration changes are picked up by Presto.

```
docker restart presto-1
```

### Let's use Presto to query the data from the Kafka topic

Next let's query the data from Presto. Connect to the Presto CLI using

```
docker exec -ti presto-cli presto --server presto-1:8080 --catalog kafka --schema logistics
```

on the `presto:logistics>` prompt use the `show tables` command to display the registered tables:

```
show tables;
```

and you should get exactly one row back, the `truck_position` table:

```
presto:logistics> show tables
               -> ;
     Table      
----------------
 truck_position 
(1 row)
```

Now we can use the `SELECT` statement on the table to return the data:

```
SELECT * FROM truck_position;
```

We can see that we get some data back, but the message is shown as just one column `_message`, and not split up into one column per field in the message. The reason for that is that the connector does not yet know about how to interpret the message.  

```
presto:logistics> SELECT * FROM truck_position;
 _partition_id | _partition_offset | _message_corrupt |                                                                                            _message
---------------+-------------------+------------------+---------------------------------------------------------------------------------------------------------------------------------------------
             2 |                 0 | false            | {"timestamp":1597770414534,"truckId":58,"driverId":32,"routeId":1325712174,"eventType":"Normal","correlationId":"-2599424926733256171","lati
             2 |                 1 | false            | {"timestamp":1597770417571,"truckId":58,"driverId":32,"routeId":1325712174,"eventType":"Normal","correlationId":"-2599424926733256171","lati
             2 |                 2 | false            | {"timestamp":1597770420720,"truckId":58,"driverId":32,"routeId":1325712174,"eventType":"Normal","correlationId":"-2599424926733256171","lati
             2 |                 3 | false            | {"timestamp":1597770424360,"truckId":58,"driverId":32,"routeId":1325712174,"eventType":"Normal","correlationId":"-2599424926733256171","lati
             2 |                 4 | false            | {"timestamp":1597770427381,"truckId":58,"driverId":32,"routeId":1325712174,"eventType":"Normal","correlationId":"-2599424926733256171","lati
             2 |                 5 | false            | {"timestamp":1597770430941,"truckId":58,"driverId":32,"routeId":1325712174,"eventType":"Normal","correlationId":"-2599424926733256171","lati
             2 |                 6 | false            | {"timestamp":1597770434240,"truckId":58,"driverId":32,"routeId":1325712174,"eventType":"Normal","correlationId":"-2599424926733256171","lati
             2 |                 7 | false            | {"timestamp":1597770437801,"truckId":58,"driverId":32,"routeId":1325712174,"eventType":"Normal","correlationId":"-2599424926733256171","lati
             2 |                 8 | false            | {"timestamp":1597770440870,"truckId":58,"driverId":32,"routeId":1325712174,"eventType":"Normal","correlationId":"-2599424926733256171","lati
             2 |                 9 | false            | {"timestamp":1597770444700,"truckId":58,"driverId":32,"routeId":1325712174,"eventType":"Normal","correlationId":"-2599424926733256171","lati
             2 |                10 | false            | {"timestamp":1597770448101,"truckId":58,"driverId":32,"routeId":1325712174,"eventType":"Normal","correlationId":"-2599424926733256171","lati
```

One way to split the value of the `_message` column up is by using the `json_extract` Presto SQL function:

```
SELECT json_extract(_message, '$.truckId') as truck_id
	, json_extract(_message, '$.driverId') as driver_id
	, json_extract(_message, '$.eventType') as event_type 
	, json_extract(_message, '$.latitude') as latitude 
	, json_extract(_message, '$.longitude') as longitude 
FROM truck_position;
```

Unfortunately the Presto Kafka connector does not support creating views, so every access of the table would have to deal with this. 

But there is another way to do the mapping in a more static fashion. 


### Using a table definition to map the topic to a table

We can create a table definition file, which consists of a JSON definition for a table. Create a file `truck_position.json` in the folder `./scripts/presto/` and add the following content:

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
                "type": "BIGINT",
                "comment": "Time of the tracking message in real life"
            },
            {
                "name": "truck_id",
                "mapping": "truckId",
                "type": "BIGINT",
                "comment": "ID of the truck"
            },
            {
                "name": "driver_id",
                "mapping": "driverId",
                "type": "BIGINT",
                "comment": "ID of the driver"
            },
            {
                "name": "route_id",
                "mapping": "routeId",
                "type": "BIGINT",
                "comment": "ID of the route the truck is driving on."
            },
            {
                "name": "event_type",
                "mapping": "eventType",
                "type": "VARCHAR",
                "comment": "Driving behaviour, where Normal signals normal behaviour"
            },
            {
                "name": "latitude",
                "mapping": "latitude",
                "type": "DOUBLE",
                "comment": "Latitude part of the geo coordinate"
            },
            {
                "name": "longitude",
                "mapping": "longitude",
                "type": "DOUBLE",
                "comment": "Longitude part of the geo coordinate"
            }       
	]
    }
}
```

In the `kafka.properties` configuration file, there is one setting `kafka.table-description-dir=/usr/lib/presto/default/etc/kafka` which specifies where Presto can find the table definition file and in the `docker-compose.override.yml` the local file defined above is mapped into the `presto-1` container.

Recreate the `presto-1` container using `docker-compose up -d`.

Now we can use the `SELECT` statement to prove that the mapping is working. From the Presto command line, execute:

```
SELECT * FROM truck_position;
```

we can see that there is no longer a `_message` column but instead one column for each mapping of the table definition file. Much more usable of course!

```
presto:logistics> SELECT * FROM truck_position;
 kafka_key |   timestamp   | truck_id | driver_id |  route_id  |        event_type         | latitude | longitude | _partition_id | _partition_offset | _message_corrupt |
-----------+---------------+----------+-----------+------------+---------------------------+----------+-----------+---------------+-------------------+------------------+--------------------------
 81        | 1597770414480 |       81 |      NULL | 1927624662 | Normal                    |    41.62 |    -93.58 |             1 |                 0 | false            | {"timestamp":159777041448
 75        | 1597770415144 |       75 |      NULL | 1390372503 | Normal                    |     40.7 |    -89.52 |             1 |                 1 | false            | {"timestamp":159777041514
 57        | 1597770415211 |       57 |      NULL | 1594289134 | Normal                    |    38.65 |     -90.2 |             1 |                 2 | false            | {"timestamp":159777041521
 75        | 1597770417850 |       75 |      NULL | 1390372503 | Normal                    |    40.86 |    -89.91 |             1 |                 3 | false            | {"timestamp":159777041785
 81        | 1597770417865 |       81 |      NULL | 1927624662 | Normal                    |    41.69 |    -93.36 |             1 |                 4 | false            | {"timestamp":159777041786
 57        | 1597770418510 |       57 |      NULL | 1594289134 | Normal                    |     39.1 |    -89.74 |             1 |                 5 | false            | {"timestamp":159777041851
 75        | 1597770421350 |       75 |      NULL | 1390372503 | Normal                    |    40.96 |    -90.29 |             1 |                 6 | false            | {"timestamp":159777042135
 81        | 1597770421700 |       81 |      NULL | 1927624662 | Normal                    |    41.71 |    -93.04 |             1 |                 7 | false            | {"timestamp":159777042170
 57        | 1597770422001 |       57 |      NULL | 1594289134 | Normal                    |    39.84 |    -89.63 |             1 |                 8 | false            | {"timestamp":159777042200
``` 

We can also do a describe of the table to see the definition

```
DESCRIBE truck_position;
```

We can see "our" own columns from the definition and some other internal columns all starting with `_`. They represent some technical properties of a Kafka message, such as the partition or the offset of the message.

```
presto:logistics> describe truck_position;
      Column       |     Type     | Extra |                         Comment
-------------------+--------------+-------+----------------------------------------------------------
 kafka_key         | varchar      |       |
 timestamp         | bigint       |       | Time of the tracking message in real life
 truck_id          | bigint       |       | ID of the truck
 driver_id         | bigint       |       | ID of the driver
 route_id          | bigint       |       | ID of the route the truck is driving on.
 event_type        | varchar      |       | Driving behaviour, where Normal signals normal behaviour
 latitude          | double       |       | Latitude part of the geo coordinate
 longitude         | double       |       | Longitude part of the geo coordinate
 _partition_id     | bigint       |       | Partition Id
 _partition_offset | bigint       |       | Offset for the message within the partition
 _message_corrupt  | boolean      |       | Message data is corrupt
 _message          | varchar      |       | Message text
 _message_length   | bigint       |       | Total number of message bytes
 _key_corrupt      | boolean      |       | Key data is corrupt
 _key              | varchar      |       | Key text
 _key_length       | bigint       |       | Total number of key bytes
 _timestamp        | timestamp(3) |       | Offset Timestamp
(17 rows)
```

We can restrict on any column, for example on `event_type`.

```
SELECT * FROM truck_position
WHERE event_type != 'Normal';
```

It will of course do a full topic scan, as there are no indexes on Kafka (except on timestamp to offset):

```
 kafka_key |   timestamp   | truck_id | driver_id |  route_id  |        event_type         | latitude | longitude | _partition_id | _partition_offset | _message_corrupt |
-----------+---------------+----------+-----------+------------+---------------------------+----------+-----------+---------------+-------------------+------------------+--------------------------
 28        | 1597770574886 |       28 |        10 | 1962261785 | Overspeed                 |    36.37 |     -95.5 |             3 |                29 | false            | {"timestamp":159777057488
 28        | 1597770676875 |       28 |        10 | 1962261785 | Unsafe following distance |    38.22 |    -91.18 |             3 |                59 | false            | {"timestamp":159777067687
 28        | 1597770782107 |       28 |        10 | 1962261785 | Unsafe tail distance      |    37.09 |    -94.23 |             3 |                89 | false            | {"timestamp":159777078210
 28        | 1597770887296 |       28 |        10 | 1962261785 | Overspeed                 |    37.81 |    -92.08 |             3 |               119 | false            | {"timestamp":159777088729
 28        | 1597770993075 |       28 |        10 | 1962261785 | Lane Departure            |    37.51 |    -92.89 |             3 |               149 | false            | {"timestamp":159777099307
 28        | 1597771098076 |       28 |        10 | 1962261785 | Lane Departure            |    37.34 |    -92.99 |             3 |               179 | false            | {"timestamp":159777109807
 28        | 1597771206866 |       28 |        10 | 1962261785 | Overspeed                 |    37.94 |    -91.99 |             3 |               209 | false            | {"timestamp":159777120686
 28        | 1597771310386 |       28 |        10 | 1962261785 | Unsafe following distance |    37.02 |    -94.54 |             3 |               239 | false            | {"timestamp":159777131038
 71        | 1598124739056 |       71 |        10 | 1927624662 | Unsafe tail distance      |    36.37 |     -95.5 |             3 |               412 | false            | {"timestamp":159812473905
 71        | 1598124841586 |       71 |        10 | 1927624662 | Unsafe following distance |    38.22 |    -91.18 |             3 |               559 | false            | {"timestamp":159812484158
 71        | 1598124944886 |       71 |        10 | 1927624662 | Unsafe following distance |    37.09 |    -94.23 |             3 |               708 | false            | {"timestamp":159812494488
 31        | 1598124950196 |       31 |        25 | 1961634315 | Unsafe tail distance      |    36.84 |    -89.54 |             3 |               715 | false            | {"timestamp":159812495019
 88        | 1598124985256 |       88 |        27 |  160779139 | Unsafe tail distance      |    38.83 |    -90.79 |             3 |               765 | false            | {"timestamp":159812498525
 92        | 1598124986356 |       92 |        16 |  987179512 | Unsafe tail distance      |     40.7 |    -89.52 |             3 |               766 | false            | {"timestamp":159812498635
```
 
Knowing that we can also do more complex analytics using all the capabilities of the SQL language built into Presto and available to the Kafka connector as well. 

```
SELECT driver_id, event_type, count(*) as nof
FROM truck_position
WHERE event_type != 'Normal'
GROUP BY driver_id, event_type;
```

We get the count of unnormal event types per driver:

```
 driver_id |        event_type         | nof
-----------+---------------------------+-----
        11 | Overspeed                 |  71
        11 | Lane Departure            |  74
        15 | Lane Departure            |  10
        32 | Overspeed                 |   6
        25 | Lane Departure            |   8
        22 | Overspeed                 |   7
        18 | Unsafe tail distance      |  12
        16 | Unsafe tail distance      |   7
        20 | Lane Departure            |   5
        27 | Overspeed                 |   4
        30 | Overspeed                 |   8
        28 | Overspeed                 |   8
        29 | Unsafe tail distance      |   3
        29 | Lane Departure            |   5
        18 | Overspeed                 |   4
        20 | Unsafe tail distance      |  11
        20 | Overspeed                 |   8
        16 | Lane Departure            |   5
        32 | Lane Departure            |  10
        28 | Unsafe following distance |   6
        28 | Unsafe tail distance      |   8
        27 | Unsafe following distance |  10
        17 | Unsafe tail distance      |   5
        17 | Lane Departure            |   8
        18 | Unsafe following distance |   5
```

In such a query it would be interesting to know the name of the driver. But this information it is not available in the Kafka topic. Knowing SQL, we could use a Join Operation to join data from the `truck_position` table/topic to the `driver` table in the Postgresql database (we have created in the preperation step above). This is what we will do in the next section.

### Joining with Driver table in Postgresql

Presto allows to work with multiple data sources in one single statement. 


```
docker exec -ti presto-cli presto --server presto-1:8080 --catalog kafka --schema logistics
```

```
SELECT * FROM postgresql.logistics_db.driver;
```

```
 id | first_name | last_name  | available | birthdate  |       last_update
----+------------+------------+-----------+------------+-------------------------
 10 | Diann      | Butler     | Y         | 2068-06-10 | 2020-08-23 11:30:36.936
 11 | Micky      | Isaacson   | Y         | 1972-08-31 | 2020-08-23 11:30:36.940
 12 | Laurence   | Lindsey    | Y         | 1978-05-19 | 2020-08-23 11:30:36.942
 13 | Pam        | Harrington | Y         | 2068-06-10 | 2020-08-23 11:30:36.945
 14 | Brooke     | Ferguson   | Y         | 2066-12-10 | 2020-08-23 11:30:36.947
 15 | Clint      | Hudson     | Y         | 1975-06-05 | 2020-08-23 11:30:36.949
 16 | Ben        | Simpson    | Y         | 1974-09-11 | 2020-08-23 11:30:36.951
 17 | Frank      | Bishop     | Y         | 2060-10-03 | 2020-08-23 11:30:36.953
 18 | Trevor     | Hines      | Y         | 1978-02-23 | 2020-08-23 11:30:36.955
 19 | Christy    | Stephens   | Y         | 1973-01-11 | 2020-08-23 11:30:36.957
 20 | Clarence   | Lamb       | Y         | 1977-11-15 | 2020-08-23 11:30:36.958
(11 rows)
```

```
SELECT tp.driver_id, d.first_name, d.last_name, tp.event_type, count(*) as nof
FROM truck_position		AS tp
LEFT JOIN postgresql.logistics_db.driver   AS d
ON tp.driver_id = d.id
WHERE event_type != 'Normal'
GROUP BY tp.driver_id, d.first_name, d.last_name, tp.event_type;
```

```
 driver_id | first_name | last_name  |        event_type         | nof
-----------+------------+------------+---------------------------+-----
        16 | Ben        | Simpson    | Unsafe tail distance      |   7
        11 | Micky      | Isaacson   | Lane Departure            |  74
        19 | Christy    | Stephens   | Unsafe tail distance      |   4
        31 | NULL       | NULL       | Unsafe tail distance      |   6
        11 | Micky      | Isaacson   | Unsafe tail distance      |  83
        25 | NULL       | NULL       | Unsafe tail distance      |  11
        25 | NULL       | NULL       | Lane Departure            |   8
        25 | NULL       | NULL       | Overspeed                 |   6
        15 | Clint      | Hudson     | Unsafe tail distance      |   6
        15 | Clint      | Hudson     | Unsafe following distance |   7
        19 | Christy    | Stephens   | Lane Departure            |   3
        27 | NULL       | NULL       | Lane Departure            |   8
        28 | NULL       | NULL       | Unsafe following distance |   6
```

```
SELECT driver_id, first_name, last_name, event_type, nof
FROM (SELECT driver_id, event_type, count(*) AS nof
		FROM truck_position
		WHERE event_type != 'Normal'
		GROUP BY driver_id, event_type
		)		AS tp
LEFT JOIN postgresql.logistics_db.driver   AS d
ON tp.driver_id = d.id
```

### Joining with Driver topic

Add the `logisticsdb_driver` topic to the property `kafka.table-names` in the `kafka.properties` file, so that it will be available in Presto as a table.

```
kafka.nodes=kafka-1:19092
kafka.table-names=truck_position,logisticsdb_driver
kafka.default-schema=logistics
kafka.hide-internal-columns=false
kafka.table-description-dir=/usr/lib/presto/default/etc/kafka
```

Now restart the `presto-1` container using `docker restart presto-1`.

Connect to the Presto CLI

```
docker exec -ti presto-cli presto --server presto-1:8080 --catalog kafka --schema logistics
```

and show the tables available

```
show tables
```

If we describe the `logisticsdb_driver` table 

```
DESCRIBE logisticsdb_driver;
```

we can see that the whole raw message is available as `_message`:

```
      Column       |     Type     | Extra |                   Comment
-------------------+--------------+-------+---------------------------------------------
 _partition_id     | bigint       |       | Partition Id
 _partition_offset | bigint       |       | Offset for the message within the partition
 _message_corrupt  | boolean      |       | Message data is corrupt
 _message          | varchar      |       | Message text
 _message_length   | bigint       |       | Total number of message bytes
 _key_corrupt      | boolean      |       | Key data is corrupt
 _key              | varchar      |       | Key text
 _key_length       | bigint       |       | Total number of key bytes
 _timestamp        | timestamp(3) |       | Offset Timestamp
(9 rows)
```

Let's see the content

```
SELECT _message FROM logisticsdb_driver;
```

and we can see that each driver is avaialbe as a JSON record:

```
                                                       _message
----------------------------------------------------------------------------------------------------------------------
 {"id":16,"first_name":"Ben","last_name":"Simpson","available":"Y","birthdate":1714,"last_update":1598182236951}
 {"id":17,"first_name":"Frank","last_name":"Bishop","available":"Y","birthdate":33148,"last_update":1598182236953}
 {"id":13,"first_name":"Pam","last_name":"Harrington","available":"Y","birthdate":35955,"last_update":1598182236945}
 {"id":14,"first_name":"Brooke","last_name":"Ferguson","available":"Y","birthdate":35407,"last_update":1598182236947}
 {"id":19,"first_name":"Christy","last_name":"Stephens","available":"Y","birthdate":1106,"last_update":1598182236957}
 {"id":10,"first_name":"Diann","last_name":"Butler","available":"Y","birthdate":35955,"last_update":1598182236936}
 {"id":12,"first_name":"Laurence","last_name":"Lindsey","available":"Y","birthdate":3060,"last_update":1598182236942}
 {"id":15,"first_name":"Clint","last_name":"Hudson","available":"Y","birthdate":1981,"last_update":1598182236949}
 {"id":20,"first_name":"Clarence","last_name":"Lamb","available":"Y","birthdate":2875,"last_update":1598182236958}
 {"id":11,"first_name":"Micky","last_name":"Isaacson","available":"Y","birthdate":973,"last_update":1598182236940}
 {"id":18,"first_name":"Trevor","last_name":"Hines","available":"Y","birthdate":2975,"last_update":1598182236955}
(11 rows)
```

We could again use the `json_extract` function to split the properties into separate columns or use another table definition file. 

Here is the table definition file for mapping the data of the `logisticsdb_driver` topic to individual columns. Create a new file `logisticsdb_driver.json` in the folder `./scripts/presto/`


```
{
    "tableName": "logisticsdb_driver",
    "schemaName": "logistics",
    "topicName": "logisticsdb_driver",
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

and add an additional mapping to the `docker-compse.override.yml` to map the table definition file into the `presto-1` container:

```
      - ./scripts/presto/truck_position.json:/usr/lib/presto/default/etc/kafka/truck_position.json
```

Recreate the `presto-1` container using `docker-compose up -d`.

If you now do a describe on the table, you should see the effects of the mapping:

```
      Column       |     Type     | Extra |                   Comment
-------------------+--------------+-------+---------------------------------------------
 kafka_key         | varchar      |       |
 id                | bigint       |       |
 first_name        | varchar      |       |
 last_name         | varchar      |       |
 available         | varchar      |       |
 birthdate         | bigint       |       |
 last_update       | bigint       |       |
 _partition_id     | bigint       |       | Partition Id
 _partition_offset | bigint       |       | Offset for the message within the partition
 _message_corrupt  | boolean      |       | Message data is corrupt
 _message          | varchar      |       | Message text
 _message_length   | bigint       |       | Total number of message bytes
 _key_corrupt      | boolean      |       | Key data is corrupt
 _key              | varchar      |       | Key text
 _key_length       | bigint       |       | Total number of key bytes
 _timestamp        | timestamp(3) |       | Offset Timestamp
```

We can now use the same SELECT statement as before, but replace the Postgresql `postgresql.logistics_db.driver ` table by the Kafka table:

```
SELECT driver_id, first_name, last_name, event_type, nof
FROM (SELECT driver_id, event_type, count(*) AS nof
		FROM truck_position
		WHERE event_type != 'Normal'
		GROUP BY driver_id, event_type
		)		AS tp
LEFT JOIN logisticsdb_driver   AS d
ON tp.driver_id = d.id;
```

We will get the same result as before, but no longer being dependent on two data sources. 

#### Be aware of update on the `logisticsdb_driver` topic!

Let's see what happens if we do an update on one of the drivers in the Postgresql table. But first let's see the current state of driver with ID `21`:

```
SELECT * 
FROM logisticsdb_driver
WHERE id = 21; 
```

we can see that we get one record with `available` set to `Y`. 

```
 kafka_key | id | first_name | last_name | available | birthdate |  last_update  | _partition_id | _partition_offset | _message_corrupt |                                                   _messag>
-----------+----+------------+-----------+-----------+-----------+---------------+---------------+-------------------+------------------+---------------------------------------------------------->
 21        | 21 | Lila       | Page      | Y         |      2651 | 1598186449022 |             4 |                 1 | false            | {"id":21,"first_name":"Lila","last_name":"Page","availabl>
```

Let's update that record in the source table in Postgresql, but before doing that, let's listen on the Kafka topic using kafkacat and use a grep to filter all message where there is a value of `:21`, i.e. we are only interested in driver `21`. 


```
docker exec -ti kafkacat kafkacat -b kafka-1 -t logisticsdb_driver | grep ":21"
```

we can see that there is one message in the topic for the driver with id `21`. 

```
docker@ubuntu:~$ docker exec -ti kafkacat kafkacat -b kafka-1 -t logisticsdb_driver | grep ":21"
{"id":21,"first_name":"Lila","last_name":"Page","available":"Y","birthdate":2651,"last_update":1598191309466}
```

In another terminal window (leave the kafkacat running as is), connect to Postgresql and perform the update of driver `21` and set `available` to `N`:

```
docker exec -ti postgresql psql -d demodb -U demo
SET search_path TO logistics_db;
UPDATE "driver" SET "available" = 'N', "last_update" = CURRENT_TIMESTAMP  WHERE "id" = 21;
```

in the kafkacat window you will now see a 2nd message for driver `21`:

```
docker@ubuntu:~$ docker exec -ti kafkacat kafkacat -b kafka-1 -t logisticsdb_driver | grep ":21"
{"id":21,"first_name":"Lila","last_name":"Page","available":"Y","birthdate":2651,"last_update":1598191309466}
{"id":21,"first_name":"Lila","last_name":"Page","available":"N","birthdate":2651,"last_update":1598191373828}
```

What does that mean for our Presto table? Let's see the result of a SELECT where `id` is `21`.

```
presto:logistics> SELECT *
               -> FROM logisticsdb_driver
               -> WHERE id = 21;
               ->
 kafka_key | id | first_name | last_name | available | birthdate |  last_update  | _partition_id | _partition_offset | _message_corrupt |                                                   _messag>
-----------+----+------------+-----------+-----------+-----------+---------------+---------------+-------------------+------------------+---------------------------------------------------------->
 21        | 21 | Lila       | Page      | Y         |      2651 | 1598186449022 |             4 |                 1 | false            | {"id":21,"first_name":"Lila","last_name":"Page","availabl>
 21        | 21 | Lila       | Page      | N         |      2651 | 1598186505945 |             4 |                 3 | false            | {"id":21,"first_name":"Lila","last_name":"Page","availabl>
(2 rows)
```

We can see that we also get two records back. This is a bit "unexpected", if we assume that `kafka_key`, which is equivalent to the `id`, is kind of a primary key. The reason for that behaviour is of course because there are two messages in the Kafka topic, one for the initial insert and one for the update. The Kafka topic is configured as a log compacted  topic, but this is done in the background after some time, so there is always a chance that we get multiple records for a given key. 

If we re-run the join to `truck_position` for only driver `21`

```
SELECT driver_id, first_name, last_name, event_type, nof
FROM (SELECT driver_id, event_type, count(*) AS nof
		FROM truck_position
		WHERE event_type != 'Normal'
		GROUP BY driver_id, event_type
		)		AS tp
LEFT JOIN logisticsdb_driver   AS d
ON tp.driver_id = d.id
WHERE d.id = 21;
```

we can see that this cause duplicates, due to the two rows returned for the `logisticsdb_driver` kafka table:

```
 driver_id | first_name | last_name |        event_type         | nof
-----------+------------+-----------+---------------------------+-----
        21 | Lila       | Page      | Lane Departure            |   6
        21 | Lila       | Page      | Lane Departure            |   6
        21 | Lila       | Page      | Unsafe following distance |  11
        21 | Lila       | Page      | Unsafe following distance |  11
        21 | Lila       | Page      | Overspeed                 |   7
        21 | Lila       | Page      | Overspeed                 |   7
        21 | Lila       | Page      | Unsafe tail distance      |   4
        21 | Lila       | Page      | Unsafe tail distance      |   4
```        

How can we avoid that? We have simulate the behaviour of log compaction in Presto, i.e. we should only return the newest message for each `kafka_key`. 
Presto supports many SQL functions, such as LAG and LEAD as well as LAST_VALUE. Using LAST_VALUE we return the newest `last_update` value for each key and these records we return.

```
SELECT * 
FROM logisticsdb_driver 
WHERE (last_update) IN (SELECT LAST_VALUE(last_update) OVER (PARTITION BY kafka_key 
											ORDER BY last_update 
											RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_update 
							FROM logisticsdb_driver);
```

This removes the older values and we can replace the join to the `logisticsdb_driver` table by this query:

```
SELECT driver_id, first_name, last_name, event_type, nof
FROM (SELECT driver_id, event_type, count(*) AS nof
		FROM truck_position
		WHERE event_type != 'Normal'
		GROUP BY driver_id, event_type
		)		AS tp
LEFT JOIN (
	SELECT * 
	FROM logisticsdb_driver 
	WHERE (last_update) IN (SELECT LAST_VALUE(last_update) OVER (PARTITION BY id 
												ORDER BY last_update 
												RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_update 
								FROM logisticsdb_driver)	) d						
ON tp.driver_id = d.id
```

Unfortunately the Kafka connector does not support views, otherwise some views could be used to simplify these statements.

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

------

## Demo 3 - Enrich Data

### Show driver table

```
docker exec -ti postgresql psql -d sample -U sample


SELECT * FROM driver;
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
