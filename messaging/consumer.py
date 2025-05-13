from .rabbitmq import get_connection

def callback(ch, method, properties, body):
    print(f"\n[🐾 Pet Event Received]")
    print(f"📬 Routing Key: {method.routing_key}")
    print(f"📨 Message: {body.decode()}")

def start_consumer():
    connection = get_connection()
    channel = connection.channel()

    queue_name = 'queue.group3.21'
    exchange_name = 'group3.21.direct'
    routing_key = 'group3.21.routing.key'

    channel.exchange_declare(exchange=exchange_name, exchange_type='direct', durable=True)
    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()