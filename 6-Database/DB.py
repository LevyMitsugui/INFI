import mysql.connector;

class Database:
	def __init__(self):
		try:
			self.db = mysql.connector.connect(       								# Creates a connection to the database
					host="localhost",
					user="infi",
					password="infi2324",
					database="infi2324"												# Selects the desired database from the server
			)
			self.db.orders = []
			self.db.open = []
			self.db.order_by_num = []
			print("Connected to the database server")

		except mysql.connector.Error as err:
			print("Error connecting to database server: " + str(err))


	def insertOrder(self, client, order):
		'''
		Inserts an order to the orders table of the database

		Parameters:
		client (str): The name of the client
		order (Order): The order to be inserted

		Returns:
		None
		'''
		cursor = self.db.cursor()													#Creates a cursor object to execute queries, cursors are used to execute single queries
		sql = "INSERT INTO orders (client, number, workpiece, quantity, due_date, late_pen, early_pen) VALUES (%s, %s, %s, %s, %s, %s, %s)"
		value = (client, order.number, order.workpiece, order.quantity, order.due_date, order.late_pen, order.early_pen)
																				#Insert to the orders table the data of the order plus the ID of the desired client
		cursor.execute(sql, value)
		self.db.commit()


	def updateOrders(self):
		'''
		Updates all orders from the database

		Parameters:
		None

		Returns:
		None
		'''
		cursor = self.db.cursor()
		sql = "CREATE TEMPORARY TABLE temp SELECT * FROM orders"
		cursor.execute(sql)
		sql = "ALTER TABLE temp DROP COLUMN id"
		cursor.execute(sql)
		sql = "SELECT * FROM temp"
		cursor.execute(sql)
		self.orders = cursor.fetchall()

		sql = "DROP TABLE temp"	
		cursor.execute(sql)
		self.db.commit()


	def updateOpenOrders(self):
		'''
		Updates all pendent orders from the database sorted from smaller to larger due_date

		Parameters:
		None

		Returns:
		None
		'''
		cursor = self.db.cursor()
		sql = "CREATE TEMPORARY TABLE temp SELECT * FROM orders WHERE id IN (SELECT id FROM open)"
		cursor.execute(sql)
		sql = "ALTER TABLE temp DROP COLUMN id"
		cursor.execute(sql)
		sql = "SELECT * FROM temp ORDER BY due_date"
		cursor.execute(sql)
		self.open = cursor.fetchall()

		sql = "DROP TABLE temp"
		cursor.execute(sql)
		self.db.commit()


	def printOrders(self):
		'''
		Prints all orders from the database

		Parameters:
		None

		Returns:
		None
		'''
		
		print("\n################################### Orders #################################### \n   client | ord_num | workpiece | quantity | due_date | late_pen | early_pen")
		for x in self.orders:
			print(list(x))
		print  ("###############################################################################\n")


	def printOpen(self):
		'''
		Prints all pendent orders from the database

		Parameters:
		None

		Returns:
		None
		'''
		print("\n################################ Open Orders ################################## \n   client | ord_num | workpiece | quantity | due_date | late_pen | early_pen")
		for x in self.open:
			print(list(x))
		print  ("###############################################################################\n")


	def printOrder(self):
		'''
		Prints the last specific order gotten from the database

		Parameters:
		None

		Returns:
		None
		'''
		print("\n################################ Order Found ################################## \n   client | ord_num | workpiece | quantity | due_date | late_pen | early_pen")
		for x in self.order_by_num:
			print(list(x))
		print  ("###############################################################################\n")


	def getOrderByNum(self, client, order_number):
		'''
		Gets a specific order from the database by the client and the order number and closes it

		Parameters:
		client (str): The name of the client
		order_number (int): The number of the order

		Returns:
		None
		'''
		cursor = self.db.cursor()
		sql = "SELECT EXISTS(SELECT * FROM orders WHERE client = \"" + client + "\")"		#Check if the client exists
		cursor.execute(sql)
		c_exists = cursor.fetchall()
		if(c_exists[0][0]):
			sql = "SELECT EXISTS(SELECT * FROM orders WHERE number = " + str(order_number) + " AND client = \"" + client + "\")"
			cursor.execute(sql)
			o_exists = cursor.fetchall()
			if(o_exists[0][0]):
				sql = "SELECT * FROM orders WHERE number = " + str(order_number) + " AND client = \"" + client + "\""
				cursor.execute(sql)
				self.order_by_num = cursor.fetchall()
				cursor.execute("SET SQL_SAFE_UPDATES = 0")
				cursor.execute("DELETE FROM open WHERE id IN (SELECT id FROM orders WHERE number = " + str(order_number) + " AND client = \"" + client + "\")")
				cursor.execute("SET SQL_SAFE_UPDATES = 1")
				self.db.commit()
			else:
				print("Order doesn't exist")
		else:
			print("Client doesn't exist")

	def getMostUrgentOrder(self):
		'''
		Gets the most urgent order from the database (if due_date is the same, the order with the lower number is chosen) and closes it

		Parameters:
		None

		Returns:
		None
		'''
		cursor = self.db.cursor()
		cursor.execute("CREATE TEMPORARY TABLE temp SELECT * FROM orders WHERE id IN (SELECT id FROM open)")
		cursor.execute("SELECT MIN(due_date) FROM temp")
		min_due_date = cursor.fetchall()
		cursor.execute("SET SQL_SAFE_UPDATES = 0")
		cursor.execute("DELETE FROM temp WHERE due_date <> " + str(min_due_date[0][0]))
		self.db.commit()
		cursor.execute("DELETE FROM open WHERE id IN (SELECT MIN(id) FROM temp)")
		cursor.execute("SET SQL_SAFE_UPDATES = 1")
		cursor.execute("ALTER TABLE temp DROP COLUMN id")
		cursor.execute("SELECT * FROM temp")
		self.order_by_num = cursor.fetchall()
		cursor.execute("DROP TABLE temp")
		self.db.commit()

	# Coppied that just for testing, but it already exists in ERP Main.py
class Order:
    def __init__(self, number, workpiece, quantity, due_date, late_pen, early_pen):
        self.number = number
        self.workpiece = workpiece
        self.quantity = quantity
        self.due_date = due_date
        self.late_pen = late_pen
        self.early_pen = early_pen



############# TESTING #############

db = Database()										#Create a db, get current clients, orders and print them

order1 = Order(2, "P3", 5, 6, 12, 3)
order2 = Order(19, "P6", 1, 4, 10, 10)
# db.insertOrder("AA", order1)						#Insert order1
# db.insertOrder("BB", order2)						#Insert order2

# db.getOrderByNum("AA", 2)							#Get order1 and closes it
# db.getMostUrgentOrder()								#Get most urgent order and closes it

# 	#Get clients, orders after action
db.updateOrders()
db.printOrders()
db.updateOpenOrders()
db.printOpen()



