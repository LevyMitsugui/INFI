import mysql.connector
from mysql.connector import errorcode
from mysql.connector import pooling
import time
import datetime

class SQLConnection:
	def __init__(self, user, password):
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
	
	def execute_transaction(self, sql, dbname):
		"""
		Executes a transaction and retries it if a deadlock occurs.

		Parameters:
			cursor (Cursor): The cursor object for executing SQL queries.

		Returns:
			None
		"""
		with self.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				max_retries = 5  # Maximum number of retries
				retry_delay = 1  # Delay between retries in seconds
				for i in range(max_retries):
					try:
						# Execute the transaction
						cursor.execute("USE {}".format(dbname))
						
						cursor.execute(sql)
						conn.commit()
						break  # Exit the loop if the transaction is successful
					except mysql.connector.errors.InternalError as e:
						if e.errno == errorcode.ER_LOCK_DEADLOCK:
							if i == max_retries - 1:
								raise Exception("Failed to execute transaction after", max_retries, "retries")
							print("Deadlock occurred. Retrying in", retry_delay, "seconds...")
							time.sleep(retry_delay)
						else:
							raise


class Database:

	def __init__(self, user, password):
		'''
		Initializes a new instance of the class.

		Parameters:
		None

		Returns:
		None
		'''
		self.erp_orders = []
		self.erp_open = []
		self.erp_processing = []
		self.erp_done = []
		self.erp_order = []
		self.mes_orders = []
		self.mes_open = []
		self.mes_processing = []
		self.mes_done = []
		self.mes_order = []
		self.requests_orders = []
		self.requests_open = []
		self.requests_processing = []
		self.requests_done = []
		self.requests_order = []
		self.ware1 = []
		self.ware1_qnt = []
		self.ware2 = []
		self.ware2_qnt = []
		self.user = user
		self.password = password
		# self.database = database
		self.conn = self.__createsConnection__()
		self.__createsDatabase__()
		# self.__createsDatabase__("erp")
		
	def __createsConnection__(self):
		return SQLConnection(self.user, self.password)

	def __createsDatabase__(self):
		
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				dbname = "erp"
				for i in range(3):
					sql = "SHOW DATABASES LIKE '{}'".format(dbname)
					cursor.execute(sql)
					
					aux = cursor.fetchall()
					if not aux:	# If the database doesn't exists it will be created
						sql = "CREATE DATABASE IF NOT EXISTS {}".format(dbname)
						cursor.execute(sql)
						conn.commit()

						sql = "USE {}".format(dbname)
						cursor.execute(sql)

						if dbname == "erp":
							# sql = "CREATE TABLE IF NOT EXISTS {}_orders(id INT NOT NULL AUTO_INCREMENT, done VARCHAR(1) NOT NULL DEFAULT '', client VARCHAR(30) NOT NULL, number INT NOT NULL, workpiece VARCHAR(2) NOT NULL, quantity INT NOT NULL, due_date INT NOT NULL, late_pen INT NOT NULL, early_pen INT NOT NULL, PRIMARY KEY (id));".format(dbname)
							sql = "CREATE TABLE IF NOT EXISTS {}_orders(id INT NOT NULL AUTO_INCREMENT, done VARCHAR(1) NOT NULL DEFAULT '', admission TIME, delivery TIME, client VARCHAR(30) NOT NULL, number INT NOT NULL, workpiece VARCHAR(2) NOT NULL, quantity INT NOT NULL, due_date INT NOT NULL, late_pen INT NOT NULL, early_pen INT NOT NULL, PRIMARY KEY (id));".format(dbname)
						elif dbname == "mes":
							sql = "CREATE TABLE IF NOT EXISTS {}_orders(id INT NOT NULL AUTO_INCREMENT, done VARCHAR(1) NOT NULL DEFAULT '', delivered INT NOT NULL DEFAULT 0, start TIME, end TIME, client VARCHAR(30) NOT NULL, number INT NOT NULL, workpiece VARCHAR(2) NOT NULL, quantity INT NOT NULL, due_date INT NOT NULL, late_pen INT NOT NULL, early_pen INT NOT NULL, PRIMARY KEY (id));".format(dbname)
						else:
							sql = "CREATE TABLE IF NOT EXISTS {}_orders(id INT NOT NULL AUTO_INCREMENT, done VARCHAR(1) NOT NULL DEFAULT '', workpiece VARCHAR(2) NOT NULL, arrival TIME, start TIME, end TIME, dispatch TIME, raw_cost INT NOT NULL DEFAULT 0, PRIMARY KEY (id));".format(dbname)
						cursor.execute(sql)

						sql = "CREATE TABLE IF NOT EXISTS {}_open(id INT NOT NULL);".format(dbname)			
						cursor.execute(sql)
						
						sql = "CREATE TABLE IF NOT EXISTS {}_processing(id INT NOT NULL);".format(dbname)			
						cursor.execute(sql)

						sql = "CREATE TRIGGER IF NOT EXISTS after_order_insert AFTER INSERT  ON {}_orders FOR EACH ROW INSERT INTO {}_open VALUES (NEW.id);".format(dbname, dbname)			
						cursor.execute(sql)
						
						sql = "CREATE TRIGGER IF NOT EXISTS before_order_delete BEFORE DELETE ON {}_orders FOR EACH ROW DELETE FROM {}_open WHERE id = OLD.id;".format(dbname, dbname)
						cursor.execute(sql)

						if (dbname == "mes"):

							sql = "CREATE TABLE IF NOT EXISTS {}_ware1(workpiece VARCHAR(2) NOT NULL);".format(dbname)
							cursor.execute(sql)

							sql = "CREATE TABLE IF NOT EXISTS {}_ware2(workpiece VARCHAR(2) NOT NULL);".format(dbname)
							cursor.execute(sql)

							sql = "CREATE TABLE IF NOT EXISTS {}_in_ware_queue(conveyor INT NOT NULL, piece INT NOT NULL);".format(dbname)
							cursor.execute(sql)

							sql = "CREATE TABLE IF NOT EXISTS {}_out_ware_queue(conveyor INT NOT NULL, piece INT NOT NULL);".format(dbname)
							cursor.execute(sql)

							sql = "CREATE TABLE IF NOT EXISTS {}_machine_upd_queue(machine INT NOT NULL, tool INT NOT NULL, time INT NOT NULL, secondTime INT NOT NULL DEFAULT 0);".format(dbname)
							cursor.execute(sql)

							sql = "CREATE TABLE IF NOT EXISTS {}_gate_upd_queue(gate INT NOT NULL, piece INT NOT NULL, quantity INT NOT NULL);".format(dbname)
							cursor.execute(sql)
						elif (dbname == "requests"):
							cursor.execute("CREATE TABLE IF NOT EXISTS {}_suplier(workpiece VARCHAR(2) NOT NULL, raw_cost INT NOT NULL DEFAULT 0);".format(dbname))

						conn.commit()
					
					if not aux: # If the database doesn't exists it will be shown
						self.__fetchAll__(dbname)
					if dbname == "erp":
						dbname = "mes"
					elif dbname == "mes":
						dbname = "requests"

	
	def __fetchOrders__(self, dbname):
		self.getOrders(dbname)
		#self.__printOrders__(dbname)

	def __fetchOpen__(self, dbname):	
		self.getOpenOrders(dbname)
		#self.__printOpen__(dbname)

	def __fetchProcessing__(self, dbname):
		self.getProcessingOrders(dbname)
		#self.__printProcessing__(dbname)

	def __fetchOrdersDone__(self, dbname):
		self.getOrdersDone(dbname)
		#self.__printDone__(dbname)
	
	def __fetchAll__(self, dbname):
		self.getOrders(dbname)
		self.getOpenOrders(dbname)
		#self.__printOrders__(dbname)
		#self.__printOpen__(dbname)

	def __fetchWare__(self, warenumber):	
		self.getWare(warenumber)
		#self.__printWare__(warenumber)

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
				timeNow = datetime.datetime.now().time()
				if dbname == "erp":
					print("																					timeAdmission: ", timeNow)
					sql = "INSERT INTO {}_orders (admission, client, number, workpiece, quantity, due_date, late_pen, early_pen) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)".format(dbname)
					value = (timeNow, client, order.number, order.workpiece, order.quantity, order.due_date, order.late_pen, order.early_pen)
				# elif dbname == "mes":
				# 	sql = "INSERT INTO {}_orders (start, client, number, workpiece, quantity, due_date, late_pen, early_pen) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)".format(dbname)
				# 	value = (timeNow, client, order.number, order.workpiece, order.quantity, order.due_date, order.late_pen, order.early_pen)
				else:
					sql = "INSERT INTO {}_orders (client, number, workpiece, quantity, due_date, late_pen, early_pen) VALUES (%s, %s, %s, %s, %s, %s, %s)".format(dbname)
					value = (client, order.number, order.workpiece, order.quantity, order.due_date, order.late_pen, order.early_pen)
																						#Insert to the orders table the data of the order plus the ID of the desired client
				cursor.execute(sql, value)
				conn.commit()

		# self.__fetchOrders__(dbname)
		self.__fetchAll__(dbname)

		
	def insertRequestOrder(self, request, dbname):
		'''
		Inserts an order to the orders table of the database

		Parameters:
		order (Order): The order to be inserted

		Returns:
		None
		'''
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				sql = "USE {}".format(dbname)
				cursor.execute(sql)
				sql = "INSERT INTO {}_orders (workpiece) VALUES ('{}')".format(dbname, request['Piece'])
				# cursor.execute(sql)
				self.conn.execute_transaction(sql, dbname)
				conn.commit()

		# self.__fetchOrders__(dbname)
		self.__fetchAll__(dbname)

	def insertInQueue(self, queue, update, dbname):
		'''
		Inserts an update request to the queue table of the database

		Parameters:
		update (Dict): The update to be inserted

		Returns:
		None
		'''
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				sql = "USE {}".format(dbname)
				cursor.execute(sql)
				if(dbname == "mes"):
					if(queue == "inWH"):
						sql = "INSERT INTO mes_in_ware_queue (conveyor, piece) VALUES (%s, %s)".format(dbname)
						value = (update['conveyor'], update['piece'])
					elif (queue == "outWH"):
						sql = "INSERT INTO mes_out_ware_queue (conveyor, piece) VALUES (%s, %s)".format(dbname)
						value = (update['conveyor'], update['piece'])
					elif (queue == "machineUpd"):
						sql = "INSERT INTO mes_machine_upd_queue (machine, tool, time, secondTime) VALUES (%s, %s, %s, %s)".format(dbname)
						value = (update['machine'], update['tool'], update['time'], update['secondTime'])
					elif (queue == "gateUpd"):
						sql = "INSERT INTO mes_gate_upd_queue (gate, piece, quantity) VALUES (%s, %s, %s)".format(dbname)
						value = (update['gate'], update['piece'], update['quantity'])
				
				cursor.execute(sql, value)
				conn.commit()

	def insertInTable(self, table, columns, data, dbname):
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				sql = "USE {}".format(dbname)
				cursor.execute(sql)
				sql = "INSERT INTO {} ({}) VALUES ({})".format(table, columns, data)
				cursor.execute(sql)

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
				sql = "DROP TABLE IF EXISTS temp"
				cursor.execute(sql)
				sql = "CREATE TEMPORARY TABLE temp SELECT * FROM {}_orders".format(dbname)
				cursor.execute(sql)
				sql = "ALTER TABLE temp DROP COLUMN id"
				cursor.execute(sql)
				sql = "ALTER TABLE temp DROP COLUMN done"
				cursor.execute(sql)
				if (dbname == "mes"):
					cursor.execute("ALTER TABLE temp DROP COLUMN delivered")
					cursor.execute("ALTER TABLE temp DROP COLUMN start")
					cursor.execute("ALTER TABLE temp DROP COLUMN end")
				elif (dbname == "erp"):
					cursor.execute("ALTER TABLE temp DROP COLUMN admission")
					cursor.execute("ALTER TABLE temp DROP COLUMN delivery")
				else:
					cursor.execute("ALTER TABLE temp DROP COLUMN arrival")
					cursor.execute("ALTER TABLE temp DROP COLUMN dispatch")
					cursor.execute("ALTER TABLE temp DROP COLUMN raw_cost")
					cursor.execute("ALTER TABLE temp DROP COLUMN start")
					cursor.execute("ALTER TABLE temp DROP COLUMN end")
				sql = "SELECT * FROM temp"
				cursor.execute(sql)
				if(dbname == "erp"):
					self.erp_orders = cursor.fetchall()
					orders = self.erp_orders
				elif(dbname == "mes"):
					self.mes_orders = cursor.fetchall()
					orders = self.mes_orders
				elif(dbname == "requests"):
					self.requests_orders = cursor.fetchall()
					orders = self.requests_orders

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
				sql = "DROP TABLE IF EXISTS temp"
				cursor.execute(sql)
				sql = "CREATE TEMPORARY TABLE temp SELECT * FROM {}_orders WHERE id IN (SELECT id FROM {}_open)".format(dbname, dbname)
				cursor.execute(sql)
				sql = "ALTER TABLE temp DROP COLUMN id"
				cursor.execute(sql)
				sql = "ALTER TABLE temp DROP COLUMN done"
				cursor.execute(sql)
				if (dbname == "mes"):
					cursor.execute("ALTER TABLE temp DROP COLUMN delivered")
					cursor.execute("ALTER TABLE temp DROP COLUMN start")
					cursor.execute("ALTER TABLE temp DROP COLUMN end")
				elif (dbname == "erp"):
					cursor.execute("ALTER TABLE temp DROP COLUMN admission")
					cursor.execute("ALTER TABLE temp DROP COLUMN delivery")
				else:
					cursor.execute("ALTER TABLE temp DROP COLUMN arrival")
					cursor.execute("ALTER TABLE temp DROP COLUMN dispatch")
					cursor.execute("ALTER TABLE temp DROP COLUMN raw_cost")
					cursor.execute("ALTER TABLE temp DROP COLUMN start")
					cursor.execute("ALTER TABLE temp DROP COLUMN end")
				if (dbname != "requests"):
					sql = "SELECT * FROM temp ORDER BY due_date"
					cursor.execute(sql)
				else:
					sql = "SELECT * FROM temp"
					cursor.execute(sql)
				if (dbname == "erp"):
					self.erp_open = cursor.fetchall()
					openOrders = self.erp_open
				elif (dbname == "mes"):
					self.mes_open = cursor.fetchall()
					openOrders = self.mes_open
				elif(dbname == "requests"):
					self.requests_open = cursor.fetchall()
					openOrders = self.requests_open

				sql = "DROP TABLE temp"
				cursor.execute(sql)
				conn.commit()

				return openOrders


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
				sql = "DROP TABLE IF EXISTS temp"
				cursor.execute(sql)
				if(dbname == "erp"):
					sql = "CREATE TEMPORARY TABLE temp SELECT mp.* FROM {}_orders mp WHERE ID in (SELECT * FROM {}_processing) ORDER BY due_date".format(dbname, dbname)
				elif(dbname == "mes"):
					sql = "CREATE TEMPORARY TABLE temp SELECT mp.* FROM {}_orders mp LEFT JOIN (SELECT workpiece, COUNT(*) AS ware2_count FROM {}_ware2 GROUP BY workpiece) mw ON mp.workpiece = mw.workpiece WHERE id IN (SELECT id FROM {}_processing) AND mw.ware2_count >= quantity AND done <> 'X' ORDER BY due_date".format(dbname, dbname, dbname)
				cursor.execute(sql)
				cursor.execute("SELECT * FROM temp")
				if(dbname == "erp"):
					self.erp_order = cursor.fetchall()
				elif(dbname == "mes"):
					self.mes_order = cursor.fetchall()
				cursor.execute("DROP TABLE temp")
				conn.commit()


		if(dbname == "erp" and self.erp_order):
			self.__fetchProcessing__(dbname)
			return self.erp_order
		elif (dbname == "mes" and self.mes_order):
			self.__fetchProcessing__(dbname)
			return self.mes_order
		else:
			return None

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
				sql = "DROP TABLE IF EXISTS temp"
				cursor.execute(sql)
				sql = "CREATE TEMPORARY TABLE temp SELECT * FROM {}_orders WHERE id IN (SELECT id FROM {}_processing)".format(dbname, dbname)
				cursor.execute(sql)
				sql = "ALTER TABLE temp DROP COLUMN id"
				cursor.execute(sql)
				sql = "ALTER TABLE temp DROP COLUMN done"
				cursor.execute(sql)
				if (dbname == "mes"):
					cursor.execute("ALTER TABLE temp DROP COLUMN delivered")
					cursor.execute("ALTER TABLE temp DROP COLUMN start")
					cursor.execute("ALTER TABLE temp DROP COLUMN end")
				elif (dbname == "erp"):
					cursor.execute("ALTER TABLE temp DROP COLUMN admission")
					cursor.execute("ALTER TABLE temp DROP COLUMN delivery")
				else:
					cursor.execute("ALTER TABLE temp DROP COLUMN arrival")
					cursor.execute("ALTER TABLE temp DROP COLUMN dispatch")
					cursor.execute("ALTER TABLE temp DROP COLUMN raw_cost")
					cursor.execute("ALTER TABLE temp DROP COLUMN start")
					cursor.execute("ALTER TABLE temp DROP COLUMN end")
				if (dbname != "requests"):
					sql = "SELECT * FROM temp ORDER BY due_date"
					cursor.execute(sql)
				else:
					sql = "SELECT * FROM temp"
					cursor.execute(sql)
				if (dbname == "erp"):
					self.erp_processing = cursor.fetchall()
					processingOrders = self.erp_processing
				elif (dbname == "mes"):
					self.mes_processing = cursor.fetchall()
					processingOrders = self.mes_processing
				elif(dbname == "requests"):
					self.requests_processing = cursor.fetchall()
					processingOrders = self.requests_processing

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

				sql = "DROP TABLE IF EXISTS temp"
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
				elif(dbname == "requests"):
					self.requests_done = cursor.fetchall()
					ordersDone = self.requests_done

				sql = "DROP TABLE temp"	
				cursor.execute(sql)
				conn.commit()

				return ordersDone
			
	def getWaitingRequests(self, workpiece, oldest = False):
		'''
		Gets all waiting orders from the database

		Parameters:
		None

		Returns:
		None
		'''
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				sql = "USE requests"
				cursor.execute(sql)
				
				sql = "SELECT * FROM requests_orders WHERE workpiece = '{}' AND end IS NOT NULL AND arrival = (SELECT MIN(arrival) FROM requests_orders WHERE workpiece = '{}')".format(workpiece, workpiece)
				cursor.execute(sql)

				requests = cursor.fetchall()

				if(oldest):	#Reverses the tuple, giving the oldest first
					requests = requests[::-1]

				return cursor.fetchall()

	def getOrderByNum(self, client, number, dbname):
		'''
		Get the order from the database

		Parameters:
		client (str): The name of the client
		number (int): The number of the order

		Returns:
		tuple: The order
		'''
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				sql = "USE {}".format(dbname)
				cursor.execute(sql)

				sql = "SELECT * FROM {}_orders WHERE client = '{}' AND number = {}".format(dbname, client, number)
				cursor.execute(sql)

				return cursor.fetchall()

	def getDelivered(self, client, order_number, dbname):
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				sql = "USE {}".format(dbname)
				cursor.execute(sql)
				sql = "SELECT delivered FROM {}_orders WHERE number = ".format(dbname) + str(order_number) + " AND client = \"" + client + "\""
				cursor.execute(sql)
				return cursor.fetchall()

	def getStock(self, piece, dbname):
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				sql = "USE {}".format(dbname)
				cursor.execute(sql)
				sql = "SELECT stock FROM {}_orders WHERE workpiece = '{}'".format(dbname, piece)
				cursor.execute(sql)
				return cursor.fetchall()

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

	def getWareQueue(self, command):
		'''
		Get all input requests in the queue

		Parameters:
		None

		Returns:
		inputQueue (tuple): (workpiece, quantity)
		None: If there are no input requests in the queue
		'''
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				sql = "USE mes"
				cursor.execute(sql)
				sql = "SELECT * FROM mes_{}_ware_queue".format(command)
				cursor.execute(sql)
				return cursor.fetchall()
			
	def getMachineUpdQueue(self):
		'''
		Get all machine update requests in the queue

		Parameters:
		None

		Returns:
		machineUpdQueue (tuple): (workpiece, quantity)
		None: If there are no machine update requests in the queue
		'''
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				sql = "USE mes"
				cursor.execute(sql)
				sql = "SELECT * FROM mes_machine_upd_queue"
				cursor.execute(sql)
				return cursor.fetchall()
	
	def getGateUpdQueue(self):
		'''
		Get all gate update requests in the queue

		Parameters:
		None

		Returns:
		gateUpdQueue (tuple): (workpiece, quantity)
		None: If there are no gate update requests in the queue
		'''
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				sql = "USE mes"
				cursor.execute(sql)
				sql = "SELECT * FROM mes_gate_upd_queue"
				cursor.execute(sql)
				return cursor.fetchall()


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
			print("###############################################################################\n")
		elif(dbname == "mes"):
			print("\n################################ [MES] Orders ################################# \n   client | ord_num | workpiece | quantity | due_date | late_pen | early_pen")
			for x in self.mes_orders:
				print(list(x))
			print("###############################################################################\n")
		# elif(dbname == "requests"):
		# 	print("\n############################# [Requests] Orders ############################### \n   workpiece | material | time | tools")
		# 	for x in self.requests_orders:
		# 		print(list(x))
			# print("###############################################################################\n")


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
			print("###############################################################################\n")
		elif(dbname == "mes"):
			print("\n############################# [MES] Open Orders ############################### \n   client | ord_num | workpiece | quantity | due_date | late_pen | early_pen")
			for x in self.mes_open:
				print(list(x))
			print("###############################################################################\n")
		# elif(dbname == "requests"):
		# 	print("\n########################## [Requests] Open Orders ############################# \n   workpiece | material | time | tools")
		# 	for x in self.requests_open:
		# 		print(list(x))
			# print("###############################################################################\n")

	
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
			print("###############################################################################\n")
		elif(dbname == "mes"):
			print("\n############################# [MES] Processing Orders ############################### \n   client | ord_num | workpiece | quantity | due_date | late_pen | early_pen")
			for x in self.mes_processing:
				print(list(x))
			print("###############################################################################\n")
		# elif(dbname == "requests"):
		# 	print("\n########################## [Requests] Processing Orders ############################# \n   workpiece | material | time | tools")
		# 	for x in self.requests_processing:
		# 		print(list(x))
			# print("###############################################################################\n")

	
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
			print("###############################################################################\n")
		elif(dbname == "mes"):
			print("\n############################# [MES] Orders Done ############################### \n   client | ord_num | workpiece | quantity | due_date | late_pen | early_pen")
			for x in self.mes_done:
				print(list(x))
			print("###############################################################################\n")
		# elif(dbname == "requests"):
		# 	print("\n########################## [Requests] Orders Done ############################# \n   workpiece | material | time | tools")
		# 	for x in self.requests_done:
		# 		print(list(x))
			# print("###############################################################################\n")


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
			print("###############################################################################\n")
		elif(dbname == "mes"):
			print("\n################################ [MES] Order Found ################################## \n   client | ord_num | workpiece | quantity | due_date | late_pen | early_pen")
			for x in self.mes_order:
				print(list(x))
			print("###############################################################################\n")
		# elif(dbname == "requests"):
		# 	print("\n############################# [Requests] Order Found ############################### \n   workpiece | material | time | tools")
		# 	for x in self.requests_order:
		# 		print(list(x))
			# print("###############################################################################\n")


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
		max_retries = 5
		retry_delay = 0.5
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				for i in range(max_retries):
					try:
						sql = "USE {}".format(dbname)
						cursor.execute(sql)
						sql = "SELECT EXISTS(SELECT * FROM {}_orders WHERE client = \"".format(dbname) + client + "\" AND done <> 'X')"		#Check if the client exists
						cursor.execute(sql)
						c_exists = cursor.fetchall()
						if(c_exists[0][0]):
							sql = "SELECT EXISTS(SELECT * FROM {}_orders WHERE number = ".format(dbname) + str(order_number) + " AND client = \"" + client + "\" AND done <> 'X')"
							cursor.execute(sql)
							o_exists = cursor.fetchall()
							if(o_exists[0][0]):
								sql = "SELECT * FROM {}_orders WHERE number = ".format(dbname) + str(order_number) + " AND client = \"" + client + "\" AND done <> 'X'"
								cursor.execute(sql)
								if(dbname == "erp"):
									self.erp_order = cursor.fetchall()
								elif(dbname == "mes"):
									self.mes_order = cursor.fetchall()
								cursor.execute("SET SQL_SAFE_UPDATES = 0")
								sql = "SELECT id FROM {}_orders WHERE number = ".format(dbname) + str(order_number) + " AND client = \"" + client + "\" AND done <> 'X'"
								cursor.execute(sql)
								process_id = cursor.fetchall()
								cursor.execute("DELETE FROM {}_open WHERE id = {}".format(dbname, process_id[0][0]))
								cursor.execute("INSERT INTO {}_processing(id) VALUES ({})".format(dbname, process_id[0][0]))
								cursor.execute("SET SQL_SAFE_UPDATES = 1")
								conn.commit()

							else:
								print("Order doesn't exist")
								return None
						else:
							print("Client doesn't exist")
							return None
						break
					except Exception as e:
						if i == max_retries - 1:
							raise Exception("Failed to execute queries after",max_retries, "retries")
						print("Failed to execute queries. Retrying in", retry_delay, "seconds...")
						time.sleep(retry_delay)
		
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
		max_retries = 5
		retry_delay = 0.5
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				for i in range(max_retries):
					try:
						sql = "USE {}".format(dbname)
						cursor.execute(sql)

						sql = "SELECT EXISTS(SELECT * FROM {}_orders WHERE id IN (SELECT id FROM {}_open))".format(dbname, dbname)		#Check if any order exists
						cursor.execute(sql)
						exists = cursor.fetchall()
						if(exists[0][0]):
							sql = "DROP TABLE IF EXISTS temp"
							cursor.execute(sql)
							cursor.execute("CREATE TEMPORARY TABLE temp SELECT * FROM {}_orders WHERE id IN (SELECT id FROM {}_open)".format(dbname, dbname))
							cursor.execute("SELECT MIN(due_date) FROM temp")
							min_due_date = cursor.fetchall()
							cursor.execute("SET SQL_SAFE_UPDATES = 0")
							cursor.execute("DELETE FROM temp WHERE due_date <> " + str(min_due_date[0][0]))
							conn.commit()
							sql = "SELECT MIN(id) FROM temp"
							cursor.execute(sql)
							min_id = cursor.fetchall()
							cursor.execute("DELETE FROM {}_open WHERE id = {}".format(dbname, min_id[0][0]))
							cursor.execute("INSERT INTO {}_processing(id) VALUES ({})".format(dbname, min_id[0][0]))
							cursor.execute("SET SQL_SAFE_UPDATES = 1")
							cursor.execute("ALTER TABLE temp DROP COLUMN id")
							cursor.execute("ALTER TABLE temp DROP COLUMN done")
							if (dbname == "mes"):
								cursor.execute("ALTER TABLE temp DROP COLUMN delivered")
								cursor.execute("ALTER TABLE temp DROP COLUMN start")
								cursor.execute("ALTER TABLE temp DROP COLUMN end")
							elif (dbname == "erp"):
								cursor.execute("ALTER TABLE temp DROP COLUMN admission")
								cursor.execute("ALTER TABLE temp DROP COLUMN delivery")
							else:
								cursor.execute("ALTER TABLE temp DROP COLUMN arrival")
								cursor.execute("ALTER TABLE temp DROP COLUMN dispatch")
								cursor.execute("ALTER TABLE temp DROP COLUMN raw_cost")
								cursor.execute("ALTER TABLE temp DROP COLUMN start")
								cursor.execute("ALTER TABLE temp DROP COLUMN end")
							sql = "SELECT * FROM temp"
							cursor.execute(sql)
							if(dbname == "erp"):
								self.erp_order = cursor.fetchall()
							elif(dbname == "mes"):
								self.mes_order = cursor.fetchall()
							cursor.execute("DROP TABLE temp")
							conn.commit()

						else:
							# print("[Database] No order being processed in mySQL database")
							return None
						
						break
					except Exception as e:
						if i == max_retries - 1:
							raise Exception("Failed to execute queries after",max_retries, "retries")
						print("Failed to execute queries. Retrying in", retry_delay, "seconds...")
						time.sleep(retry_delay)
		
		self.__fetchOpen__(dbname)

		if(dbname == "erp"):
			return self.erp_order
		elif(dbname == "mes"):
			return self.mes_order
		
		
	def processRequestOrder(self, dbname):
		'''
		Gets the most urgent order from the database (if due_date is the same, the order with the lower number is chosen) and closes it

		Parameters:
		None

		Returns:
		List: The most urgent order
		None: If no order was found
		'''
		max_retries = 5
		retry_delay = 0.5
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				for i in range(max_retries):
					try:
						sql = "USE {}".format(dbname)
						cursor.execute(sql)
						cursor.execute("SELECT MIN(id) FROM (SELECT * FROM {}_orders ord WHERE id IN (SELECT id FROM {}_open op)) res").format(dbname, dbname)
						min_id = cursor.fetchall()
						cursor.execute("SET SQL_SAFE_UPDATES = 0")
						cursor.execute("DELETE FROM {}_open WHERE id = {}".format(dbname, min_id[0][0]))
						cursor.execute("INSERT INTO {}_processing(id) VALUES ({})".format(dbname, min_id[0][0]))
						cursor.execute("SET SQL_SAFE_UPDATES = 1")
						cursor.execute("SELECT * FROM {}_orders WHERE id = {}".format(dbname, min_id[0][0]))
						self.requests_order = cursor.fetchall()
						conn.commit()
						
						break
					except Exception as e:
						if i == max_retries - 1:
							raise Exception("Failed to execute queries after",max_retries, "retries")
						print("Failed to execute queries. Retrying in", retry_delay, "seconds...")
						time.sleep(retry_delay)
		
		self.__fetchOpen__(dbname)
		return self.requests_order
	
	def processRequestByPiece(self, workpiece, dbname):
		'''
		Gets the most urgent order from the database (if due_date is the same, the order with the lower number is chosen) and closes it

		Parameters:
		None

		Returns:
		List: The most urgent order
		None: If no order was found
		'''
		max_retries = 5
		retry_delay = 0.5
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				for i in range(max_retries):
					try:
						conn.autocommit = False
						sql = "USE {}".format(dbname)
						cursor.execute(sql)

					# sql = "SELECT EXISTS(SELECT * FROM {}_orders WHERE workpiece = '{}' AND id IN (SELECT id FROM {}_open)) FOR UPDATE".format(dbname, workpiece, dbname)		#Check if any order exists
					# cursor.execute(sql)
					# exists = cursor.fetchall()
					# if(exists[0][0]):
						# sql = "DROP TABLE IF EXISTS temp"
						# cursor.execute(sql)
						cursor.execute("SELECT MIN(id) FROM {}_orders WHERE workpiece = '{}' AND id IN (SELECT id FROM {}_open) FOR UPDATE".format(dbname, workpiece, dbname))
						# cursor.execute("CREATE TEMPORARY TABLE temp SELECT * FROM {}_orders WHERE workpiece = '{}' AND id IN (SELECT id FROM {}_open)".format(dbname, workpiece, dbname))
						# cursor.execute("SELECT MIN(id) FROM temp")
						min_id = cursor.fetchall()
						cursor.execute("SET SQL_SAFE_UPDATES = 0")
						# cursor.execute("DELETE FROM temp WHERE id <> " + str(min_id[0][0]))
						# conn.commit()
						if(min_id[0][0] != None):
							cursor.execute("DELETE FROM {}_open WHERE id = {}".format(dbname, min_id[0][0]))
							cursor.execute("INSERT INTO {}_processing(id) VALUES ({})".format(dbname, min_id[0][0]))
							cursor.execute("SET SQL_SAFE_UPDATES = 1")
							# cursor.execute("SELECT * FROM temp")
							cursor.execute("SELECT * FROM {}_orders WHERE id = {}".format(dbname, min_id[0][0]))
							self.requests_order = cursor.fetchall()
						else:
							self.requests_order = None
						# cursor.execute("DROP TABLE temp")
						conn.commit()

					# else:
					# 	# print("[Database] No order being processed in mySQL database")
					# 	return None
						
						break
					except Exception as e:
						# conn.rollback()
						if i == max_retries - 1:
							raise Exception("Failed to execute queries after",max_retries, "retries")
						print("Failed to execute queries. Retrying in", retry_delay, "seconds...")
						time.sleep(retry_delay)
		
		self.__fetchOpen__(dbname)
		return self.requests_order
	
	
	def processWareQueue(self, command, update):
		'''
		Remove the ware operation request from the database queue

		Parameters:
		command (str): The type of operation to be executed (ware in or out)
		update (dict): A dictionary containing the machine, tool, and time values.

		Returns:
		List: The request removed
		None: If no request was found
		'''
		max_retries = 5
		retry_delay = 0.5
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				for i in range(max_retries):
					try:
						sql = "USE mes"
						cursor.execute(sql)
						
						sql = "SELECT EXISTS(SELECT * FROM mes_{}_ware_queue WHERE conveyor = {} AND piece = {})".format(command, update['conveyor'], update['piece'])		#Check if any order exists
						cursor.execute(sql)
						exists = cursor.fetchall()
						if(exists[0][0]):
							cursor.execute("SELECT * FROM mes_{}_ware_queue WHERE conveyor = {} AND piece = {}".format(command, update['conveyor'], update['piece']))		#Check if any order exists
							updateTup = []
							updateTup = cursor.fetchall()
							cursor.execute("SET SQL_SAFE_UPDATES = 0")
							cursor.execute("DELETE FROM mes_{}_ware_queue WHERE conveyor = {} AND piece = {}".format(command, update['conveyor'], update['piece']))
							cursor.execute("SET SQL_SAFE_UPDATES = 1")
							conn.commit()
							return updateTup
						
						else:
							# print("[Database] No order being processed in mySQL database")
							return None
						
						break
					except Exception as e:
						if i == max_retries - 1:
							raise Exception("Failed to execute queries after",max_retries, "retries")
						print("Failed to execute queries. Retrying in", retry_delay, "seconds...")
						time.sleep(retry_delay)
			
	def processMachineUpdQueue(self, update):
		"""
		Remove the machine update from the database queue.

		Parameters:
		update (dict): A dictionary containing the machine, tool, and time values.

		Returns:
		List: The machine update removed
		None: If no machine update exists in queue.
		"""
		max_retries = 5
		retry_delay = 0.5
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				for i in range(max_retries):
					try:
						sql = "USE mes"
						cursor.execute(sql)
						
						sql = "SELECT EXISTS(SELECT * FROM mes_machine_upd_queue WHERE machine = {} AND tool = {} AND time = {})".format(update['machine'], update['tool'], update['time'])		#Check if any order exists
						cursor.execute(sql)
						exists = cursor.fetchall()
						if(exists[0][0]):
							cursor.execute("SELECT * FROM mes_machine_upd_queue WHERE machine = {} AND tool = {} AND time = {}".format(update['machine'], update['tool'], update['time']))		#Check if any order exists
							updateTup = []
							updateTup = cursor.fetchall()
							cursor.execute("SET SQL_SAFE_UPDATES = 0")
							cursor.execute("DELETE FROM mes_machine_upd_queue WHERE machine = {} AND tool = {} AND time = {}".format(update['machine'], update['tool'], update['time']))
							cursor.execute("SET SQL_SAFE_UPDATES = 1")
							conn.commit()
							return updateTup
						
						else:
							# print("[Database] No order being processed in mySQL database")
							return None
						
						break
					except Exception as e:
						if i == max_retries - 1:
							raise Exception("Failed to execute queries after",max_retries, "retries")
						print("Failed to execute queries. Retrying in", retry_delay, "seconds...")
						time.sleep(retry_delay)
	
	def processGateUpdQueue(self, update):
		"""
		Get the gate update queue from the database.

		Parameters:
		update (dict): A dictionary containing the gate, piece, and quantity values.

		Returns:
		List: The gate update removed
		None: If no gate update exists in queue.
		"""
		max_retries = 5
		retry_delay = 0.5
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				for i in range(max_retries):
					try:
						sql = "USE mes"
						cursor.execute(sql)
						
						sql = "SELECT EXISTS(SELECT * FROM mes_gate_upd_queue WHERE gate = {} AND piece = {} AND quantity = {})".format(update['gate'], update['piece'], update['quantity'])		#Check if any order exists
						cursor.execute(sql)
						exists = cursor.fetchall()
						if(exists[0][0]):
							cursor.execute("SELECT * FROM mes_gate_upd_queue WHERE gate = {} AND piece = {} AND quantity = {}".format(update['gate'], update['piece'], update['quantity']))	
							updateTup = []
							updateTup = cursor.fetchall()
							cursor.execute("SET SQL_SAFE_UPDATES = 0")
							cursor.execute("DELETE FROM mes_gate_upd_queue WHERE gate = {} AND piece = {} AND quantity = {}".format(update['gate'], update['piece'], update['quantity']))
							cursor.execute("SET SQL_SAFE_UPDATES = 1")
							conn.commit()
							return updateTup
						
						else:
							# print("[Database] No order being processed in mySQL database")
							return None
						
						break
					except Exception as e:
						if i == max_retries - 1:
							raise Exception("Failed to execute queries after",max_retries, "retries")
						print("Failed to execute queries. Retrying in", retry_delay, "seconds...")
						time.sleep(retry_delay)
	
	def returnRequestByPiece(self, workpiece, dbname):
		'''
		Gets the most urgent order from the database (if due_date is the same, the order with the lower number is chosen) and closes it

		Parameters:
		None

		Returns:
		List: The most urgent order
		None: If no order was found
		'''
		max_retries = 5
		retry_delay = 0.5
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				for i in range(max_retries):
					try:
						sql = "USE {}".format(dbname)
						cursor.execute(sql)

						sql = "SELECT EXISTS(SELECT * FROM {}_orders WHERE workpiece = '{}' AND id IN (SELECT id FROM {}_processing))".format(dbname, workpiece, dbname)		#Check if any order exists
						cursor.execute(sql)
						exists = cursor.fetchall()
						if(exists[0][0]):
							sql = "DROP TABLE IF EXISTS temp"
							cursor.execute(sql)
							cursor.execute("CREATE TEMPORARY TABLE temp SELECT * FROM {}_orders WHERE workpiece = '{}' AND id IN (SELECT id FROM {}_processing)".format(dbname, workpiece, dbname))
							cursor.execute("SELECT MAX(id) FROM temp")
							max_id = cursor.fetchall()
							
							cursor.execute("SET SQL_SAFE_UPDATES = 0")
							cursor.execute("DELETE FROM temp WHERE id <> {}".format(max_id[0][0]))
							cursor.execute("DELETE FROM {}_processing WHERE id = {}".format(dbname, max_id[0][0]))
							cursor.execute("INSERT INTO {}_open(id) VALUES ({})".format(dbname, max_id[0][0]))
							cursor.execute("SET SQL_SAFE_UPDATES = 1")
							conn.commit()
							
							cursor.execute("ALTER TABLE temp DROP COLUMN id")
							cursor.execute("ALTER TABLE temp DROP COLUMN done")
							cursor.execute("ALTER TABLE temp DROP COLUMN arrival")
							cursor.execute("ALTER TABLE temp DROP COLUMN dispatch")
							cursor.execute("ALTER TABLE temp DROP COLUMN raw_cost")
							cursor.execute("ALTER TABLE temp DROP COLUMN start")
							cursor.execute("ALTER TABLE temp DROP COLUMN end")
							cursor.execute("SELECT * FROM temp")
							self.requests_order = cursor.fetchall()
							cursor.execute("DROP TABLE temp")
							conn.commit()

						else:
							# print("[Database] No order being processed in mySQL database")
							return None
						
						break
					except Exception as e:
						if i == max_retries - 1:
							raise Exception("Failed to execute queries after",max_retries, "retries")
						print("Failed to execute queries. Retrying in", retry_delay, "seconds...")
						time.sleep(retry_delay)
		
		self.__fetchOpen__(dbname)
		return self.requests_order
	
	def setRequestReady(self, workpiece, dbname):
		'''
		Sets a request as done in the database

		Parameters:
		request (dic): The request to be set as done

		Returns:
		None
		'''
		max_retries = 5
		retry_delay = 0.5
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				for i in range(max_retries):
					try:
						sql = "USE {}".format(dbname)
						cursor.execute(sql)
						sql = "SELECT MIN(id) FROM {}_orders WHERE workpiece = '{}'".format(dbname, workpiece) + " AND id IN (SELECT id FROM {}_processing)".format(dbname)
						cursor.execute(sql)
						min_id = cursor.fetchall()
						if len(min_id) > 0:
							min_id = min_id[0][0]
							if(min_id != None):
								sql = "UPDATE {}_orders SET done = 'X' WHERE id = {}".format(dbname, min_id)
								cursor.execute(sql)
								conn.commit()
								sql = "DELETE FROM {}_processing WHERE id = {}".format(dbname, min_id)
								cursor.execute(sql)
								conn.commit()
						break
					except Exception as e:
						if i == max_retries - 1:
							raise Exception("Failed to execute queries after",max_retries, "retries")
						print("Failed to execute queries. Retrying in", retry_delay, "seconds...")
						time.sleep(retry_delay)
		
		self.__fetchOrdersDone__(dbname)
		
	def setOrderDone(self, client, order_number, dbname):
		'''
		Sets an order as done in the database

		Parameters:
		client (str): The name of the client
		order_number (int): The number of the order

		Returns:
		None
		'''
		max_retries = 5
		retry_delay = 0.5
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				for i in range(max_retries):
					try:
						sql = "USE {}".format(dbname)
						cursor.execute(sql)
						sql = "SELECT EXISTS (SELECT * FROM {}_orders WHERE id IN (SELECT id FROM {}_processing) AND number = ".format(dbname, dbname) + str(order_number) + " AND client = \"" + client + "\")"
						cursor.execute(sql)
						exists = cursor.fetchall()
						if(exists[0][0]):
							if dbname == "erp":
								# cursor.execute("SELECT admission FROM {}_orders WHERE number = ".format(dbname) + str(order_number) + " AND client = \"" + client + "\"")
								# admissionTime = cursor.fetchall()
								# timeAdmission = datetime.datetime.strptime(admissionTime[0][0], '%H:%M:%S')
								timeNow = datetime.datetime.now().time()
								# print("																					timeAdmission: ", timeAdmission)
								# print("																					timeNow: ", timeNow)
								# timeDiff = datetime.datetime.strptime(timeNow, '%H:%M:%S') - datetime.datetime.strptime(admissionTime[0][0], '%H:%M:%S')
								# print("																					timeElapsed: ", timeDiff)
								sql = "UPDATE {}_orders SET done = 'X', delivery = '{}' WHERE number = ".format(dbname, timeNow) + str(order_number) + " AND client = \"" + client + "\" AND done <> 'X'"
								cursor.execute(sql)
							elif dbname == "mes":
								# cursor.execute("SELECT start FROM {}_orders WHERE number = ".format(dbname) + str(order_number) + " AND client = \"" + client + "\"")
								# admissionTime = cursor.fetchall()
								# timeAdmission = datetime.datetime.strptime(admissionTime[0][0], '%H:%M:%S')
								timeNow = datetime.datetime.now().time()
								# print("																					timeAdmission: ", timeAdmission)
								# print("																					timeNow: ", timeNow)
								# timeDiff = datetime.datetime.strptime(timeNow, '%H:%M:%S') - datetime.datetime.strptime(admissionTime[0][0], '%H:%M:%S')
								# print("																					timeElapsed: ", timeDiff)
								sql = "UPDATE {}_orders SET done = 'X', end = '{}' WHERE number = ".format(dbname, timeNow) + str(order_number) + " AND client = \"" + client + "\" AND done <> 'X'"
								cursor.execute(sql)
							else:
								sql = "UPDATE {}_orders SET done = 'X' WHERE number = ".format(dbname) + str(order_number) + " AND client = \"" + client + "\" AND done <> 'X'"
								cursor.execute(sql)
							conn.commit()
							sql = "DELETE FROM {}_processing WHERE id IN (SELECT id FROM {}_orders WHERE number = ".format(dbname, dbname) + str(order_number) + " AND client = \"" + client + "\")"
							cursor.execute(sql)
							conn.commit()
							return timeDiff.total_seconds()
						else:
							return None
						break
					except Exception as e:
						if i == max_retries - 1:
							raise Exception("Failed to execute queries after",max_retries, "retries")
						print("Failed to execute queries. Retrying in", retry_delay, "seconds...")
						time.sleep(retry_delay)
		
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
					res = True
				else:
					sql = "SELECT EXISTS (SELECT * FROM mes_ware{} WHERE workpiece = '{}')".format(warenum, workpiece)
					cursor.execute(sql)
					exists = cursor.fetchall()
					if exists[0][0]:
						sql = "DELETE FROM mes_ware{} WHERE workpiece = '{}' LIMIT 1".format(warenum, workpiece)
						cursor.execute(sql)
						res = True
					else:
						res = False
				conn.commit()
				return res

				# self.__fetchWare__(warenum)

	def updateDeliveredPieces(self, client, order_number, quantity, dbname):
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				sql = "USE {}".format(dbname)
				cursor.execute(sql)
				sql = "UPDATE {}_orders SET delivered = (delivered + {}) WHERE number = ".format(dbname, quantity) + str(order_number) + " AND client = \"" + client + "\""
				cursor.execute(sql)
				conn.commit()

	def updateColumn(self, table, column, value, dbname, id = None, condition = None):
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				sql = "USE {}".format(dbname)
				cursor.execute(sql)
				if(type(id) != int):
					sql = "SELECT MIN(id) FROM {}_{} WHERE {}".format(dbname, table, condition)
					# print(sql)
					cursor.execute(sql)
					id = cursor.fetchall()[0][0]
				# id_str = "{}".format(id) if type(id) == int else "(SELECT MIN(id) FROM {}_processing WHERE {})".format(dbname, condition)
				value_str = "'{}'" if (type(value) == str and value != "CURRENT_TIME()") else "{}"
				cursor.execute("SET SQL_SAFE_UPDATES = 0")
				sql = "UPDATE {}_{} SET {} = ".format(dbname, table, column) + value_str.format(value) + " WHERE id = {}".format(id)
				# print(sql)
				cursor.execute(sql)
				cursor.execute("SET SQL_SAFE_UPDATES = 1")
				conn.commit()
				sql = "SELECT {} FROM {}_{} WHERE id = {}".format(column, dbname, table, id)
				# print(sql)
				cursor.execute(sql)
				return cursor.fetchall()[0][0]

	def countPiece(self, workpiece, table, dbname):
		'''
		Returns the quantity of the selected workpiece in the selected warehouse

		Parameters:
		workpiece (str): The name of the workpiece
		warenum (int): The number of the warehouse

		Returns:
		int: The quantity of the workpiece in the warehouse
		'''
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				sql = "USE {}".format(dbname)
				cursor.execute(sql)
				table_str = " WHERE ID IN (SELECT * FROM {}_{})".format(dbname, table) if (table != "") else ""
				aggregate = "COUNT(*)" if dbname == "requests" else "SUM(quantity)"
				sql = "SELECT workpiece, " + aggregate + " FROM {}_orders".format(dbname) + table_str + "AND workpiece = '{}'".format(workpiece) + " GROUP BY workpiece ORDER BY workpiece"
				cursor.execute(sql)
				return cursor.fetchall()
	
	def countAllPieces(self, table, dbname, done = False):
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				sql = "USE {}".format(dbname)
				cursor.execute(sql)
				extra_str = " WHERE" if (done or table != "") else ""
				table_str = " ID IN (SELECT * FROM {}_{})".format(dbname, table) if (table != "") else ""
				or_str = " OR" if (done and table != "") else ""
				done_str = " done = 'X'" if done else ""
				aggregate = "COUNT(*)" if dbname == "requests" else "SUM(quantity)"
				sql = "SELECT workpiece, " + aggregate + " FROM {}_orders".format(dbname) + extra_str + table_str + or_str + done_str + " GROUP BY workpiece ORDER BY workpiece"
				cursor.execute(sql)
				return cursor.fetchall()
	
	def countWare(self, warenum, dbname, workpiece = ""):
		with self.conn.get_connection() as conn:											# Connects to the server
			with conn.cursor() as cursor:
				sql = "USE {}".format(dbname)
				cursor.execute(sql)
				piece_str = " WHERE workpiece = '{}'".format(workpiece) if workpiece != "" else ""
				sql = "SELECT workpiece, COUNT(*) as count FROM {}_ware{}".format(dbname, warenum) + piece_str + " GROUP BY workpiece"
				cursor.execute(sql)
				return cursor.fetchall()
			