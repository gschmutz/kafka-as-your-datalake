# Kafka as your Data Lake - is it feasible?

This project describes the setup and execution of the demo for the Kafka Summit 2020 presentation [Kafka as your Data Lake - is it feasible?](https://www.slideshare.net/gschmutz/kafka-as-your-data-lake-is-it-feasible). 

![Alt Image Text](./images/kafka-as-your-datalake.png "Kafka as your Data Lake")

The demos are all based on a containerised platform which can easily be provisioned using Docker Compose. 

 * [Preparation](0-Preparation.md) - describes how to setup the platform as well as the necessary artefacts, such as Postgresql Schema and Table, Kafka Topics and a data stream of simulated "live" data 
 * [Demo 1 - Streaming Data Lake](1-Demo-ksqlDB.md) - shows how to use ksqlDB to create a "real-time" Delta Lake
 * [Demo 2 - Batch Processing with Spark](2-Demo-Spark.md) - shows how to use Spark to use Batch Processing to access data in one or more Kafka topics
 * [Demo 3 - Batch Query with Presto](3-Demo-Presto.md) - show how to use Presto to use SQL Queries to access one or more Kafka topics

