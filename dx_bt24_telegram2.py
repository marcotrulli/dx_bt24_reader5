import asyncio
from bleak import BleakClient
import requests
import paho.mqtt.client as mqtt

# -------------------------
# CONFIGURAZIONE
# -------------------------
MAC_ADDRESS = "48:87:2D:6C:FB:0C"  # indirizzo BLE del sensore
CHAR_UUID = "0000FFE1-0000-1000-8000-00805F9B34FB"

TELEGRAM_TOKEN = "8270696186:AAEHRIPXbWpc_MnZ9kjMTmPDE2XO85Kbud0"
CHAT_ID = 123456789  # tuo chat ID

MQTT_BROKER = "127.0.0.1"   # broker Mosquitto locale
MQTT_PORT = 1883
MQTT_TOPIC = "sonoff/sonoff01/cmnd/POWER"  # topic Tasmota della luce

DEVICE_STATE = 0  # 0=spenta, 1=accesa

# -------------------------
# CLIENT MQTT
# -------------------------
mqtt_client = mqtt.Client()
try:
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()
    print("✅ Connesso al broker MQTT")
except Exception as e:
    print("❌ Errore connessione MQTT:", e)

# -------------------------
# FUNZIONI TELEGRAM
# -------------------------
def send_telegram_message(testo):
    try:
        requests.get(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            params={"chat_id": CHAT_ID, "text": testo},
            timeout=5
        )
    except Exception as e:
        print("❌ Errore invio Telegram:", e)

def check_telegram_commands():
    global DEVICE_STATE
    try:
        res = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates", timeout=5)
        data = res.json()
    except Exception as e:
        print("❌ Errore lettura comandi Telegram:", e)
        return

    for update in data.get("result", []):
        text = update.get("message", {}).get("text", "")
        chat_id = update.get("message", {}).get("chat", {}).get("id")
        if chat_id != CHAT_ID:
            continue

        if text.lower() == "/on" and DEVICE_STATE != 1:
            DEVICE_STATE = 1
            mqtt_client.publish(MQTT_TOPIC, "ON")
            send_telegram_message("💡 Luce ACCESA via Telegram")

        elif text.lower() == "/off" and DEVICE_STATE != 0:
            DEVICE_STATE = 0
            mqtt_client.publish(MQTT_TOPIC, "OFF")
            send_telegram_message("🌑 Luce SPENTA via Telegram")

# -------------------------
# CALLBACK BLE
# -------------------------
async def ble_callback(sender, data):
    global DEVICE_STATE
    try:
        valore = int(data.decode().strip())
    except ValueError:
        print("Dato BLE non valido:", data)
        return

    if valore != DEVICE_STATE:
        DEVICE_STATE = valore
        if valore == 1:
            mqtt_client.publish(MQTT_TOPIC, "ON")
            testo = "💡 Sensore attivato → luce ACCESA"
        else:
            mqtt_client.publish(MQTT_TOPIC, "OFF")
            testo = "🌑 Sensore spento → luce SPENTA"
        send_telegram_message(testo)
        print("Messaggio Telegram:", testo)

# -------------------------
# LOOP PRINCIPALE
# -------------------------
async def main():
    async with BleakClient(MAC_ADDRESS) as client:
        print("✅ Connesso al sensore BLE")
        await client.start_notify(CHAR_UUID, ble_callback)
        print("In ascolto BLE e comandi Telegram...")

        while True:
            check_telegram_commands()
            await asyncio.sleep(2)

# -------------------------
# RUN SCRIPT
# -------------------------
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        print("🔌 Script interrotto")
