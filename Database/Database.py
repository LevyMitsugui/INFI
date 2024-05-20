import mysql.connector
from mysql.connector import errorcode
from mysql.connector import pooling
import time

class SQLDatabase:
	def __init__(self, user, password, database):
		"""
		Initializes a new instance of the class.

		Parameters:
		- user (str): The username used to connect to the database.
		- password (str): The password used to connect to the database.
		- database (str): The name of the database to connect to.

		Returns:
		None
		"""
		self.user = user
		self.password = password
		self.database = database
		self.pool = self.__createConnectionPool()
		
	def __createConnectionPool(self):
		"""
		Creates a MySQL connection pool.

		Returns:
		    MySQLConnectionPool: The created connection pool.

		Parameters:
		    self (Connection): The Connection object.

		Attributes:
		    user (str): The username for the MySQL connection.
		    password (str): The password for the MySQL connection.
		    database (str): The name of the MySQL database.

		Example usage:
		    connection = Connection("username", "password", "database")
		    connection_pool = connection.__createConnectionPool()
		"""
		max_retries = 5  # Maximum number of retries
		retry_delay = 2  # Delay between retries in seconds
		for i in range(max_retries):
			try:
				print("Connected to the database server")
				return pooling.MySQLConnectionPool(
					pool_name="myConnectionPool",
					pool_size=10,
					host="localhost",
					user=self.user,
					password=self.password
				)
			except Exception as e:
				if i == max_retries - 1:
					raise Exception("Failed to connect to the database after {} retries".format(max_retries))
				print("Failed to connect to the database. Retrying in {} seconds...".format(retry_delay))
				time.sleep(retry_delay)

	def get_connection(self):
		"""
		Get a connection from the connection pool.

		Returns:
		    MySQLConnection: A connection from the connection pool.
		"""
		return self.pool.get_connection()

	def close_connection(self, connection):
		connection.close()

	def execute(self, query):
		"""
		Execute a SQL query and return the result.

 		Parameters:
			query (str): A string representing the SQL query to execute.

		Returns:
		 	List[Tuple]: A list of tuples containing the result of the query.
		"""
		try:
			with self.get_connection() as connection:
				with connection.cursor() as cursor:
					cursor.execute(query)
					result = cursor.fetchall()
			return result
		except Exception as e:
			print("Error executing query:", e)
			return None
	
	def commit(self, query):
		"""
		Commit the changes made to the database.

		Returns:
		 	None
		"""
		try:
			with self.get_connection() as connection:
				with connection.cursor() as cursor:
					cursor.execute(query)
					connection.commit()
		except Exception as e:
			print("Error executing and commiting query:", e)

	def execute_query(self, query):
		"""
		Execute a SQL query and return the result.

 		Parameters:
			query (str): A string representing the SQL query to execute.

		Returns:
		 	List[Tuple]: A list of tuples containing the result of the query.
		"""
		try:
			with self.get_connection() as connection:
				with connection.cursor() as cursor:
					cursor.execute("USE {}".format(self.database))
					cursor.execute(query)
					result = cursor.fetchall()
			return result
		except Exception as e:
			print("Error executing query at database:", e)
			return None

	def execute_non_query(self, query):
		"""
		Execute a SQL query and return the result.

 		Parameters:
			query (str): A string representing the SQL query to execute.

		Returns:
		 	List[Tuple]: A list of tuples containing the result of the query.
		"""
		try:
			with self.get_connection() as connection:
				with connection.cursor() as cursor:
					cursor.execute("USE {}".format(self.database))
					cursor.execute(query)
					connection.commit()
		except Exception as e:
			print("Error executing and commiting query at database:", e)

	def execute_multi_query(self, query):
		"""
		Execute a SQL query and return the result.

 		Parameters:
			query (str): A string representing the SQL query to execute.

		Returns:
		 	List[Tuple]: A list of tuples containing the result of the query.
		"""		

	def change_database(self, database):
		self.database = database

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
		self.erp_processing = []
		self.mes_processing = []
		self.mes_done = []
		self.mes_done = []
		self.erp_order = []
		self.mes_order = []
		self.ware1 = []
		self.ware1_qnt = []
		self.ware2 = []
		self.ware2_qnt = []
		self.user = user
		self.password = password
		# self.database = database
		self.conn = self.__createsConnection__(database)
		self.__createsDatabase__(database)
		# self.__createsDatabase__("erp")
		
	def __createsConnection__(self, database):
		return SQLDatabase(self.user, self.password, database)

	def __createsDatabase__(self, dbname):
		
		try:			
			sql = "SHOW DATABASES LIKE '{}'".format(dbname)
			
			aux = self.conn.execute(sql)
			if not aux:	# If the database doesn't exists it will be created
				sql = "CREATE DATABASE IF NOT EXISTS {}".format(dbname)
				self.conn.commit(sql)

				self.conn.change_database(dbname)

				sql = "CREATE TABLE IF NOT EXISTS {}_orders(id INT NOT NULL AUTO_INCREMENT, done VARCHAR(4) NOT NULL DEFAULT '', client VARCHAR(30) NOT NULL, number INT NOT NULL, workpiece VARCHAR(2) NOT NULL, quantity INT NOT NULL, due_date INT NOT NULL, late_pen INT NOT NULL, early_pen INT NOT NULL, PRIMARY KEY (id));".format(dbname)			
				self.conn.execute_non_query(sql)

				sql = "CREATE TABLE IF NOT EXISTS {}_open(id INT NOT NULL);".format(dbname)			
				self.conn.execute_non_query(sql)
				
				sql = "CREATE TABLE IF NOT EXISTS {}_processing(id INT NOT NULL);".format(dbname)			
				self.conn.execute_non_query(sql)

				sql = "CREATE TRIGGER IF NOT EXISTS after_order_insert AFTER INSERT  ON {}_orders FOR EACH ROW INSERT INTO {}_open VALUES (NEW.id);".format(dbname, dbname)			
				self.conn.execute_non_query(sql)
				
				sql = "CREATE TRIGGER IF NOT EXISTS before_order_delete BEFORE DELETE ON {}_orders FOR EACH ROW DELETE FROM {}_open WHERE id = OLD.id;".format(dbname, dbname)
				self.conn.execute_non_query(sql)

				sql = "CREATE TRIGGER IF NOT EXISTS before_open_delete BEFORE DELETE ON {}_open FOR EACH ROW INSERT INTO {}_processing VALUES (OLD.id);".format(dbname, dbname)
				self.conn.execute_non_query(sql)

				if (dbname == "mes"):

					sql = "CREATE TABLE IF NOT EXISTS {}_ware1(workpiece VARCHAR(2) NOT NULL);".format(dbname)
					self.conn.execute_non_query(sql)

					sql = "CREATE TABLE IF NOT EXISTS {}_ware2(workpiece VARCHAR(2) NOT NULL);".format(dbname)
					self.conn.execute_non_query(sql)

			if not aux: # If the database doesn't exists it will be shown
				self.__fetchAll__(dbname)
		except mysql.connector.Error as err:
			print("Error connecting to database server: " + str(err))

	
	def __fetchOrders__(self, dbname):
		self.getOrders(dbname)
		self.__printOrders__(dbname)

	def __fetchOpen__(self, dbname):	
		self.getOpenOrders(dbname)
		self.__printOpen__(dbname)

	def __fetchProcessing__(self, dbname):
		self.getProcessingOrders(dbname)
		self.__printProcessing__(dbname)

	def __fetchOrdersDone__(self, dbname):
		self.getOrdersDone(dbname)
		self.__printDone__(dbname)
	
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
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				sql = "USE {}".format(dbname)
				cursor.execute(sql)
				sql = "INSERT INTO {}_orders (client, number, workpiece, quantity, due_date, late_pen, early_pen) VALUES (%s, %s, %s, %s, %s, %s, %s)".format(dbname)
				value = (client, order.number, order.workpiece, order.quantity, order.due_date, order.late_pen, order.early_pen)
																						#Insert to the orders table the data of the order plus the ID of the desired client
				cursor.execute(sql, value)
				conn.commit()

		# self.__fetchOrders__(dbname)
		self.__fetchAll__(dbname)


	def getOrders(self, dbname):
		'''
		Updates all orders from the database

		Parameters:
		None

		Returns:
		None
		'''
# with self.__createsConnector__(dbname) as cursor:											# Connects to the server
# 	if cursor:
	
		with self.conn.get_connection() as conn:
			with conn.cursor() as cursor:
				sql = "USE {}".format(dbname)
				cursor.execute(sql)
				sql = "CREATE TEMPORARY TABLE temp SELECT * FROM {}_orders".format(dbname)
				cursor.execute(sql)
				sql = "ALTER TABLE temp DROP COLUMN id"
				cursor.execute(sql)
				sql = "ALTER TABLE temp DROP COLUMN done"
				cursor.execute(sql)
				sql = "SELECT * FROM temp"
				cursor.execute(sql)
				if(dbname == "erp"):
					self.erp_orders = cursor.fetchall()
					orders = self.erp_orders
				elif(dbname == "mes"):
					self.mes_orders = cursor.fetchall()
					orders = self.mes_orders

				sql = "DROP TABLE temp"
				cursor.execute(sql)
				conn.commit()

				return orders


	def getOpenOrders(self, dbname):
		'''
		Updates all pendent orders from the database sorted from smaller to larger due_date

		Parameters:
		None

		Returns:
		None
		'''
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				sql = "USE {}".format(dbname)
				cursor.execute(sql)
				sql = "CREATE TEMPORARY TABLE temp SELECT * FROM {}_orders WHERE id IN (SELECT id FROM {}_open)".format(dbname, dbname)
				cursor.execute(sql)
				sql = "ALTER TABLE temp DROP COLUMN id"
				cursor.execute(sql)
				sql = "ALTER TABLE temp DROP COLUMN done"
				cursor.execute(sql)
				sql = "SELECT * FROM temp ORDER BY due_date"
				cursor.execute(sql)
				if (dbname == "erp"):
					self.erp_open = cursor.fetchall()
					openOrders = self.erp_open
				elif (dbname == "mes"):
					self.mes_open = cursor.fetchall()
					openOrders = self.mes_open

				sql = "DROP TABLE temp"
				cursor.execute(sql)
				conn.commit()

				return openOrders


	def getProcessingOrders(self, dbname):
		'''
		Updates all processing orders from the database

		Parameters:
		None

		Returns:
		None
		'''
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				sql = "USE {}".format(dbname)
				cursor.execute(sql)
				sql = "CREATE TEMPORARY TABLE temp SELECT * FROM {}_orders WHERE id IN (SELECT id FROM {}_processing)".format(dbname, dbname)
				cursor.execute(sql)
				sql = "ALTER TABLE temp DROP COLUMN id"
				cursor.execute(sql)
				sql = "ALTER TABLE temp DROP COLUMN done"
				cursor.execute(sql)
				sql = "SELECT * FROM temp ORDER BY due_date"
				cursor.execute(sql)
				if (dbname == "erp"):
					self.erp_processing = cursor.fetchall()
					processingOrders = self.erp_processing
				elif (dbname == "mes"):
					self.mes_processing = cursor.fetchall()
					processingOrders = self.mes_processing

				sql = "DROP TABLE temp"
				cursor.execute(sql)
				conn.commit()

				return processingOrders


	def getOrdersDone(self, dbname):
		'''
		Updates all orders done from the database

		Parameters:
		None

		Returns:
		None
		'''
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				sql = "USE {}".format(dbname)
				cursor.execute(sql)
				sql = "CREATE TEMPORARY TABLE temp SELECT * FROM {}_orders WHERE done = 'X'".format(dbname)
				cursor.execute(sql)
				sql = "ALTER TABLE temp DROP COLUMN id"
				cursor.execute(sql)
				sql = "ALTER TABLE temp DROP COLUMN done"
				cursor.execute(sql)
				sql = "SELECT * FROM temp"
				cursor.execute(sql)

				if(dbname == "erp"):
					self.erp_done = cursor.fetchall()
					ordersDone = self.erp_done
				elif(dbname == "mes"):
					self.mes_done = cursor.fetchall()
					ordersDone = self.mes_done

				sql = "DROP TABLE temp"	
				cursor.execute(sql)
				conn.commit()

				return ordersDone

	def getWare(self, warenumber):
		'''
		Updates all workpieces at the selected warehouse

		Parameters:
		None

		Returns:
		None
		'''
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				sql = "USE {}".format("mes")
				cursor.execute(sql)
				sql = "SELECT * FROM mes_ware{}".format(warenumber)
				cursor.execute(sql)
				if(warenumber == 1):
					self.ware1 = cursor.fetchall()
					sql = "SELECT workpiece, COUNT(*) FROM mes_ware{} GROUP BY workpiece".format(warenumber)
					cursor.execute(sql)
					self.ware1_qnt = cursor.fetchall()
				elif(warenumber == 2):
					self.ware2 = cursor.fetchall()
					sql = "SELECT workpiece, COUNT(*) FROM mes_ware{} GROUP BY workpiece".format(warenumber)
					cursor.execute(sql)
					self.ware2_qnt = cursor.fetchall()
				conn.commit()


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
			for x in self.ware1_qnt:
				print(list(x))
			print("-------------------------")
			ware1_pieces = [item[0] for item in self.ware1]
			print("                                  ", ware1_pieces)
		elif(warenumber == 2):
			print("\n############################### [MES] Warehouse 2 ############################### \n   workpiece | quantity")
			for x in self.ware2_qnt:
				print(list(x))
			print("-------------------------")
			ware2_pieces = [item[0] for item in self.ware2]
			print("                                  ", ware2_pieces)
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

	
	def __printProcessing__(self, dbname):
		'''
		Prints all processing orders from the database

		Parameters:
		None

		Returns:
		None
		'''
		if(dbname == "erp"):
			print("\n############################# [ERP] Processing Orders ############################### \n   client | ord_num | workpiece | quantity | due_date | late_pen | early_pen")
			for x in self.erp_processing:
				print(list(x))
		elif(dbname == "mes"):
			print("\n############################# [MES] Processing Orders ############################### \n   client | ord_num | workpiece | quantity | due_date | late_pen | early_pen")
			for x in self.mes_processing:
				print(list(x))
		print  	   ("###############################################################################\n")

	
	def __printDone__(self, dbname):
		'''
		Prints all orders done from the database

		Parameters:
		None

		Returns:
		None
		'''
		if(dbname == "erp"):
			print("\n############################# [ERP] Orders Done ############################### \n   client | ord_num | workpiece | quantity | due_date | late_pen | early_pen")
			for x in self.erp_done:
				print(list(x))
		elif(dbname == "mes"):
			print("\n############################# [MES] Orders Done ############################### \n   client | ord_num | workpiece | quantity | due_date | late_pen | early_pen")
			for x in self.mes_done:
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
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				sql = "USE {}".format(dbname)
				cursor.execute(sql)
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
						cursor.execute("DELETE FROM {}_open WHERE id IN (SELECT id FROM {}_orders WHERE number = ".format(dbname, dbname) + str(order_number) + " AND client = \"" + client + "\")")
						cursor.execute("SET SQL_SAFE_UPDATES = 1")
						conn.commit()

					else:
						print("Order doesn't exist")
						return None
				else:
					print("Client doesn't exist")
					return None
		
		self.__fetchOpen__(dbname)
		if(dbname == "erp"):
			return self.erp_order
		elif(dbname == "mes"):
			return self.mes_order

	def processMostUrgentOrder(self, dbname):
		'''
		Gets the most urgent order from the database (if due_date is the same, the order with the lower number is chosen) and closes it

		Parameters:
		None

		Returns:
		List: The most urgent order
		None: If no order was found
		'''
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				sql = "USE {}".format(dbname)
				cursor.execute(sql)

				sql = "SELECT EXISTS(SELECT * FROM {}_orders WHERE id IN (SELECT id FROM {}_open))".format(dbname, dbname)		#Check if any order exists
				cursor.execute(sql)
				exists = cursor.fetchall()
				if(exists[0][0]):
					cursor.execute("CREATE TEMPORARY TABLE temp SELECT * FROM {}_orders WHERE id IN (SELECT id FROM {}_open)".format(dbname, dbname))
					cursor.execute("SELECT MIN(due_date) FROM temp")
					min_due_date = cursor.fetchall()
					cursor.execute("SET SQL_SAFE_UPDATES = 0")
					cursor.execute("DELETE FROM temp WHERE due_date <> " + str(min_due_date[0][0]))
					conn.commit()
					cursor.execute("DELETE FROM {}_open WHERE id IN (SELECT MIN(id) FROM temp)".format(dbname))
					cursor.execute("SET SQL_SAFE_UPDATES = 1")
					cursor.execute("ALTER TABLE temp DROP COLUMN id")
					cursor.execute("ALTER TABLE temp DROP COLUMN done")
					cursor.execute("SELECT * FROM temp")
					if(dbname == "erp"):
						self.erp_order = cursor.fetchall()
					elif(dbname == "mes"):
						self.mes_order = cursor.fetchall()
					cursor.execute("DROP TABLE temp")
					conn.commit()

				else:
					# print("[Database] No order being processed in mySQL database")
					return None
		
		self.__fetchOpen__(dbname)

		if(dbname == "erp"):
			return self.erp_order
		elif(dbname == "mes"):
			return self.mes_order
		

	def getMostUrgentOrder(self, dbname):
		'''
		Gets the most urgent processing order from the database (if due_date is the same, the order with the lower number is chosen) and closes it

		Parameters:
		None

		Returns:
		List: The most urgent order
		None: If no order was found
		'''
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				sql = "USE {}".format(dbname)
				cursor.execute(sql)

				
				sql = "CREATE TEMPORARY TABLE temp SELECT mp.* FROM mes_orders mp JOIN (SELECT workpiece, COUNT(*) AS ware2_count FROM mes_ware2 GROUP BY workpiece) mw ON mp.workpiece = mw.workpiece WHERE mp.quantity <= mw.ware2_count AND done <> 'X' ORDER BY due_date;"
				cursor.execute(sql)
				cursor.execute("ALTER TABLE temp DROP COLUMN id")
				cursor.execute("ALTER TABLE temp DROP COLUMN done")
				cursor.execute("SELECT * FROM temp")
				if(dbname == "erp"):
					self.erp_order = cursor.fetchall()
				elif(dbname == "mes"):
					self.mes_order = cursor.fetchall()
				cursor.execute("DROP TABLE temp")
				conn.commit()
				# sql = "SELECT EXISTS(SELECT * FROM {}_orders WHERE id NOT IN (SELECT id FROM {}_open))".format(dbname, dbname)		#Check if exists any order being processed
				# cursor.execute(sql)
				# exists = cursor.fetchall()
				# if(exists[0][0]):
				# 	cursor.execute("CREATE TEMPORARY TABLE temp SELECT * FROM {}_orders WHERE id NOT IN (SELECT id FROM {}_open)".format(dbname, dbname))
				# 	cursor.execute("SELECT MIN(due_date) FROM temp")
				# 	min_due_date = cursor.fetchall()
				# 	cursor.execute("SET SQL_SAFE_UPDATES = 0")
				# 	cursor.execute("DELETE FROM temp WHERE due_date <> " + str(min_due_date[0][0]))
				# 	conn.commit()
				# 	cursor.execute("SET SQL_SAFE_UPDATES = 1")
				# 	cursor.execute("ALTER TABLE temp DROP COLUMN id")
				# 	cursor.execute("ALTER TABLE temp DROP COLUMN done")
				# 	cursor.execute("SELECT * FROM temp")
				# 	if(dbname == "erp"):
				# 		self.erp_order = cursor.fetchall()
				# 	elif(dbname == "mes"):
				# 		self.mes_order = cursor.fetchall()
				# 	cursor.execute("DROP TABLE temp")
				# 	conn.commit()

				# else:
					# print("[Database] No order being processed in MySQL database")
					# return None			


		if(dbname == "erp" and self.erp_order):
			self.__fetchProcessing__(dbname)
			return self.erp_order
		elif (dbname == "mes" and self.mes_order):
			self.__fetchProcessing__(dbname)
			return self.mes_order
		else:
			return None
		
	def setOrderDone(self, client, order_number, dbname):
		'''
		Sets an order as done in the database

		Parameters:
		client (str): The name of the client
		order_number (int): The number of the order

		Returns:
		None
		'''
		sql = "UPDATE {}_orders SET done = 'X' WHERE number = ".format(dbname) + str(order_number) + " AND client = \"" + client + "\""
		self.conn.execute_non_query(sql)
		sql = "DELETE FROM {}_processing WHERE id IN (SELECT id FROM {}_orders WHERE number = ".format(dbname, dbname) + str(order_number) + " AND client = \"" + client + "\")"
		self.conn.execute_non_query(sql)
		
		self.__fetchOrdersDone__(dbname)
			
	def updateWare(self, workpiece, quantity, dbname, warenum):
		'''
		Updates the selected warehouse with the new quantity

		Parameters:
		workpiece (str): The name of the workpiece
		quantity (int): The new quantity

		Returns:
		None
		'''
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				sql = "USE {}".format(dbname)
				cursor.execute(sql)
				if(quantity > 0):
					sql = "INSERT INTO mes_ware{}(workpiece) VALUES (%s)".format(warenum)
					value = (workpiece,)
					cursor.execute(sql, value)
				else:
					sql = "DELETE FROM mes_ware{} WHERE workpiece = '{}' LIMIT 1".format(warenum, workpiece)
					cursor.execute(sql)
				conn.commit()

				# self.__fetchWare__(warenum)

	def countPiece(self, workpiece, table):
		'''
		Returns the quantity of the selected workpiece in the selected warehouse

		Parameters:
		workpiece (str): The name of the workpiece
		warenum (int): The number of the warehouse

		Returns:
		int: The quantity of the workpiece in the warehouse
		'''
		sql = "SELECT COUNT(*) FROM {} WHERE workpiece = '{}'".format(table, workpiece)
		return self.conn.execute_query(sql)
	
	def countAllPiece(self, table):
		sql = "SELECT workpiece, SUM(quantity) FROM {}_orders WHERE ID IN (SELECT * FROM {}) GROUP BY workpiece;".format(self.conn.database, table)
		return self.conn.execute_query(sql)
	
	def countWare(self, warenum):
		sql = "SELECT workpiece, COUNT(*) as count FROM {}_ware{} GROUP BY workpiece".format(self.conn.database, warenum)
		return self.conn.execute_query(sql)
	

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



