import asyncio
import requests
import time
from bleak import BleakClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# -------------------------
# CONFIGURAZIONE
# -------------------------
MAC_ADDRESS = "48:87:2D:6C:FB:0C"  # indirizzo BLE sensore
CHAR_UUID = "0000FFE1-0000-1000-8000-00805F9B34FB"

TELEGRAM_TOKEN = "8270696186:AAEHRIPXbWpc_MnZ9kjMTmPDE2XO85Kbud0"
CHAT_ID = 123456789  # il tuo chat ID

EMAIL = "marcotrulli2006@gmail.com"
PASSWORD = "Enrico22!"
DEVICE_NAME = "Luce Camera Marco"

DEVICE_STATE = 0  # 0=spenta, 1=accesa

# -------------------------
# FUNZIONI TELEGRAM
# -------------------------
def send_telegram_message(testo):
    requests.get(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        params={"chat_id": CHAT_ID, "text": testo}
    )

def click_ewelink():
    # Configura Chromium headless
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    try:
        # Login
        driver.get("https://eu-ewelink.com/login")
        time.sleep(3)
        driver.find_element(By.NAME, "email").send_keys(EMAIL)
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        driver.find_element(By.XPATH, "//button[contains(text(),'Log In')]").click()
        time.sleep(5)

        # Clicca pulsante luce
        device_button = driver.find_element(By.XPATH, f"//div[contains(text(), '{DEVICE_NAME}')]/ancestor::div[contains(@class,'device-card')]//button")
        device_button.click()
        print(f"✅ Pulsante {DEVICE_NAME} cliccato!")
    except Exception as e:
        print("❌ Errore:", e)
    finally:
        time.sleep(2)
        driver.quit()

def check_telegram_commands():
    global DEVICE_STATE
    res = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates")
    data = res.json()
    for update in data.get("result", []):
        text = update.get("message", {}).get("text", "")
        chat_id = update.get("message", {}).get("chat", {}).get("id")
        if chat_id != CHAT_ID:
            continue

        if text.lower() == "/on" and DEVICE_STATE != 1:
            DEVICE_STATE = 1
            click_ewelink()
            send_telegram_message("💡 Luce ACCESA via Telegram")

        elif text.lower() == "/off" and DEVICE_STATE != 0:
            DEVICE_STATE = 0
            click_ewelink()
            send_telegram_message("🌑 Luce SPENTA via Telegram")

# -------------------------
# CALLBACK BLE
# -------------------------
async def ble_callback(sender, data):
    global DEVICE_STATE
    try:
        valore = int(data.decode().strip())
    except ValueError:
        print("Dato non valido:", data)
        return

    if valore != DEVICE_STATE:
        DEVICE_STATE = valore
        click_ewelink()
        testo = "💡 Sensore attivato → luce ACCESA" if valore == 1 else "🌑 Sensore spento → luce SPENTA"
        send_telegram_message(testo)
        print("Messaggio Telegram:", testo)

# -------------------------
# LOOP PRINCIPALE
# -------------------------
async def main():
    async with BleakClient(MAC_ADDRESS) as client:
        print("✅ Connesso al sensore BLE!")
        await client.start_notify(CHAR_UUID, ble_callback)
        print("In ascolto BLE e comandi Telegram...")
        while True:
            check_telegram_commands()
            await asyncio.sleep(2)

# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Programma terminato dall'utente")
