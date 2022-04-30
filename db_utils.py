import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode
from datetime import datetime


try:
	connection = mysql.connector.connect(
		host='localhost',
	    database='rse_local',
	    user='root',
	    password='root')
	connection_status = True
except Error:
	connection_status = False


# if connection_status:
# 	cursor = connection.cursor(prepared=True)
# 	query = "SELECT name FROM skill"
# 	cursor.execute(query)
# 	names = cursor.fetchall()
# 	result = [] 
# 	for t in names: 
# 	    for x in t: 
# 	        result.append(x) 
# 	print(result)
# else:
# 	print("connection failed")

def save_data_db(data):
	# data = {"data":{"addresses":[],"file_details":{"file_extension":".pdf","filename":"Vinisha+Venugopal_Software+Resume","filesize":80651},"person_details":{"contacts":["281-435-8709"],"emails":["vinishavenu@utexas.edu"],"name":"Vinisha Venugopal"}},"status":"success"}
	if connection_status:
		insert_data = insert_into_resume(data)
		return insert_data
	return {"status": "db connection fail."}


def insert_into_resume(data):
	dl = []
	# import pdb; pdb.set_trace()
	dl.append(data.get("person_details").get("name"))
	dl.append(data.get("person_details").get("emails")[0])
	dl.append(data.get("person_details").get("contacts")[0])
	now = datetime.now()
	str_time = now.strftime("%Y-%m-%d %H:%M:%S")
	dl.append(str_time)
	dl.append(str_time)
	dl.append(str_time)
	cursor = connection.cursor(prepared=True)
	sql_insert_query ="""INSERT INTO `resume`(`userId`,`folderId`,`first_name`,`middle_name`,`last_name`,`email_id`,`phone_number`,`address`,`zip_code`,`experience`,`current_role`,`previous_role`,`degree_type`,`institution_name`,`specialization`,`status`,`deletedAt`,`createdAt`,`updatedAt`,`cityId`,`stateId`,`countryId`,`visaTagId`,`folderFileId`)VALUES (1,1,%s," "," ",%s,%s," "," ",1," "," "," "," "," ",1,%s,%s,%s,1,1,1,1,1)"""
	try:
		result  = cursor.execute(sql_insert_query, dl)
		connection.commit()
		print(result)
		return {"status": "Record inserted successfully into word table."}
	except Error:
		print(Error)
		return {"status": "resume insert db_query fail"}




