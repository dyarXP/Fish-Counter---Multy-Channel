import discord, re, pytz, time, os, random
from discord.ext import commands

# ================= CONFIG =================
TOKEN = "MTQyODQyOTU5Nzk2MzE5NDQ5MA.GJWLz8.GsDzIf1lrhHD6gjj3Z2RL-cQiwzvMisTNGCO4c"  # Ganti dengan token botmu
CHANNEL_IDS = [
    1431084067943747584,  # Ganti dengan channel ID
]

# ================= INTENTS =================
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ================= TIMEZONE =================
TZ_JAKARTA = pytz.timezone("Asia/Jakarta")

# ================= WARNA TERMINAL =================
COLORS = {
    "END": "\033[0m",
    "RED": "\033[91m",
    "YELLOW": "\033[93m",
    "GREEN": "\033[92m",
    "CYAN": "\033[96m",
    "BLUE": "\033[94m",
    "MAGENTA": "\033[95m",
    "WHITE": "\033[97m",
}

RARITY_COLORS = {
    "Uncommon": COLORS["GREEN"],
    "Rare": COLORS["BLUE"],
    "Epic": COLORS["MAGENTA"],
    "Legend": COLORS["YELLOW"],
    "Mythic": COLORS["RED"],
    "Secret": COLORS["CYAN"],
}

# ================= GLOBAL VAR =================
last_output_time = None
total_interval = 0.0
total_output = 0
total_earn_coin = 0.0
total_delay = 0.0
rarity_count = {r: 0 for r in RARITY_COLORS.keys()}
active_channels = set()
fake_username = random.choice(["AquaHunter", "FishPro", "Oceanic", "DeepCatch", "BaitMaster", "SharkByte", "ReelKing"])
last_catch_delay = 0.0

# ================= HELPER =================
def format_time_detail(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}h {minutes:02d}m {secs:05.2f}s"

def clean_markdown(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"[*_`~]+", "", text).strip()

def parse_price_to_number(text: str) -> float:
    numbers = re.findall(r"[\d.,]+", text)
    if not numbers:
        return 0.0
    try:
        return float(numbers[0].replace(",", ""))
    except:
        return 0.0

def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")

def show_banner():
    banner = [
        "   ___ _     _             __             ",
        "  / __(_)___| |__         / /  ___   __ _ ",
        " / _\\ | / __| '_ \\ _____ / /  / _ \\ / _` |",
        "/ /   | \\__ \\ | | |_____/ /__| (_) | (_| |",
        "\\/    |_|___/_| |_|     \\____/\\___/ \\__, |",
        "      Ex @RHD Made with   🍌        |___/ ",
        "      Webhook by Vizub                      "
    ]
    colors = [COLORS["RED"], COLORS["YELLOW"], COLORS["GREEN"], COLORS["CYAN"], COLORS["BLUE"], COLORS["MAGENTA"]]
    for i, line in enumerate(banner):
        print(colors[i % len(colors)] + line + COLORS["END"])
    print("\n")

# ================= DASHBOARD PANEL SIMPLE + WARNA =================
def show_dashboard(last_catch):
    clear_terminal()
    show_banner()

    total_fish = sum(rarity_count.values())
    avg_delay = total_delay / total_output if total_output > 0 else 0.0

    def format_line(label, value, label_width=18):
        return f"{label.ljust(label_width)}: {value}"

    # Judul
    print("✅ FISH COUNTER 🎣 MULTI-CHANNEL\n")

    # Statistik Worker
    print(format_line("Online Channels", f"{len(active_channels)} / {len(CHANNEL_IDS)}"))
    print(format_line("Total Caught", total_output))
    print(format_line("Total Earn Coin", f"{int(total_earn_coin):,} Coins"))
    print(format_line("Total Time", format_time_detail(total_interval)))
    print(format_line("Delay Last Catch", format_time_detail(last_catch_delay)))
    print(format_line("Avg Delay/Catch", format_time_detail(avg_delay)))

    print("\nRarity Count")
    # Rarity 3 kolom dengan warna
    rarity_list = list(RARITY_COLORS.keys())
    col_width = 20
    def format_rarity_row(row):
        cells = []
        for r in row:
            cell = f"{RARITY_COLORS[r]}{r} : {rarity_count[r]}{COLORS['END']}"
            cells.append(cell.ljust(col_width))
        return "   ".join(cells)

    print(format_rarity_row(rarity_list[:3]))
    print(format_rarity_row(rarity_list[3:]))

    # Last Catch
    print("\n" + format_line("Last Update (WIB)", last_catch['time']))
    print(format_line("Player", last_catch['player']))
    print(format_line("Catch", last_catch['fish']))
    rarity_color = RARITY_COLORS.get(last_catch['rarity'], COLORS['WHITE'])
    print(format_line("Rarity", f"{rarity_color}{last_catch['rarity']}{COLORS['END']}"))
    print(format_line("Weight", last_catch['weight']))
    print(format_line("Price", last_catch['price']))
    print(format_line("Mutation", last_catch['mutation']))
    print("\n")

# ================= DISCORD EVENTS =================
@bot.event
async def on_ready():
    print(f"✅ Bot login sebagai {bot.user}")
    print("📡 Memantau channel ID berikut:")
    for cid in CHANNEL_IDS:
        print(f"- {cid}")
    print("⏳ Menunggu pesan log ikan...\n")

@bot.event
async def on_message(message):
    global last_output_time, total_interval, total_output, total_earn_coin, rarity_count, last_catch_delay, total_delay

    if message.author == bot.user:
        return
    if message.channel.id not in CHANNEL_IDS:
        return

    active_channels.add(message.channel.id)
    current_time = time.time()
    if last_output_time is not None:
        last_catch_delay = current_time - last_output_time
        total_interval += last_catch_delay
        total_delay += last_catch_delay
    else:
        last_catch_delay = 0.0
    last_output_time = current_time
    total_output += 1

    waktu_wib = message.created_at.replace(tzinfo=pytz.utc).astimezone(TZ_JAKARTA)
    waktu_str = waktu_wib.strftime("%d %B %Y %H:%M:%S")

    player_name, fish_name, rarity, weight, sell_price, mutation = "-", "-", "-", "-", "-", "-"

    if message.embeds:
        for embed in message.embeds:
            e = embed.to_dict()
            if "fields" in e:
                for field in e["fields"]:
                    name = clean_markdown(field["name"]).lower()
                    value = clean_markdown(field["value"])
                    if any(k in name for k in ["player", "fisher", "username"]):
                        player_name = fake_username
                    elif "fish" in name:
                        fish_name = value
                    elif "rarity" in name:
                        rarity = value
                        for r in rarity_count:
                            if r.lower() in rarity.lower():
                                rarity_count[r] += 1
                    elif "weight" in name:
                        weight = value
                    elif any(k in name for k in ["price", "sell", "harga"]):
                        sell_price = value
                        total_earn_coin += parse_price_to_number(value)
                    elif "mutation" in name:
                        mutation = value

    last_catch_info = {
        "time": waktu_str,
        "player": player_name,
        "fish": fish_name,
        "rarity": rarity,
        "weight": weight,
        "price": sell_price,
        "mutation": mutation
    }

    show_dashboard(last_catch_info)

# ================= RUN BOT =================
bot.run(TOKEN)
