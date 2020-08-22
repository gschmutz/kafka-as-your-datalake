import time
from confluent_kafka import Producer

p = Producer({'bootstrap.servers': 'localhost:29092'})
messages = ["message1","message2","message3", "message4", "message5"]

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

for data in messages:
	# Trigger any available delivery report callbacks from previous produce() calls
	p.poll(0)

	if data.encode('utf-8') == 'message2':
		microseconds_since_epoc = milliseconds = int((time.time() - 60) * 1000) 
	else:
		microseconds_since_epoc = milliseconds = int((time.time() - 0) * 1000) 
	p.produce('timestamp_test_topic', data.encode('utf-8'), callback=delivery_report, timestamp=microseconds_since_epoc)

	# Wait for any outstanding messages to be delivered and delivery report
	# callbacks to be triggered.
	time.sleep(2.5)
	p.flush()
