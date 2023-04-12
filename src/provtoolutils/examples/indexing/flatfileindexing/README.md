# Flatfileindexing

This example demonstrates a simple service, which could serve files based on queries over the provenance of each provenance container. Such a functionality would normally be delivered by a full blown data management system.

## BoM

|Library|
|---|
|ch.qos.logback|
|com.googlecode.json-simple|
|com.graphql-java|
|io.micronaut|
|io.micronaut.test|
|jakarta.annotation|
|org.junit.jupiter|
|org.mockito|

## Debugging

mvn mn:run -Dmn.debug=true -Dmn.debug.suspend

## Debugging tests

mvn -Dmaven.surefire.debug test

## Usage

curl -X POST -H "Content-Type:application/json" -d '{data{entity(label: "testfile1.txt"){label}}}' http://localhost:8080/search

## Tests

mvn test org.pitest:pitest-maven:mutationCoverage

## Build

A recent JDK (17+) and Maven is needed to build. Go to the directory with the flatfileindexing pom.xml inside and run:

```
mvn package
```

This will create a fat jar with batteries included.

## Develop

Run in development mode with:

```
./mvnw mn:run -Dmn.appArgs="-flatfileindexing.watchdir=<full path to src/main/resources/testdata>"
```

## Run

```
java -jar flatfileindexing-<version>.jar
```

## Usage within container

The following Dockerfile can be used:

```
FROM alpine:3.16

RUN apk add openjdk17-jre-headless maven
```

Run it with:

```
docker run --rm -it -v $PWD:/app/:ro -v <your data directory>:/data:ro -p <host port>:8080 <image name> /bin/sh
```

Within the image, build and start the container:

```
cd /app
mvn package
java -jar target/flatfileindexing-<version>.jar flatfileindexing.watchdir=/data
```

Use curl or any other tool to perform the query (see above).
