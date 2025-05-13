import pika
from .rabbitmq import get_connection

def send_event(exchange_name, routing_key, message):
    connection = get_connection()
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange_name, exchange_type='direct', durable=True)
    channel.basic_publish(
        exchange=exchange_name,
        routing_key=routing_key,
        body=message.encode('utf-8'),
        properties=pika.BasicProperties(
            delivery_mode=2  # Сделает сообщение постоянным
        )
    )
    print(f" [x] Sent {routing_key}:{message}")
    connection.close()