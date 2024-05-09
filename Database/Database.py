import mysql.connector;

class Database:
	def __init__(self, user, password, database):
		'''
		Initializes a new instance of the class.

		Parameters:
		None

		Returns:
		None
		'''
		self.erp_orders = []
		self.mes_orders = []
		self.erp_open = []
		self.mes_open = []
		self.erp_order = []
		self.mes_order = []
		self.ware1 = []
		self.ware2 = []
		self.user = user
		self.password = password
		# self.database = database
		self.__createsDatabase__(database)
		# self.__createsDatabase__("erp")
		

	def __createsConnector__(self, dbname):
		try:
			self.connector = mysql.connector.connect(       						# Creates a connector to access the database
					host="localhost",
					user=self.user,													# The user YOU selected to access the server
					password=self.password,											# The password YOU selected to access the server
			)

			cursor = self.connector.cursor()
			sql = "USE {}".format(dbname)
			cursor.execute(sql)
			
			cursor.close()

			return True
		except mysql.connector.Error as err:
			print("Error connecting to database server: " + str(err))
			return False

	def __deletesConnector__(self):
		self.connector.close()

	def __createsDatabase__(self, dbname):
		
		try:
			self.connector = mysql.connector.connect(       						# Creates a connector to access the database
					host="localhost",
					user=self.user,													# The user YOU selected to access the server
					password=self.password											# The password YOU selected to access the server
			)
			print("Connected to the database server")

			cursor = self.connector.cursor()
			sql = "CREATE DATABASE IF NOT EXISTS {}".format(dbname)
			cursor.execute(sql)
			self.connector.commit()

			sql = "USE {}".format(dbname)
			
			cursor.execute(sql)


			sql = "CREATE TABLE IF NOT EXISTS {}_orders(id INT NOT NULL AUTO_INCREMENT, client VARCHAR(30) NOT NULL, number INT NOT NULL, workpiece VARCHAR(2) NOT NULL, quantity INT NOT NULL, due_date INT NOT NULL, late_pen INT NOT NULL, early_pen INT NOT NULL, PRIMARY KEY (id));".format(dbname)
			cursor.execute(sql)

			sql = "CREATE TABLE IF NOT EXISTS {}_open(id INT NOT NULL);".format(dbname)
			cursor.execute(sql)

			sql = "CREATE TRIGGER IF NOT EXISTS after_order_insert AFTER INSERT  ON {}_orders FOR EACH ROW INSERT INTO {}_open VALUES (NEW.id);".format(dbname,dbname)			
			cursor.execute(sql)
			
			sql = "CREATE TRIGGER IF NOT EXISTS before_order_delete BEFORE DELETE ON {}_orders FOR EACH ROW DELETE FROM {}_open WHERE id = OLD.id;".format(dbname, dbname)
			cursor.execute(sql)
			# if (dbname == "erp"):
			# 	sql = "CREATE TABLE IF NOT EXISTS erp_orders(id INT NOT NULL AUTO_INCREMENT, client VARCHAR(30) NOT NULL, number INT NOT NULL, workpiece VARCHAR(2) NOT NULL, quantity INT NOT NULL, due_date INT NOT NULL, late_pen INT NOT NULL, early_pen INT NOT NULL, PRIMARY KEY (id));"
			# 	cursor.execute(sql)

			# 	sql = "CREATE TABLE IF NOT EXISTS erp_open(id INT NOT NULL);"
			# 	cursor.execute(sql)

			# 	sql = "CREATE TRIGGER IF NOT EXISTS after_order_insert AFTER INSERT  ON erp_orders FOR EACH ROW INSERT INTO erp_open VALUES (NEW.id);"
			# 	cursor.execute(sql)
				
			# 	sql = "CREATE TRIGGER IF NOT EXISTS before_order_delete BEFORE DELETE ON erp_orders FOR EACH ROW DELETE FROM erp_open WHERE id = OLD.id;"
			# 	cursor.execute(sql)

			# el
			if (dbname == "mes"):
				# sql = "CREATE TABLE IF NOT EXISTS mes_orders(id INT NOT NULL AUTO_INCREMENT, client VARCHAR(30) NOT NULL, number INT NOT NULL, workpiece VARCHAR(2) NOT NULL, quantity INT NOT NULL, due_date INT NOT NULL, late_pen INT NOT NULL, early_pen INT NOT NULL, PRIMARY KEY (id));"
				# cursor.execute(sql)

				# sql = "CREATE TABLE IF NOT EXISTS mes_open(id INT NOT NULL);"
				# cursor.execute(sql)

				sql = "CREATE TABLE IF NOT EXISTS {}_ware1(workpiece VARCHAR(2) NOT NULL, quantity INT NOT NULL);".format(dbname)
				cursor.execute(sql)

				sql = "CREATE TABLE IF NOT EXISTS {}_ware2(workpiece VARCHAR(2) NOT NULL, quantity INT NOT NULL);".format(dbname)
				cursor.execute(sql)

				# sql = "CREATE TRIGGER IF NOT EXISTS after_order_insert AFTER INSERT  ON mes_orders FOR EACH ROW INSERT INTO mes_open VALUES (NEW.id);"
				# cursor.execute(sql)
				
				# sql = "CREATE TRIGGER IF NOT EXISTS before_order_delete BEFORE DELETE ON mes_orders FOR EACH ROW DELETE FROM mes_open WHERE id = OLD.id;"
				# cursor.execute(sql)

			self.connector.commit()

			cursor.close()
			self.__deletesConnector__()

			self.__fetchAll__(dbname)
		except mysql.connector.Error as err:
			print("Error connecting to database server: " + str(err))

	
	def __fetchOrders__(self, dbname):
		self.getOrders(dbname)
		self.__printOrders__(dbname)

	def __fetchOpen__(self, dbname):	
		self.getOpenOrders(dbname)
		self.__printOpen__(dbname)
	
	def __fetchAll__(self, dbname):
		self.getOrders(dbname)
		self.getOpenOrders(dbname)
		self.__printOrders__(dbname)
		self.__printOpen__(dbname)

	def __fetchWare__(self, warenumber):	
		self.getWare(warenumber)
		self.__printWare__(warenumber)

	def insertOrder(self, client, order, dbname):
		'''
		Inserts an order to the orders table of the database

		Parameters:
		client (str): The name of the client
		order (Order): The order to be inserted

		Returns:
		None
		'''
		if(self.__createsConnector__(dbname)):											# Connects to the server
			cursor = self.connector.cursor()													#Creates a cursor object to execute queries, cursors are used to execute single queries
			sql = "INSERT INTO {}_orders (client, number, workpiece, quantity, due_date, late_pen, early_pen) VALUES (%s, %s, %s, %s, %s, %s, %s)".format(dbname)
			value = (client, order.number, order.workpiece, order.quantity, order.due_date, order.late_pen, order.early_pen)
																					#Insert to the orders table the data of the order plus the ID of the desired client
			cursor.execute(sql, value)
			self.connector.commit()

			cursor.close()
			self.__deletesConnector__()

			self.__fetchOrders__(dbname)


	def getOrders(self, dbname):
		'''
		Updates all orders from the database

		Parameters:
		None

		Returns:
		None
		'''
		if(self.__createsConnector__(dbname)):											# Connects to the server
			cursor = self.connector.cursor()
			
			sql = "CREATE TEMPORARY TABLE temp SELECT * FROM {}_orders".format(dbname)
			cursor.execute(sql)
			sql = "ALTER TABLE temp DROP COLUMN id"
			cursor.execute(sql)
			sql = "SELECT * FROM temp"
			cursor.execute(sql)

			if(dbname == "erp"):
				self.erp_orders = cursor.fetchall()
			elif(dbname == "mes"):
				self.mes_orders = cursor.fetchall()

			sql = "DROP TABLE temp"	
			cursor.execute(sql)
			self.connector.commit()

			cursor.close()
			self.__deletesConnector__()


	def getOpenOrders(self, dbname):
		'''
		Updates all pendent orders from the database sorted from smaller to larger due_date

		Parameters:
		None

		Returns:
		None
		'''
		if(self.__createsConnector__(dbname)):											# Connects to the server
			cursor = self.connector.cursor()
			value = (dbname, dbname)
			sql = "CREATE TEMPORARY TABLE temp SELECT * FROM {}_orders WHERE id IN (SELECT id FROM {}_open)".format(dbname, dbname)
			cursor.execute(sql)
			sql = "ALTER TABLE temp DROP COLUMN id"
			cursor.execute(sql)
			sql = "SELECT * FROM temp ORDER BY due_date"
			cursor.execute(sql)
			if (dbname == "erp"):
				self.erp_open = cursor.fetchall()
			elif (dbname == "mes"):
				self.mes_open = cursor.fetchall()

			sql = "DROP TABLE temp"
			cursor.execute(sql)
			self.connector.commit()

			cursor.close()
			self.__deletesConnector__()

	def getWare(self, warenumber):
		'''
		Updates all workpieces at the selected warehouse

		Parameters:
		None

		Returns:
		None
		'''
		if(self.__createsConnector__("mes")):											# Connects to the server
			cursor = self.connector.cursor()
			sql = "SELECT * FROM mes_ware{}".format(warenumber)
			cursor.execute(sql)
			if(warenumber == 1):
				self.mes_ware1 = cursor.fetchall()
			elif(warenumber == 2):
				self.mes_ware2 = cursor.fetchall()
			self.connector.commit()

			cursor.close()
			self.__deletesConnector__()


	def __printWare__(self, warenumber):
		'''
		Prints all workpieces at the selected warehouse

		Parameters:
		None

		Returns:
		None
		'''
		if(warenumber == 1):
			print("\n############################### [MES] Warehouse 1 ############################### \n   workpiece | quantity")
			for x in self.mes_ware1:
				print(list(x))
		elif(warenumber == 2):
			print("\n############################### [MES] Warehouse 2 ############################### \n   workpiece | quantity")
			for x in self.mes_ware2:
				print(list(x))
		print      ("#################################################################################\n")

	def __printOrders__(self, dbname):
		'''
		Prints all orders from the database

		Parameters:
		None

		Returns:
		None
		'''
		
		if(dbname == "erp"):
			print("\n################################ [ERP] Orders ################################# \n   client | ord_num | workpiece | quantity | due_date | late_pen | early_pen")
			for x in self.erp_orders:
				print(list(x))
		elif(dbname == "mes"):
			print("\n################################ [MES] Orders ################################# \n   client | ord_num | workpiece | quantity | due_date | late_pen | early_pen")
			for x in self.mes_orders:
				print(list(x))
		print      ("###############################################################################\n")


	def __printOpen__(self, dbname):
		'''
		Prints all pendent orders from the database

		Parameters:
		None

		Returns:
		None
		'''
		if(dbname == "erp"):
			print("\n############################# [ERP] Open Orders ############################### \n   client | ord_num | workpiece | quantity | due_date | late_pen | early_pen")
			for x in self.erp_open:
				print(list(x))
		elif(dbname == "mes"):
			print("\n############################# [MES] Open Orders ############################### \n   client | ord_num | workpiece | quantity | due_date | late_pen | early_pen")
			for x in self.mes_open:
				print(list(x))
		print  	   ("###############################################################################\n")


	def printOrder(self, dbname):
		'''
		Prints the last specific order gotten from the database

		Parameters:
		None

		Returns:
		None
		'''
		if(dbname == "erp"):
			print("\n################################ [ERP] Order Found ################################## \n   client | ord_num | workpiece | quantity | due_date | late_pen | early_pen")
			for x in self.erp_order:
				print(list(x))
		elif(dbname == "mes"):
			print("\n################################ [MES] Order Found ################################## \n   client | ord_num | workpiece | quantity | due_date | late_pen | early_pen")
			for x in self.mes_order:
				print(list(x))
		print      ("###############################################################################\n")


	def processOrderByNum(self, client, order_number, dbname):
		'''
		Gets a specific order from the database by the client and the order number and closes it

		Parameters:
		client (str): The name of the client
		order_number (int): The number of the order

		Returns:
		List: The order with the correspondent client and order number
		None: If no order was found
		'''
		if(self.__createsConnector__(dbname)):											# Connects to the server
			
			
			cursor = self.connector.cursor()
			sql = "SELECT EXISTS(SELECT * FROM {}_orders WHERE client = \"".format(dbname) + client + "\")"		#Check if the client exists
			cursor.execute(sql)
			c_exists = cursor.fetchall()
			if(c_exists[0][0]):
				sql = "SELECT EXISTS(SELECT * FROM {}_orders WHERE number = ".format(dbname) + str(order_number) + " AND client = \"" + client + "\")"
				cursor.execute(sql)
				o_exists = cursor.fetchall()
				if(o_exists[0][0]):
					sql = "SELECT * FROM {}_orders WHERE number = ".format(dbname) + str(order_number) + " AND client = \"" + client + "\""
					cursor.execute(sql)
					if(dbname == "erp"):
						self.erp_order = cursor.fetchall()
					elif(dbname == "mes"):
						self.mes_order = cursor.fetchall()
					cursor.execute("SET SQL_SAFE_UPDATES = 0")
					cursor.execute("DELETE FROM {}_open WHERE id IN (SELECT id FROM {}_orders WHERE number = ".format(dbname, dbname) + str(order_number) + " AND client = \"" + client + "\")", values)
					cursor.execute("SET SQL_SAFE_UPDATES = 1")
					self.connector.commit()
					
					cursor.close()
					self.__deletesConnector__()

					self.__fetchOpen__()
					if(dbname == "erp"):
						return self.erp_order
					elif(dbname == "mes"):
						return self.mes_order
				else:
					print("Order doesn't exist")
			else:
				print("Client doesn't exist")
			
			cursor.close()
			self.__deletesConnector__()
			return None

	def processMostUrgentOrder(self, dbname):
		'''
		Gets the most urgent order from the database (if due_date is the same, the order with the lower number is chosen) and closes it

		Parameters:
		None

		Returns:
		List: The most urgent order
		None: If no order was found
		'''
		if(self.__createsConnector__(dbname)):											# Connects to the server
			cursor = self.connector.cursor()
			
			
			sql = "SELECT EXISTS(SELECT * FROM {}_orders WHERE id IN (SELECT id FROM {}_open))".format(dbname, dbname)		#Check if any order exists
			cursor.execute(sql)
			exists = cursor.fetchall()
			if(exists[0][0]):
				cursor.execute("CREATE TEMPORARY TABLE temp SELECT * FROM {}_orders WHERE id IN (SELECT id FROM {}_open)".format(dbname, dbname))
				cursor.execute("SELECT MIN(due_date) FROM temp")
				min_due_date = cursor.fetchall()
				cursor.execute("SET SQL_SAFE_UPDATES = 0")
				cursor.execute("DELETE FROM temp WHERE due_date <> " + str(min_due_date[0][0]))
				self.connector.commit()
				cursor.execute("DELETE FROM {}_open WHERE id IN (SELECT MIN(id) FROM temp)".format(dbname))
				cursor.execute("SET SQL_SAFE_UPDATES = 1")
				cursor.execute("ALTER TABLE temp DROP COLUMN id")
				cursor.execute("SELECT * FROM temp")
				if(dbname == "erp"):
					self.erp_order = cursor.fetchall()
				elif(dbname == "mes"):
					self.mes_order = cursor.fetchall()
				cursor.execute("DROP TABLE temp")
				self.connector.commit()

				cursor.close()
				self.__deletesConnector__()
				self.__fetchOpen__(dbname)

				if(dbname == "erp"):
					return self.erp_order
				elif(dbname == "mes"):
					return self.mes_order
			else:
				print("[Database] No open order to process in SQL database")

			cursor.close()
			self.__deletesConnector__()
			return None
			
	def updateWare(self, workpiece, quantity, dbname, warenum):
		'''
		Updates the selected warehouse with the new quantity

		Parameters:
		workpiece (str): The name of the workpiece
		quantity (int): The new quantity

		Returns:
		None
		'''
		if(self.__createsConnector__(dbname)):											# Connects to the server
			cursor = self.connector.cursor()
			
			sql = "SELECT EXISTS(SELECT * FROM mes_ware{} WHERE workpiece = '{}')".format(warenum, workpiece)		#Check if any workpiece of the type was already processed
			cursor.execute(sql)
			exists = cursor.fetchall()
			if(exists[0][0]):
				if(warenum == 1):
					sql = "UPDATE mes_ware1 SET quantity = quantity - {} WHERE workpiece = '{}'".format(quantity, workpiece)
				elif(warenum == 2):
					sql = "UPDATE mes_ware2 SET quantity = quantity + {} WHERE workpiece = '{}'".format(quantity, workpiece)
				cursor.execute(sql)
				self.connector.commit()

			else:
				print("[Database] No Workpiece of this type in the Warehouse")
				if(warenum == 2):
					sql = "INSERT INTO mes_ware2(workpiece, quantity) VALUES (%s, %s)"
					value = (workpiece, quantity)
					cursor.execute(sql, value)
					self.connector.commit()

			cursor.close()
			self.__deletesConnector__()
			self.__fetchWare__(warenum)

	# Coppied that just for testing, but it already exists in ERP Main.py
# class Order:
#     def __init__(self, number, workpiece, quantity, due_date, late_pen, early_pen):
#         self.number = number
#         self.workpiece = workpiece
#         self.quantity = quantity
#         self.due_date = due_date
#         self.late_pen = late_pen
#         self.early_pen = early_pen



############# TESTING #############

# db = Database()										#Create a db, get current clients, orders and print them

# order1 = Order(2, "P3", 5, 6, 12, 3)
# order2 = Order(19, "P6", 1, 4, 10, 10)
# db.insertOrder("AA", order1)						#Insert order1
# db.insertOrder("BB", order2)						#Insert order2

# db.processOrderByNum("AA", 2)							#Get order1 and closes it
# db.processMostUrgentOrder()								#Get most urgent order and closes it

# 	#Get clients, orders after action
# db.getOrders()
# db.__printOrders__()
# db.getOpenOrders()
# db.__printOpen__()



