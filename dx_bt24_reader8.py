import asyncio
from bleak import BleakClient
from ewelink import EWeLink, EWeLinkUser, EWeLinkApp

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
    stato_luce = None  # anti-spam

    # -------------------------
    # Connessione eWeLink (cloud)
    # -------------------------
    user_cred = EWeLinkUser(email=EW_EMAIL, password=EW_PASSWORD)
    app_cred = EWeLinkApp()  # valori di default dell'app
    ew = EWeLink(user_cred=user_cred, app_cred=app_cred)
    await ew.login()
    print("✅ Connesso a eWeLink cloud")

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
        nonlocal stato_luce
        try:
            valore = int(data.decode().strip())
        except ValueError:
            print("⚠️ Dato non valido:", data)
            return

        print("Sensore:", valore)

        # Cambia stato solo se diverso
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
        while True:
            await asyncio.sleep(1)

# -------------------------
# RUN SCRIPT
# -------------------------
if __name__ == "__main__":
    asyncio.run(main())
