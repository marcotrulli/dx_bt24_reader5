import asyncio
from bleak import BleakClient
import requests

# =========================
# CONFIGURAZIONE
# =========================

MAC_ADDRESS = "48:87:2D:6C:FB:0C"   # MAC del sensore BLE
CHAR_UUID = "0000FFE1-0000-1000-8000-00805F9B34FB"

TELEGRAM_TOKEN = "8270696186:AAEHRIPXbWpc_MnZ9kjMTmPDE2XO85Kbud0"
CHAT_ID = 7178902327

SOGLIA_DISTANZA = 50.0   # cm

# Stato interno
presenza_attiva = False

# =========================
# TELEGRAM
# =========================

def send_telegram_message(testo):
    try:
        r = requests.get(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            params={
                "chat_id": CHAT_ID,
                "text": testo
            },
            timeout=5
        )
        print("📨 Telegram:", r.status_code, r.text)
    except Exception as e:
        print("❌ Errore Telegram:", e)

# =========================
# CALLBACK BLE
# =========================

async def ble_callback(sender, data):
    global presenza_attiva

    try:
        testo = data.decode().strip()       # "DISTANZA:52.62"
        distanza = float(testo.split(":")[1])
    except Exception:
        print("⚠️ Dato non valido:", data)
        return

    print(f"📏 Distanza: {distanza:.2f} cm")

    if distanza < SOGLIA_DISTANZA and not presenza_attiva:
        presenza_attiva = True
        print("🚶 Presenza rilevata")
        send_telegram_message("🚨 Qualcuno è entrato nella stanza!")

    elif distanza >= SOGLIA_DISTANZA and presenza_attiva:
        presenza_attiva = False
        print("✅ Area libera")

# =========================
# MAIN LOOP
# =========================

async def main():
    async with BleakClient(MAC_ADDRESS) as client:
        print("🔵 Connesso al sensore BLE")
        await client.start_notify(CHAR_UUID, ble_callback)

        print("👂 In ascolto dei dati...")
        while True:
            await asyncio.sleep(1)

# =========================
# AVVIO
# =========================

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("⛔ Script interrotto")
