# Kafka as your Data Lake - is it feasible?

## Preparation

The platform where the demos can be run on, has been generated using the [`platys`](http://github.com/trivadispf/platys)  toolset using the [`platys-modern-data-platform`](http://github.com/trivadispf/platys-modern-data-platform) stack.

The generated artefacts are available in the `./docker` folder.

The prerequisites for running the platform are 
 
 * Docker 
 * Docker Compose. 

### Start the platform using Docker Compose

First create the following two environment variables, which export the Public IP address (if a cloud environment) and the Docker Engine (Docker Host)  IP address:

``` bash
export DOCKER_HOST_IP=<docker-host-ip>
export PUBLIC_IP=<public-host-ip>
```

It is very important that these two are set, otherwise the platform will not run properly.

Now navigate into the `docker` folder and start `docker-compose`.

``` bash
cd ./docker

docker-compose up -d
```

### Create Kafka Topics

Using the `kafka-topics` CLI inside the `kafka-1` docker container create the different Kafka topics:

``` bash
docker exec -it kafka-1 kafka-topics --bootstrap-server kafka-1:19092 --create --topic truck_position --partitions 8 --replication-factor 3

docker exec -it kafka-1 kafka-topics --bootstrap-server kafka-1:19092 --create --topic dangerous_driving_ksql --partitions 8 --replication-factor 3

docker exec -it kafka-1 kafka-topics --bootstrap-server kafka-1:19092 --create --topic dangerous_driving_and_driver_ksql --partitions 8 --replication-factor 3

docker exec -it kafka-1 kafka-topics --bootstrap-server kafka-1:19092 --create --topic logisticsdb_driver --partitions 8 --replication-factor 3 --config cleanup.policy=compact --config segment.ms=100 --config delete.retention.ms=100 --config min.cleanable.dirty.ratio=0.001
```

### Setup logistics_db Postgresql Database

Let's create the `driver` table in Postgresql.

``` bash
docker exec -ti postgresql psql -d demodb -U demo
```

Check for the `driver` table

``` sql
SELECT * FROM logistics_db.driver;
```

### Using CDC to move Postgresql driver table to Kafka topic

We will use the Kafka Connect JDBC connector to move the data from the `driver` Postgresql table to `logisticsdb_driver` Kafka topic with the same name.

``` bash
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

Check that all the data is successfully appended to the `logisticsdb_driver` topic using the `kcat` cli:

``` bash
docker exec -ti kcat kcat -b kafka-1:19092 -t logisticsdb_driver
```

### Create a stream of Vehicle Tracking Information

Open two terminals windows.

In the 1st window, run IoT Truck simulator and produce messages to the `truck_position` Kafka topic:

``` bash
docker run --network kafka-as-datalake-platform trivadis/iot-truck-simulator '-s' 'KAFKA' '-h' 'kafka-1' '-p' '19092' '-f' 'JSON'
```

In the 2nd window, start a `kcat` consumer to see the messages:

``` bash
docker exec -ti kcat kcat -b kafka-1:19092 -t truck_position
```

