import asyncio
from bleak import BleakClient
import requests
import time

# -------------------------
# CONFIGURAZIONE
# -------------------------
MAC_ADDRESS = "48:87:2D:6C:FB:0C"   # indirizzo BLE del tuo sensore
CHAR_UUID = "0000FFE1-0000-1000-8000-00805F9B34FB"

TELEGRAM_TOKEN = "8270696186:AAEHRIPXbWpc_MnZ9kjMTmPDE2XO85Kbud0"
CHAT_ID = 123456789  # sostituisci col tuo chat ID

# -------------------------
# FUNZIONE TELEGRAM
# -------------------------
def send_telegram_message(testo):
    requests.get(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        params={"chat_id": CHAT_ID, "text": testo}
    )

# -------------------------
# STATO SENSORE
# -------------------------
sensor_active = False  # True se qualcuno è sotto il sensore

# -------------------------
# CALLBACK BLE
# -------------------------
async def ble_callback(sender, data):
    global sensor_active
    try:
        valore = int(data.decode().strip())
    except ValueError:
        print("Dato non valido:", data)
        return

    if valore == 1 and not sensor_active:
        # movimento rilevato e prima non c'era
        sensor_active = True
        testo = "🚶 Qualcuno è entrato nella stanza!"
        send_telegram_message(testo)
        print(time.strftime("%H:%M:%S"), testo)
    elif valore == 0 and sensor_active:
        # movimento finito
        sensor_active = False
        print(time.strftime("%H:%M:%S"), "✅ Sensore tornato inattivo")

# -------------------------
# LOOP PRINCIPALE
# -------------------------
async def main():
    async with BleakClient(MAC_ADDRESS) as client:
        print("✅ Connesso al sensore BLE!")
        await client.start_notify(CHAR_UUID, ble_callback)
        print("In ascolto del sensore...")
        while True:
            await asyncio.sleep(1)

# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Programma terminato dall'utente")
