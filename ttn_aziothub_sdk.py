# File: ttn_aziothub_pubsub.py
# Author: Raul Ceron
# MQTT temperature and humidity pubsub for TTN Network Server.

import sys
import time
import uuid
import json
import configparser
from datetime import datetime
import paho.mqtt.client as mqtt
from azure.iot.device import IoTHubDeviceClient, Message

# Configuration
config = configparser.ConfigParser()
config.read(sys.argv[1] if len(sys.argv) == 2 else "config.ini")

ttn_config = config["ttn"]
TTN_BROKER = ttn_config.get("broker", "eu1.cloud.thethings.network")
TTN_TOPIC = ttn_config.get("topic")
TTN_USERNAME = ttn_config.get("username")
TTN_ACCESS_KEY = ttn_config.get("access_key")

az_config = config["azure"]
# The client object is used to interact with your Azure IoT hub.
IOTHUB_DEVICE_CONN_STRING = az_config.get("iothub_device_conn")
az_client = IoTHubDeviceClient.create_from_connection_string(IOTHUB_DEVICE_CONN_STRING)

# Connect the client.
az_client.connect()


def on_connect_ttn(client, userdata, flags, rc, properties=None):
    if rc != 0:
        print(f"{datetime.now()} - TTN Connection failed with reason code: {rc}")
        return
    print(f"{datetime.now()} - TTN Connected successfully")
    client.subscribe(TTN_TOPIC, qos=1)


def on_message_ttn(client, userdata, msg):
    try:
        payload = json.loads(msg.payload)

        device_id = payload["end_device_ids"]["device_id"]
        application_id = payload["end_device_ids"]["application_ids"]["application_id"]

        temperature = (
            payload["uplink_message"]["decoded_payload"].get("temperature")
            or payload["uplink_message"]["decoded_payload"].get("TempC_SHT31")
            or payload["uplink_message"]["decoded_payload"].get("temperature_1")
        )

        humidity = (
            payload["uplink_message"]["decoded_payload"].get("humidity")
            or payload["uplink_message"]["decoded_payload"].get("Hum_SHT31")
            or payload["uplink_message"]["decoded_payload"].get("relative_humidity_1")
        )

        if temperature is not None and humidity is not None:
            res = {
                "device_id": device_id,
                "application_id": application_id,
                "received_at": payload["received_at"],
                "temperature": temperature,
                "humidity": humidity,
            }

            print(res)

            msg = Message(json.dumps(res))
            msg.message_id = uuid.uuid4()
            msg.content_encoding = "utf-8"
            msg.content_type = "application/json"
            az_client.send_message(msg)
            time.sleep(1)

        else:
            print(f"{datetime.now()} - Temperature or humidity data missing.")

    except (json.JSONDecodeError, KeyError) as e:
        print(f"{datetime.now()} - Error processing message: {e}")


def main():

    if not TTN_USERNAME or not TTN_ACCESS_KEY or not IOTHUB_DEVICE_CONN_STRING:
        print(f"{datetime.now()} - Error: Missing required configuration parameters.")
        sys.exit(1)

    client_ttn = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id="",
        clean_session=True,
        userdata=None,
        protocol=mqtt.MQTTv311,
        transport="tcp",
    )

    client_ttn.username_pw_set(username=TTN_USERNAME, password=TTN_ACCESS_KEY)
    client_ttn.on_connect = on_connect_ttn
    client_ttn.on_message = on_message_ttn

    try:
        client_ttn.connect(TTN_BROKER, port=1883, keepalive=60)
        client_ttn.loop_forever()

    except Exception as e:
        print(f"{datetime.now()} - TTN Connection error: {e}")


if __name__ == "__main__":
    main()
