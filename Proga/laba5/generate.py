
from datetime import datetime
from random import random, choice, randint
from threading import Thread, Lock
import math


nicks = {
	# 23 коротких ника (однословные, 5–7 символов)
	"Raven": [],
	"Tiger": [],
	"Falcon": [],
	"Viper": [],
	"Eagle": [],
	"Wolver": [],
	"Lynx": [],
	"Hawkeye": [],
	"Crow": [],
	"Fox": [],
	"Bear": [],
	"Lion": [],
	"Boar": [],
	"Elk": [],
	"Owl": [],
	"Bat": [],
	"Seal": [],
	"Crab": [],
	"Wasp": [],
	"Ant": [],
	"Beetle": [],
	"Fly": [],
	"Spider": [],

	# 40 длинных ников с дополнительной конструкцией (два слова + суффикс)
	"ShadowStalkerXxX": [],
	"NightCrawlerGG": [],
	"FireBreatherF": [],
	"StormWeaverAAA": [],
	"EarthShakerZzZ": [],
	"WindWhisperQwQ": [],
	"ThunderMasterOoO": [],
	"LightningStrikeBz": [],
	"CrystalGuardKk": [],
	"DarkHunterVvV": [],
	"LightBringerMew": [],
	"SoulKeeperNyx": [],
	"MindReaderRz": [],
	"TimeWalkerPw": [],
	"SpaceRiderLol": [],
	"StarGazerWwW": [],
	"MoonDancerHhH": [],
	"SunChaserYyY": [],
	"DawnBreakerPp": [],
	"DuskTreaderRr": [],
	"FrostBiteXxX": [],
	"FlameBringerGG": [],
	"EmberSparkF": [],
	"BlazeFuryAAA": [],
	"VortexMasterZzZ": [],
	"PhantomGhostQwQ": [],
	"ShadowReaperOoO": [],
	"SilentAssassinBz": [],
	"StealthNinjaKk": [],
	"QuickSilverVvV": [],
	"IronFistMew": [],
	"SteelHeartNyx": [],
	"BronzeShieldRz": [],
	"GoldenEaglePw": [],
	"SilverWolfLol": [],
	"CrimsonFoxWwW": [],
	"EmeraldDragonHhH": [],
	"SapphireTigerYyY": [],
	"RubyLionPp": [],
	"DiamondHawkRr": [],

	# 37 длинных ников без конструкции (просто два слова)
	"ObsidianSerpent": [],
	"GraniteGolem": [],
	"MarbleMystic": [],
	"QuartzKnight": [],
	"TopazTitan": [],
	"JadeJaguar": [],
	"AmberApe": [],
	"CoralCobra": [],
	"PearlPegasus": [],
	"RubyRaven": [],
	"SapphireSphinx": [],
	"TopazTroll": [],
	"ObsidianOwl": [],
	"GraniteGriffin": [],
	"MarbleManticore": [],
	"QuartzQuetzal": [],
	"JadeJinni": [],
	"AmberArchon": [],
	"CoralCentaur": [],
	"PearlPhoenix": [],
	"RubyRogue": [],
	"SapphireSorcerer": [],
	"TopazTamer": [],
	"ObsidianOracle": [],
	"GraniteGuardian": [],
	"MarbleMage": [],
	"QuartzQueen": [],
	"JadeJester": [],
	"AmberArcher": [],
	"CoralCrusader": [],
	"OnyxOutcast": [],
	"PearlPaladin": [],
	"RubyRanger": [],
	"SapphireShaman": [],
	"TopazThief": [],
	"ObsidianOverseer": [],
	"OnyxWarden": []
}


def atan_transform(x, threshold=40000, max_value=50000):
	if x <= threshold:
		return x
	else:
		# Масштабируем вход для atan, чтобы в threshold получить нужный наклон
		k = 2 / threshold  # коэффициент масштабирования
		# atan стремится к π/2, поэтому масштабируем выход
		return threshold + (max_value - threshold) * (2 / math.pi) * math.atan(k * (x - threshold))


def gen_date_and_hours():
	x = chunk_time * random()
	y = (chunk_time - x) * random() * 0.8 / 3600
	dt = datetime.fromtimestamp(x + start_time)
	return dt.strftime('%Y.%m.%d'), round(atan_transform(y), 3)


id_mask = list("0123456789abcdefghijklmnopqrstuvwxyz")
def gen_id():
	return "".join([choice(id_mask) for _ in range(8)])


def gen_line():
	nick = choice(list(nicks.keys()))
	id = gen_id()
	while True:
		if id not in nicks[nick]:
			break
		id = gen_id()
	nicks[nick].append(id)
	date, hours = gen_date_and_hours()
	level = randint(0, 100)
	ban = ("true" if randint(0, 99) <= 4 else "false")
	return ",".join([nick, id, date, str(level), str(hours), ban]) + "\n"


# файл data.csv через запятую
# 1 строка: ник
# 2 строка: айди (из 8 байт)
# 3 строка: дата регистрации (начиная с 2000.01.01)
# 4 инт: уровень
# 5 флот: кол-во часов (меньше или равно с момента регистрации)
# 6 бул: вак бан? 

# numbers = list(range(1,101))
# numbers_lock = Lock()

# def worker():
# 	pass

if __name__ == "__main__":
	start_time = int(datetime(2000, 1, 1).timestamp())
	end_time = int(datetime.now().timestamp())
	chunk_time = end_time - start_time

	# предварительно создать файл
	# fsutil file createNew data.csv 1127428915
	with open("data.csv", "r+b") as file:
		file.seek(0)
		size_max = (1024**3)*1.01
		chunk = size_max / 100
		counter = 0
		size = 0
		while size < size_max:
			if size > chunk*counter:
				print(counter, "%", sep="")
				counter+=1
			line = gen_line()
			file.write(line.encode("ascii"))
			file.flush()
			size += len(line)
	