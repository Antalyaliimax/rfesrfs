import discord
from discord import app_commands, ui
from discord.ext import commands
import random
import asyncio
import os

import certifi
os.environ["SSL_CERT_FILE"] = certifi.where()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='a!', intents=intents)

# Bot sadece belirtilen sunucu ve kanalda çalışacak
GUILD_ID = 1268293263190917414
NORMAL_CHANNEL_ID = 1272988205230330016
VIP_CHANNEL_ID = 1272988336453189653
BOOST_CHANNEL_ID = 1273002819527643188


# Admin ID
ADMIN_ID = 1127352052192903259

# Dosya adları
NORMAL_ACCOUNTS_FILE = 'normalhesaplar.txt'
VIP_ACCOUNTS_FILE = 'viphesaplar.txt'
BOOST_ACCOUNTS_FILE = 'boosthesaplar.txt'


# Komut bekleme süreleri
NORMAL_COOLDOWN = 3600  # 60 dakika
VIP_COOLDOWN = 3600  # 60 dakika
BOOST_COOLDOWN = 3600  # 60 dakika


# Cooldownları tutacak dict'ler
normal_cooldowns = {}
vip_cooldowns = {}
boost_cooldowns = {}

# Rol isimleri
VIP_ROLE_NAME = 'Vip Gen'
VERIFIED_ROLE_NAME = 'ücretsiz gen'

async def remove_cooldown(user_id, is_vip, is_boost=False):
    await asyncio.sleep(BOOST_COOLDOWN if is_boost else (VIP_COOLDOWN if is_vip else NORMAL_COOLDOWN))
    if is_boost:
        boost_cooldowns.pop(user_id, None)
    elif is_vip:
        vip_cooldowns.pop(user_id, None)
    else:
        normal_cooldowns.pop(user_id, None)

async def send_account(interaction: discord.Interaction, file_name, is_vip=False, is_boost=False):
    user_id = interaction.user.id
    channel_id = interaction.channel.id

    # Role and channel checks
    if is_vip:
        if VIP_ROLE_NAME not in [role.name for role in interaction.user.roles] and user_id != ADMIN_ID:
            embed = discord.Embed( description="Bu komutu kullanmak için Premium Gen Rolüne Sahip Olmalısınız!", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        if channel_id != VIP_CHANNEL_ID:
            embed = discord.Embed( description="Bu komut yalnızca VIP kanalda kullanılabilir!", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
    elif is_boost:
        if channel_id != BOOST_CHANNEL_ID:
            embed = discord.Embed( description="Bu komut yalnızca Boost kanalda kullanılabilir!", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
    else:
        if VERIFIED_ROLE_NAME not in [role.name for role in interaction.user.roles] and user_id != ADMIN_ID:
            embed = discord.Embed( description="Bu komutu kullanmak için Ücretsiz Rolüne Sahip Olmalısınız!", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        if channel_id != NORMAL_CHANNEL_ID:
            embed = discord.Embed( description="Bu komut yalnızca Normal kanalda kullanılabilir!", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

    # Cooldown checks
    if is_vip and user_id in vip_cooldowns:
        embed = discord.Embed( description="Bu komutu tekrar kullanabilmek için beklemeniz gerekiyor.", color=discord.Color.orange())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    if is_boost and user_id in boost_cooldowns:
        embed = discord.Embed( description="Bu komutu tekrar kullanabilmek için beklemeniz gerekiyor.", color=discord.Color.orange())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    if not is_vip and not is_boost and user_id in normal_cooldowns:
        embed = discord.Embed( description="Bu komutu tekrar kullanabilmek için beklemeniz gerekiyor.", color=discord.Color.orange())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    try:
        with open(file_name, 'r') as file:
            accounts = file.readlines()

        if not accounts:
            embed = discord.Embed( description="Stokta Valorant Kalmadı! Adminler Bilgilendirildi!", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        accounts = [account.strip() for account in accounts if account.strip() != '']

        if not accounts:
            embed = discord.Embed( description="Stokta Valorant Kalmadı! Adminler Bilgilendirildi!", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        selected_account = random.choice(accounts)
        accounts.remove(selected_account)

        with open(file_name, 'w') as file:
            file.writelines([account + '\n' for account in accounts])

        async def send_account_button_callback(interaction: discord.Interaction):
            print("butona basıldı")

        button = ui.Button(label="Gen", style=discord.ButtonStyle.red)
        button.callback = send_account_button_callback
        view = ui.View()
        view.add_item(button)

        embed = discord.Embed( description=f"📦 Kalan Stok --> {len(accounts)}\n <:onay:1276546390620639375> Hesap Başarıyla DM'den İletildi!", color=discord.Color.purple ())
        await interaction.response.send_message(embed=embed, view=view)
        await interaction.user.send(f"Hesabınız: {selected_account}")

        if is_boost:
            boost_cooldowns[user_id] = True
        elif is_vip:
            vip_cooldowns[user_id] = True
        else:
            normal_cooldowns[user_id] = True

        bot.loop.create_task(remove_cooldown(user_id, is_vip, is_boost))

    except FileNotFoundError:
        embed = discord.Embed( description="Hesap dosyası bulunamadı.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        print(f"{file_name} bulunamadı.")  # Hata ayıklama mesajı

@bot.tree.command(name="gen", description="Valorant hesabı almak için kullanın.")
@app_commands.describe(type="Hesap tipi: premium, boost, free")
async def gen(interaction: discord.Interaction, type: str):
    if type == 'premium':
        await send_account(interaction, VIP_ACCOUNTS_FILE, is_vip=True)
    elif type == 'boost':
        await send_account(interaction, BOOST_ACCOUNTS_FILE, is_boost=True)
    elif type == 'free':
        await send_account(interaction, NORMAL_ACCOUNTS_FILE)
    else:
        embed = discord.Embed( description="Geçersiz hesap tipi. Lütfen 'premium', 'boost' veya 'free' girin.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name = "stokekle", description="Yeni hesaplar eklemek için kullanın.")
@app_commands.describe(type="Hesap tipi: premium, boost, free")
async def stokekle(interaction: discord.Interaction, type: str):
    if interaction.user.id == ADMIN_ID:
        if len(interaction.attachments)!= 1:
            embed = discord.Embed( description="Lütfen bir dosya ekleyin.", color=discord.Color.orange())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        file = interaction.attachments[0]
        if file.filename.endswith('.txt'):
            content = await file.read()
            content = content.decode('utf-8').strip()

            if type.lower() == 'premium':
                with open(VIP_ACCOUNTS_FILE, 'a') as f:
                    f.write('\n' + content)
            elif type.lower() == 'boost':
                with open(BOOST_ACCOUNTS_FILE, 'a') as f:
                    f.write('\n' + content)
            else:
                with open(NORMAL_ACCOUNTS_FILE, 'a') as f:
                    f.write('\n' + content)

            embed = discord.Embed( description="Stok başarıyla eklendi.", color=discord.Color.green())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed( description="Lütfen sadece .txt dosyaları ekleyin.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed( description="Bu komutu yalnızca admin kullanabilir.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="stoksil", description="Mevcut stokları silmek için kullanın.")
@app_commands.describe(type="Hesap tipi: premium, boost, free")
async def stoksil(interaction: discord.Interaction, type: str):
    if interaction.user.id == ADMIN_ID:
        if type.lower() == 'premium':
            open(VIP_ACCOUNTS_FILE, 'w').close()
            embed = discord.Embed( description="Premium stok dosyası başarıyla temizlendi.", color=discord.Color.green())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        elif type.lower() == 'boost':
            open(BOOST_ACCOUNTS_FILE, 'w').close()
            embed = discord.Embed( description="Boost stok dosyası başarıyla temizlendi.", color=discord.Color.green())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            open(NORMAL_ACCOUNTS_FILE, 'w').close()
            embed = discord.Embed( description="Normal stok dosyası başarıyla temizlendi.", color=discord.Color.green())
            await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed( description="Bu komutu yalnızca admin kullanabilir.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.event
async def on_ready():
    print(f'{bot.user} olarak giriş yapıldı.')
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} slash command(s) synced.")
    except Exception as e:
        print(e)

bot.run('MTI3NjUyOTAyODQ1NDQyMDU1NQ.Gv1S1W.OjLJe2FlZUmSdqHQFL4v45XB9XeWghbysRn9yM')
