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

def save_data_db(data, db_skills_dict):
	# data = {"data":{"addresses":[],"file_details":{"file_extension":".pdf","filename":"Vinisha+Venugopal_Software+Resume","filesize":80651},"person_details":{"contacts":["281-435-8709"],"emails":["vinishavenu@utexas.edu"],"name":"Vinisha Venugopal"}},"status":"success"}
	data_ = {}
	if connection_status:
		insert_resume_data = insert_into_resume(data)
		data_["insert_resume_data"] = insert_resume_data
		if insert_resume_data.get("status") == "success":
			insert_skills_data = insert_into_skills(data, db_skills_dict, insert_resume_data.get("id"))
			data_["insert_skills_data"] = insert_skills_data


		return data_
	return {"status": "db connection fail."}


def insert_into_resume(data):
	dl = []
	dl.append(data.get("person_details").get("name"))
	dl.append(data.get("person_details").get("emails")[0])
	dl.append(data.get("person_details").get("contacts")[0])
	if data.get("addresses"):
		dl.append(data.get("addresses")[0])
	else:
		dl.append("")
	now = datetime.now()
	str_time = now.strftime("%Y-%m-%d %H:%M:%S")
	dl.append(str_time)
	dl.append(str_time)
	dl.append(str_time)
	if data.get("visatags"):
		dl.append(data.get("visatags")[1])
	else:
		dl.append(1)
	try:
		cursor = connection.cursor(prepared=True)
		sql_insert_query ="""INSERT INTO `resume`(`userId`,`folderId`,`first_name`,`middle_name`,`last_name`,`email_id`,`phone_number`,`address`,`zip_code`,`experience`,`current_role`,`previous_role`,`degree_type`,`institution_name`,`specialization`,`status`,`deletedAt`,`createdAt`,`updatedAt`,`cityId`,`stateId`,`countryId`,`visaTagId`,`folderFileId`)VALUES (1,1,%s," "," ",%s,%s,%s," ",1," "," "," "," "," ",1,%s,%s,%s,1,1,1,%s,1)"""
		result  = cursor.execute(sql_insert_query, dl)
		connection.commit()
		print(result)
		return {"status": "success", "comment": "Record inserted successfully into resume table.", "id": cursor.lastrowid}
	except Error:
		print(Error)
		return {"status": "fail", "comment": "resume insert db_query fail"}


def insert_into_skills(data, db_skills_dict, resume_id):
	data =  data.get("skills")
	dl = []
	for k, v in data.items():
		if v > 1:
			dl.append((resume_id, db_skills_dict.get(k), 1))
		else:
			dl.append((resume_id, db_skills_dict.get(k), 0))
	values = ', '.join(map(str, dl))

	try:
		cursor = connection.cursor(prepared=True)
		sql_insert_query ="""INSERT INTO `resume_skill`(`resumeId`,`skillId`,`isProjectSkill`)VALUES {}""".format(values)
		result  = cursor.execute(sql_insert_query)
		connection.commit()
		print(result)
		return {"status": "success", "comment": "Record inserted successfully into skills table.", "id": cursor.lastrowid}
	except Error:
		print(Error)
		return {"status": "fail", "comment": "skills insert db_query fail"}


def get_skills_from_db():
	data = {}
	if connection_status:
		try:
			cursor = connection.cursor(prepared=True)
			query = "SELECT id, name FROM skill"
			cursor.execute(query)
			names = cursor.fetchall()
			for each in names:
				data[each[1].lower()] = each[0]
		except Error:
			pass

		return data
	return data


def get_visa_tags_from_db():
	data = {}
	if connection_status:
		try:
			cursor = connection.cursor(prepared=True)
			query = "SELECT id, name FROM visa_tag"
			cursor.execute(query)
			names = cursor.fetchall()
			for each in names:
				data[each[1].lower()] = each[0]
		except Error:
			pass

		return data
	return data


