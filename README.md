# HeriSureAR25-FakeIoTHubIntegration

## Installation of dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install azure-iot-device
pip install paho-mqtt==2.1.0
```

## Configuration

Complete the config.ini file with your specific details for TTN and Azure connections

```ini
[ttn]
broker = eu1.cloud.thethings.network
username = your_app_id@ttn
access_key = your_access_key 
topic = v3/+/devices/#

[azure]
iothub_name = your_iothub_name
sas_token = SharedAccessSignature sig={signature-string}&se={expiry}&skn={policyName}&sr={URL-encoded-resourceURI}
iothub_device_conn = HostName={hostname};DeviceId={device-id};SharedAccessKey={shared-access-key}
```

## Executing script

```bash
python ttn_aziothub_sdk.py config/config.ini
```

## Sample execution 

This execution creates 3 instances of the script using PM2 and with different config files for each of the devices

```bash
pm2 start ttn_aziothub_sdk.py --name ttn_rak3172 --interpreter=/home/azureuser/mqtt/.venv/bin/python -- config/config_rak3172.ini
pm2 start ttn_aziothub_sdk.py --name ttn_dragino --interpreter=/home/azureuser/mqtt/.venv/bin/python -- config/config_dragino.ini
pm2 start ttn_aziothub_sdk.py --name ttn_milesight --interpreter=/home/azureuser/mqtt/.venv/bin/python -- config/config_milesight.ini
```