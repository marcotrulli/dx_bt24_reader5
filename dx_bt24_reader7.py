import asyncio
from bleak import BleakClient
from ewelink import EWeLink

# -------------------------
# CONFIGURAZIONE
# -------------------------
MAC_ADDRESS = "48:87:2D:6C:FB:0C"  # Arduino / sensore BLE
CHAR_UUID = "0000FFE1-0000-1000-8000-00805F9B34FB"

EW_EMAIL = "marcotrulli2006@gmail.com"
EW_PASSWORD = "Enrico22!"
DEVICE_ID = "10025fa57d"  # ID luce eWeLink

# -------------------------
# FUNZIONE PRINCIPALE
# -------------------------
async def main():
    # Stato luce interno (anti-spam cloud)
    stato_luce = None

    # Inizializza eWeLink (versione moderna)
    ew = EWeLink()
    await ew.login(email=EW_EMAIL, password=EW_PASSWORD)
    print("✅ Connesso a eWeLink")

    # Funzioni per accendere / spegnere la luce
    async def luce_on():
        await ew.set_device_status(DEVICE_ID, True)
        print("💡 Luce ACCESA")

    async def luce_off():
        await ew.set_device_status(DEVICE_ID, False)
        print("🌑 Luce SPENTA")

    # -------------------------
    # CALLBACK BLE
    # -------------------------
    async def callback(sender, data):
        nonlocal stato_luce  # necessario per modificare lo stato interno
        try:
            valore = int(data.decode().strip())
        except ValueError:
            print("⚠️ Dato non valido:", data)
            return

        print("Sensore:", valore)

        # Anti-spam: cambia solo se il valore è diverso
        if valore != stato_luce:
            stato_luce = valore
            if valore == 1:
                await luce_on()
            else:
                await luce_off()

    # -------------------------
    # CONNESSIONE AL BLE
    # -------------------------
    async with BleakClient(MAC_ADDRESS) as client:
        print("✅ Connesso al DX-BT24!")
        await client.start_notify(CHAR_UUID, callback)
        print("In ascolto dei dati... premi Ctrl+C per uscire")

        # Loop infinito
        while True:
            await asyncio.sleep(1)

# -------------------------
# RUN SCRIPT
# -------------------------
if __name__ == "__main__":
    asyncio.run(main())
