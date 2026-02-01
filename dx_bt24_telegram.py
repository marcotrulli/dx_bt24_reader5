import asyncio
from bleak import BleakClient
import requests

# -------------------------
# CONFIGURAZIONE
# -------------------------
MAC_ADDRESS = "48:87:2D:6C:FB:0C"  # Arduino / sensore BLE
CHAR_UUID = "0000FFE1-0000-1000-8000-00805F9B34FB"

TELEGRAM_TOKEN = "8270696186:AAEHRIPXbWpc_MnZ9kjMTmPDE2XO85Kbud0"
CHAT_ID = 123456789  # sostituisci con il tuo chat ID personale

# -------------------------
# FUNZIONE PRINCIPALE
# -------------------------
async def main():
    stato_sensore = None

    async def callback(sender, data):
        nonlocal stato_sensore
        try:
            valore = int(data.decode().strip())
        except ValueError:
            print("⚠️ Dato non valido:", data)
            return

        if valore != stato_sensore:
            stato_sensore = valore
            testo = "💡 Sensore attivato!" if valore == 1 else "🌑 Sensore spento"
            # invio messaggio a Telegram
            requests.get(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                params={"chat_id": CHAT_ID, "text": testo}
            )
            print("Messaggio inviato a Telegram:", testo)

    # -------------------------
    # CONNESSIONE AL BLE
    # -------------------------
    async with BleakClient(MAC_ADDRESS) as client:
        print("✅ Connesso al DX-BT24!")
        await client.start_notify(CHAR_UUID, callback)
        print("In ascolto dei dati... premi Ctrl+C per uscire")

        while True:
            await asyncio.sleep(1)

# -------------------------
# RUN SCRIPT
# -------------------------
if __name__ == "__main__":
    asyncio.run(main())
