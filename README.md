## Synopsis

This is a project is for Tune's implementation engineer challenge. This app take's data from Tune's firehose platform and write it to a sqllite database. You can see sample injested data in `sample-data.json`

## Installation
1. Clone the repo
2. Add your own `.env` file with keys
  ```
  QUEUE_URL='your-sqs-url'
  AWS_REGION='your-aws-region'
  AWS_KEY='your-aws-key'
  AWS_SECRET='your-aws-secret'
  ```
 3. `pip install -r requirements.txt`
 4. `python read_queue.py`

## Technical Explanation

Tune firehose is an event delivery mechanism introduced as a premium feature for high-volume HasOffers clients, allowing push delivery of tracking and adjustment events to external event consumers. In order to handle the throughput of Tune firehose, I have constructed a highly performant,scalable app that will be able to write all these events to a sqlite database.

The system comprises of 3 parts.

1. The exposed endpoint that will receive all the event data from Tune's firehose and will push that event data to an SQS queue. This endpoint will be deployed on AWS lambda, giving us the scalability and speed required to handle all these events without having to build out the infrastructure. The code can be found in `feed_queue.py`

2. The Amazon SQS queue is our queuing service that will be able to feed event data to the series of microservices responsible for writing to a sqlitedb.

3. Microservices that will pull event data from the SQS queue and write to a sqlite database. These microservices can be deployed and scaled to as many instances as you would like. The code can be found at `read_queue.py`.


## Laymans explanation

In order to be able to store all of Tune firehose's data, we need to write it to a database. This will not only save the event data indefinitely, but it will give us the ability to easily analyse the data that comes from tune firehose. In order to perform this task, I have written an app that is able to take all of Tune firehose's data and write it to a database.


The app comprises of 3 parts.

1. The Tune data reader. This is the service that will receive data from Tune firehose and push it to a queue. This is extremely important as if we don't push to a queue, we will be vulnerable to high traffic crashing the server.
2. The queue. This is essentially just a service from Amazon that allows us to store data for a short time so that other services can have access to it
3. The database writer. This service will essentially just pull that event data that we have stored on Amazon and then write the data to the database.
