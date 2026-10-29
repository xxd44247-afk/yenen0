import os
import sys
import asyncio
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
import discord

# =====================================================================
# 🌍 RENDER / UPTIME ROBOT İÇİN ARKA PLAN WEB SUNUCUSU
# =====================================================================
def run_dummy_server():
    port = int(os.getenv("PORT", "10000"))
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    print(f"🌍 Web sunucusu aktif: {port}")
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# =====================================================================
# 🤖 SELF-BOT - 3 SANİYEDE BİR MESAJ GÖNDERME
# =====================================================================

TOKEN = os.getenv("SELF_TOKEN")
KANAL_STR = os.getenv("MESAJ_KANAL_ID", "")   # Mesajların gideceği kanal

if not TOKEN:
    sys.exit("❌ HATA: SELF_TOKEN eksik!")
if not KANAL_STR.isdigit():
    sys.exit("❌ HATA: MESAJ_KANAL_ID hatalı veya eksik!")

MESAJ_KANAL_ID = int(KANAL_STR)

client = discord.Client()

def mesajlari_yukle():
    """mesajlar.txt dosyasını okur"""
    try:
        with open("mesajlar.txt", "r", encoding="utf-8") as f:
            mesajlar = [satir.strip() for satir in f.readlines() if satir.strip()]
        if not mesajlar:
            print("❌ mesajlar.txt boş!")
            return []
        print(f"✅ {len(mesajlar)} adet mesaj yüklendi.")
        return mesajlar
    except FileNotFoundError:
        print("❌ mesajlar.txt bulunamadı!")
        return []

async def mesaj_gonderme_dongusu():
    await client.wait_until_ready()

    kanal = client.get_channel(MESAJ_KANAL_ID)
    if kanal is None:
        try:
            kanal = await client.fetch_channel(MESAJ_KANAL_ID)
        except Exception as e:
            print(f"❌ Kanal alınamadı: {e}")
            return

    mesajlar = mesajlari_yukle()
    if not mesajlar:
        return

    index = 0
    print(f"🚀 Mesaj gönderme başladı → Kanal: {MESAJ_KANAL_ID}")

    while not client.is_closed():
        try:
            mesaj = mesajlar[index]
            await kanal.send(mesaj)
            print(f"📤 Gönderildi ({index + 1}/{len(mesajlar)}): {mesaj[:50]}...")

            index = (index + 1) % len(mesajlar)  # Sona gelince başa dön
            await asyncio.sleep(3)  # 3 saniye bekle

        except Exception as e:
            print(f"❌ Mesaj gönderme hatası: {e}")
            await asyncio.sleep(5)

@client.event
async def on_ready():
    print("=========================================")
    print(f"🤖 Bağlantı başarılı: {client.user}")
    print(f"📢 Mesaj kanalı: {MESAJ_KANAL_ID}")
    print("=========================================")
    # Mesaj gönderme döngüsünü başlat
    client.loop.create_task(mesaj_gonderme_dongusu())

client.run(TOKEN)
