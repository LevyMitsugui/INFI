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
			print("Connected to the database server")
		except mysql.connector.Error as err:
			print("Error connecting to database server: " + err)

	def insertClient(self, clientName):
		cursor = self.db.cursor()													#Creates a cursor object to execute queries, cursors are used to execute single queries
																											#but it is said that cursors can lower the performance of the database..
		sql = "INSERT INTO clients (name) VALUES (%s)"								#Insert to the clients table the name of the client
		value = (clientName)
		cursor.execute(sql, value)													#Execute the query and store the result at cursor
		self.db.commit()															#Commit the changes, otherwise nothing happens at mysql server


	def insertOrder(self, client, order):
		cursor = self.db.cursor()
		client = "\""+client+"\""													#Transform the name of client, as the query needs to have the name in quotes
		sql = "SELECT EXISTS(SELECT * FROM clients WHERE name = " + client + ")"	#Check if the client exists
		cursor.execute(sql)
		exists = cursor.fetchall()													#Fetches all rows of a query result and return as a tuple
		if(exists[0][0]):
			sql = "SELECT id FROM clients WHERE name = " + client					#Search the clients name at the table and get its ID
			cursor.execute(sql)
			result = cursor.fetchall()												
			sql = "INSERT INTO orders (number, client_id, workpiece, quantity, due_date, late_pen, early_pen) VALUES (%s, %s, %s, %s, %s, %s, %s)"
			value = (order.number, result[0][0], order.workpiece, order.quantity, order.due_date, order.late_pen, order.early_pen)
																					#Insert to the orders table the data of the order plus the ID of the desired client
			cursor.execute(sql, value)
			self.db.commit()
		else:
			print("Client doesn't exist")

	def insertClient(self, client):
		cursor = self.db.cursor()
		client = [client]																	#Transform the name of client, as the query needs to have the name in quotes
		sql = "SELECT EXISTS(SELECT * FROM clients WHERE name = \"" + client[0] + "\")"		#Check if the client exists
		cursor.execute(sql)
		exists = cursor.fetchall()
		if(exists[0][0]):
			print("Client already exists")
		else:
			sql = "INSERT INTO clients (name) VALUES (%s)"									#Insert to the clients table the name of the client
			value = client
			cursor.execute(sql, value)
			self.db.commit()



	def getOrderByNum(self, client, order_number):
		cursor = self.db.cursor()
		client = [client]																	#Transform the name of client, as the query needs to have the name in quotes
		sql = "SELECT EXISTS(SELECT * FROM clients WHERE name = \"" + client[0] + "\")"		#Check if the client exists
		cursor.execute(sql)
		c_exists = cursor.fetchall()
		if(c_exists[0][0]):
			sql = "SELECT id FROM clients WHERE name = \"" + client[0] + "\""				
			cursor.execute(sql)
			c_id = cursor.fetchall()
			sql = "SELECT EXISTS(SELECT * FROM orders WHERE number = " + str(order_number) + " AND client_id = " + str(c_id[0][0]) + ")"
			cursor.execute(sql)
			o_exists = cursor.fetchall()
			if(o_exists[0][0]):
				sql = "SELECT * FROM orders WHERE number = " + str(order_number) + " AND client_id = " + str(c_id[0][0])
				cursor.execute(sql)
				self.order = cursor.fetchall()
				self.order = db.filterOrder(self.order)
			else:
				print("Order doesn't exist")
		else:
			print("Client doesn't exist")

	def getOrders(self):
		cursor = self.db.cursor()
		sql = "CREATE TEMPORARY TABLE temp SELECT * FROM orders"							#Creates a temporary table to store the result of the query
		cursor.execute(sql)
		sql = "ALTER TABLE temp DROP COLUMN client_id, DROP COLUMN id"						#Drops the columns that are not needed (leave only relevant data)
		cursor.execute(sql)
		sql = "SELECT * FROM temp"															#Selects all rows from the temporary table
		cursor.execute(sql)
		self.orders = cursor.fetchall()
		sql = "DROP TABLE temp"																#Drops the temporary table
		cursor.execute(sql)
		self.db.commit()

	def getClients(self):
		cursor = self.db.cursor()
		sql = "CREATE TEMPORARY TABLE temp SELECT * FROM clients"							#Creates a temporary table to store the result of the query
		cursor.execute(sql)
		sql = "ALTER TABLE temp DROP COLUMN id"												#Drops the columns that are not needed (leave only relevant data)
		cursor.execute(sql)
		sql = "SELECT * FROM clients"														#Selects all rows from the temporary table
		cursor.execute(sql)
		self.clients = cursor.fetchall()
		sql = "DROP TABLE temp"																#Drops the temporary table
		cursor.execute(sql)
		self.db.commit()

	def printOrders(self):
		print("\n############################# Orders ############################## \n  ord_num | workpiece | quantity | due_date | late_pen | early_pen")
		for x in self.orders:
			print(x)
		print("###################################################################\n")

	def printClients(self):
		print("\n########## Clients ########## \n name")
		for x in self.clients:
			print(x)
		print("#############################\n")

	def printOrder(self):
		print("Order found:" + str(self.order[0]))

	def filterOrder(self, order):
		cursor = self.db.cursor()
		ord_client = order[0][1]
		ord_number = order[0][2]
		sql = "CREATE TEMPORARY TABLE temp SELECT * FROM orders WHERE number = " + str(ord_number) + " AND client_id = " + str(ord_client)							#Creates a temporary table to store the result of the query
		cursor.execute(sql)
		sql = "ALTER TABLE temp DROP COLUMN client_id, DROP COLUMN id"						#Drops the columns that are not needed (leave only relevant data)
		cursor.execute(sql)
		sql = "SELECT * FROM temp"															#Selects all rows from the temporary table
		cursor.execute(sql)
		filtered_order = cursor.fetchall()
		sql = "DROP TABLE temp"																#Drops the temporary table
		cursor.execute(sql)
		self.db.commit()
		return filtered_order



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
	#Create a db, get current clients, orders and print them
db = Database()
db.getOrders()
db.getClients()
db.printClients()
db.printOrders()

# db.insertClient("AA")
# db.insertClient("BB")

# 	#Create and insert 2 different orders
order1 = Order(2, "P3", 5, 6, 12, 3)
# order2 = Order(19, "P6", 1, 4, 10, 10)
# db.insertOrder("AA", order1)
# db.insertOrder("BB", order2)

# 	#Get clients, orders after insertion and print them
# db.getClients()
# db.getOrders()
# db.printClients()
# db.printOrders()

db.getOrderByNum("AA", 2)
db.printOrder()



