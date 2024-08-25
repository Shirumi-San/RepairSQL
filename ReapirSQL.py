import datetime




# = Настройки скрипта ===========================================

# Название входного файла ("test.sql")
file = "mysql-4.sql" 

# Показатель того, сколько строк будет проверено полностью (рекомендуется не менее 100)
# если вы хотите проверять все строки полностью, то установите (-2)
limit_repair_column = -2

# Выводит в терминал информацию о проделанной работе
info = True

# Заменяет полные пути к файлам записи звонков на относительные (только для файла "mysql-4.sql")
path_repair = True

# ===============================================================




# = НЕ ТРОГАТЬ!!! ===============================================
flag_fix = False
repair_columns = []
name_table = ""
create_table = False
step = 0
infos = {}
path_repair_infos = {}
path_repair_infos["Полный путь: "] = 0
path_repair_infos["Относ. путь: "] = 0
path_repair_infos["Нет файла: "] = 0
fix_set = {
	b'\xe2\x80\x98': b'\x91', # ‘ Б
	b'\xe2\x80\x99': b'\x92', # ’ В
	b'\xe2\x80\x9c': b'\x93', # “ Г
	b'\xe2\x80\x9d': b'\x94', # ” Д
	b'\xe2\x80\xa2': b'\x95', # • Е
	b'\xe2\x80\x93': b'\x96', # – Ж
	b'\xe2\x80\x94': b'\x97', # — З
	b'\xcb\x9c':     b'\x98', # ˜ И
	b'\xe2\x84\xa2': b'\x99', # ™ Й
	b'\xc5\xa1':     b'\x9a', # š К
	b'\xe2\x80\xba': b'\x9b', # › Л
	b'\xc5\x93':     b'\x9c', # œ М
	b'\xc5\xbe':     b'\x9e', # ž О
	b'\xc5\xb8':     b'\x9f', # Ÿ П
	b'\xe2\x82\xac': b'\x80', # € р
	b'\xe2\x80\x9a': b'\x82', # ‚ т
	b'\xc6\x92':     b'\x83', # ƒ у
	b'\xe2\x80\x9e': b'\x84', # „ ф
	b'\xe2\x80\xa6': b'\x85', # … х
	b'\xe2\x80\xa0': b'\x86', # † ц
	b'\xe2\x80\xa1': b'\x87', # ‡ ч
	b'\xcb\x86':     b'\x88', # ˆ ш
	b'\xe2\x80\xb0': b'\x89', # ‰ щ
	b'\xe2\x80\xb9': b'\x8b', # ‹ ы
	b'\xc5\x92':     b'\x8c', # Œ ь
	b'\xc5\xbd':     b'\x8e', # Ž ю
}

fix_ru = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
# ===============================================================

if info:
	start = datetime.datetime.now()

def ConcatSQL(values):
	result = ""
	for value in values:
		result = result + value + ","
	return result[:-2]

def SplitValues(values):
	values_sql = values.split(",")
	if len(values_sql) > len(repair_columns):
		while len(values_sql) > len(repair_columns):
			for i in range(len(values_sql)-1):
				if (values_sql[i][0] == "'" and values_sql[i][-1] != "'") or (values_sql[i] == "'"): # or (values_sql[i][0:1] == "\'" and values_sql[i][-3:-1] != "\\\'"):
					values_sql[i] = values_sql[i] + "," + values_sql[i+1]
					values_sql.pop(i+1)
					break
	return values_sql

def FixChars(Char):
	if bytes(Char, "utf-8") in fix_set.keys():
		return fix_set[bytes(Char, "utf-8")]
	else:
		return Char.encode("latin-1")
	
def FixCharsStr(CharStr):
	result = b""
	for i in range(len(CharStr)):
		if bytes(CharStr[i], "utf-8") in fix_set.keys():
			result = result + fix_set[bytes(CharStr[i], "utf-8")]
		else:
			result = result + CharStr[i].encode("latin-1")
	return result

def Decode1252(value):
	for utf8_char_index in range(len(value)-2):
		if utf8_char_index <= len(value)-2:
			if value[utf8_char_index] == "Ð" or value[utf8_char_index] == "Ñ":
				repair_columns[value_sql_index] = -2
				try:
					use_char = (value[utf8_char_index:utf8_char_index+1].encode("latin1")+FixChars(value[utf8_char_index+1:utf8_char_index+2])).decode("utf-8")
				except UnicodeDecodeError:
					use_char = "Except"
				if use_char == "Except":
					value = value[:utf8_char_index] + value[utf8_char_index+1:]
				elif not (use_char in fix_ru):
					return "ERROR"
				else: 
					value = value[:utf8_char_index] + use_char + value[utf8_char_index+2:]
	return value

def Decode1251(value):
	for utf8_char_index in range(len(value)-2):
		if utf8_char_index <= len(value)-2:
			if value[utf8_char_index] == "Ð":
				use_char = (FixChars(value[utf8_char_index:utf8_char_index+1])+FixChars(value[utf8_char_index+1:utf8_char_index+2])).decode("utf-8")
				if (use_char == "Р" or use_char == "С"):
					if len(value[:utf8_char_index+1]) <= len(value)-2:
						use_char_next = value[utf8_char_index+2:utf8_char_index+4]
						for s in range(1,3):
							if len(value[:utf8_char_index+3+s]) <= len(value)-2:
								if value[utf8_char_index+3+s:utf8_char_index+4+s] != "Ð":
									use_char_next = use_char_next + value[utf8_char_index+3+s:utf8_char_index+4+s]
									if s == 2:
										use_char_next = use_char_next[:-1]
								else:
									break
							else:
								break
						if bytes(FixCharsStr(use_char_next).decode("utf-8"), "windows-1251") >= b'\x80' and bytes(FixCharsStr(use_char_next).decode("utf-8"), "windows-1251") <= b'\xbf':
							use_char_fix = (FixCharsStr(use_char.encode("windows-1251").decode("latin-1")) + bytes(FixCharsStr(use_char_next).decode("utf-8"), "windows-1251")).decode("utf-8")
							value = value[:utf8_char_index] + use_char_fix + value[utf8_char_index+3+s:]
				else:
					print("Fatal Error")
					return "Fatal Error"
	return value
								

with open(file, "r", encoding="utf-8") as import_sql:
	with open("repair_" + file, "w", encoding="utf-8") as export_sql:
		for line_sql in import_sql:
			flag_fix == False
			if line_sql[0] == "I":

				# исключение <xml>
				if line_sql.find("<xml>") != -1:
					export_sql.write(line_sql)
					
				else:
					values_sql = SplitValues(line_sql[22+step:len(line_sql)-2])
					for value_sql_index in range(len(repair_columns)):
						if repair_columns[value_sql_index] != -1:
							if len(values_sql[value_sql_index]) >= 2:

								DeCodeValue = Decode1252(values_sql[value_sql_index])

								if DeCodeValue == "ERROR":
									DeCodeValue = Decode1251(values_sql[value_sql_index])

								values_sql[value_sql_index] = DeCodeValue

								if repair_columns[value_sql_index] > -1:
									repair_columns[value_sql_index] -= 1

						if (path_repair) and (value_sql_index == 16):
							if values_sql[value_sql_index] == "''":
								path_repair_infos["Нет файла: "] += 1
							elif values_sql[value_sql_index][2:5] == "var":
								values_sql[value_sql_index] = values_sql[value_sql_index][0:1] + values_sql[value_sql_index][40:]
								path_repair_infos["Полный путь: "] += 1
							else:
								path_repair_infos["Относ. путь: "] += 1
									
					export_sql.write(f"INSERT INTO `{name_table}` VALUES ({ConcatSQL(values_sql)});\n")
					infos[name_table] += 1
			elif line_sql[0] == "C":
				name_table = line_sql[14:-4]
				infos[name_table] = 0
				create_table = True
				repair_columns.clear()
				step = len(line_sql) - 17
				export_sql.write(line_sql)
			elif create_table:
				if line_sql.find("varchar") != -1:
					repair_columns.append(limit_repair_column)
				elif line_sql.find("latin1") != -1:
					line_sql = line_sql.replace("latin1", "utf8mb4")
					create_table = False
				elif line_sql.find("KEY") == -1:
					repair_columns.append(-1)
				export_sql.write(line_sql)
			else:
				export_sql.write(line_sql)

if info:
	finish = datetime.datetime.now()
	print("╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍")
	print('Время работы: ' + str(finish - start))
	for table_info in infos.keys():
		print(f"  {table_info}: {infos[table_info]} записей обработано")
	if path_repair:
		print("╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍")
		for path_info in path_repair_infos.keys():
			print(f"  {path_info}{path_repair_infos[path_info]}")
	print("╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍")
