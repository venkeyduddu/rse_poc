import pdfplumber
import nltk
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    import nltkmodules
from nameparser.parser import HumanName
from nltk.corpus import wordnet
import os,time
import re
import spacy
from spacy import displacy

import requests
import io
import pyap
from urllib.parse import urlparse
from db_utils import save_data_db, get_skills_from_db, get_visa_tags_from_db
from urllib.request import urlopen
from datetime import datetime




def get_human_names(text):
    person_list = []
    person = []
    name = ""
    tokens = nltk.tokenize.word_tokenize(text)
    pos = nltk.pos_tag(tokens)
    sentt = nltk.ne_chunk(pos, binary = False)

    
    
    for subtree in sentt.subtrees(filter=lambda t: t.label() == 'PERSON'):
        for leaf in subtree.leaves():
            person.append(leaf[0])
        if len(person) > 1: 
            for part in person:
                name += part + ' '
            if name[:-1] not in person_list:
                person_list.append(name[:-1])
    
    for person in person_list:
        person_split = person.split(" ")
        for name in person_split:
            if wordnet.synsets(name):
                if(name in person):
                    person_list.remove(person)
                    break
    first_word=person_list[0]
    return first_word


def equal(a):
    m= re.sub('[^\s\w]',' ', a)
    m = ''.join([i for i in m if not i.isdigit()])
    m = m.replace("_", " ")
    m = m.upper()
    m = m.split(" ")
    return m


def extract_person_details(text):
    text= text.rstrip()
    name = get_human_names(text)
    emails = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", text)
    emails1=emails[0]
    contact=re.findall(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', text)
    contact1=contact[0]

    person_details={}
    person_details["name"] = name
    person_details["emails"] =  emails
    person_details["contacts"] = contact
    return person_details


def extract_adresses(text, person_details):
    contact = person_details.get("contacts")[0]
    text= text.rstrip()
    addresses = pyap.parse(text, country='US')
    address_list=[]
    address_dict=[]
    for address in addresses:
        address_list.append(address)
        address_dict.append(address.as_dict())
    if(len(address_list)==0):
        address=[]
    elif(len(address_list)==1 or contact==""):
        address=address_list[0]
    else:
        contact_index=-1
        contact_flag=0
        address_index=[]
        text_list=(text.split("\n"))
        for i in range(len(address_list)):
            try:
                city=address_dict[i]['city']
                for sentence in range(len(text_list)):
                    if(city in text_list[sentence]):
                        address_index.append(sentence)
                    if(contact[0] in text_list[sentence] and contact_flag==0):
                        contact_index=sentence
                        contact_flag=1
                address=address_list[address_index.index(min(address_index, key=lambda x:abs(x-contact_index)))]
            except KeyError:
                address=address_list[0]
                break

    if address_list:
        address_list = [str(x) for x in address_list]

    return address_list


def extract_file_details(url, filename, filesize):
    data = {}
    data["filesize"] = filesize
    split_tup = os.path.splitext(filename)
    file_name = split_tup[0]
    file_extension = split_tup[1]
    data["filename"] = file_name
    data["file_extension"] = file_extension

    try:
        f = urlopen(url)
        i = f.info()
        fdt = i["Last-Modified"]
        fdt = datetime.strptime(fdt, '%a, %d %b %Y %H:%M:%S GMT')
        print(fdt)
    except:
        pass

    return data



def read_pdf_from_url(url):
    req = requests.get(url)
    temp = io.BytesIO()
    temp.write(req.content)
    file_size = temp.__sizeof__()
    file_name = get_filename_from_url(url)
    temp_text = io.StringIO()
    with pdfplumber.open(temp) as pdf:
        for page_num in range(len(pdf.pages)):
            try:
                txt=pdf.pages[page_num].extract_text()
            except:
                pass
            else:
                temp_text.write('Page {0}\n'.format(page_num+1))
                temp_text.write(''.center(100, '-'))
                temp_text.write(txt)
        temp_text.seek(0)
    return temp_text, file_name, file_size

def get_filename_from_url(url):
    a = urlparse(url)
    return os.path.basename(a.path)


def extract_skills(text):
    text_string = text.lower()
    match_pattern = re.findall(r'\b[a-z]{1,15}\b', text_string)
    db_skills_dict = get_skills_from_db()
    data = {}
    if db_skills_dict.keys():
        for word in match_pattern:
            if word in db_skills_dict.keys():
                count = data.get(word,0)
                data[word] = count + 1

    print(data)
    return data, db_skills_dict


def extract_visatags(text):
    text_string = text.lower()
    db_visatags_dict = get_visa_tags_from_db()
    data = []
    if db_visatags_dict.keys():
        for each in db_visatags_dict.keys():
            for line in text_string.split("\n"):
                if each in line and "visa" in line:
                    data.append(each)
                    data.append(db_visatags_dict.get(each))
                    data.append(line)
                else:
                    continue
    print(data)
    return data, db_visatags_dict



def get_data_from_pdf(url):
    text, filename, filesize = read_pdf_from_url(url)
    text = text.read()
    data = {}
    person_details = extract_person_details(text)
    data["person_details"] = person_details
    data["file_details"] = extract_file_details(url, filename, filesize)
    addresses = extract_adresses(text, person_details)
    data["addresses"] = addresses
    skills, db_skills_dict = extract_skills(text)
    data["skills"] = skills
    visatags, db_visatags_dict = extract_visatags(text)
    data["visatags"] = visatags
    db_report = save_data_db(data, db_skills_dict)
    data["db_report"] = db_report

    return data




# url = 'https://rse-test-data.s3.amazonaws.com/PDFs/Vinisha+Venugopal_Software+Resume.pdf'
# data = get_data_from_pdf(url)
# print(data)

# print("****")

# d=pdf_to_text("Vinisha Venugopal_Software Resume.pdf")
# print(d)

# cursor = connection.cursor(prepared=True)
# sql_insert_query ="""INSERT INTO `resume`(`userId`,`folderId`,`first_name`,`middle_name`,`last_name`,`email_id`,`phone_number`,`address`,`zip_code`,`experience`,`current_role`,`previous_role`,`degree_type`,`institution_name`,`specialization`,`status`,`deletedAt`,`createdAt`,`updatedAt`,`cityId`,`stateId`,`countryId`,`visaTagId`,`folderFileId`)VALUES (1,1,%s," "," ",%s,%s," "," ",1," "," "," "," "," ",1,"2021-06-12 12:35:41","2021-06-12 12:35:41","2021-06-12 12:35:41",1,1,1,1,1)"""
# result  = cursor.execute(sql_insert_query, d)
# connection.commit()
# print (cursor.rowcount, "Record inserted successfully into word table")
