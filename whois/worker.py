import os
import logging

import pika

from datetime import datetime
from whois.database import db, Device

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=os.environ["MQ_HOST"])
)
channel = connection.channel()


result = channel.queue_declare(queue="whohacks", exclusive=False)
queue_name = result.method.queue

channel.queue_bind(exchange=os.environ["MQ_EXCHANGE"], queue=queue_name, routing_key="")

logger.info(" [*] Waiting for logs. To exit press CTRL+C")


def callback(ch, method, properties, body):
    logger.info(" [x] %r:%r" % (method.routing_key, body))
    Device.update_or_create(mac_address=body.decode().upper(), last_seen=datetime.now())


channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()
