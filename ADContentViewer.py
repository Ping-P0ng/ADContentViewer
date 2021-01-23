import tornado.ioloop
import tornado.web
import os
import sqlite3
import json
import re
import argparse
import sys


MainPageStart = """<html><head>
<title>ADContentViewer</title>
</head>
<body>
<div style="display: flex;height: 100%;width: 100%;">
<div style="float: left;
    width: 60px;
    background-color: mediumblue;
    padding: 3px;
    box-shadow: 0 0 5px 2px;
">
<form action="request">
<input type="submit" name="action" value="H" style=" background-color: Transparent;background-repeat:no-repeat;border: none;cursor:pointer;overflow: hidden;outline:none;height: 7%;width: 100%;color: white;font-size: x-large;font-family: cursive;font-style: normal;"/>
<input type="submit" name="action" value="U" style=" background-color: Transparent;background-repeat:no-repeat;border: none;cursor:pointer;overflow: hidden;outline:none;height: 7%;width: 100%;color: white;font-size: x-large;font-family: cursive;font-style: normal;"/>
<input type="submit" name="action" value="G" style=" background-color: Transparent;background-repeat:no-repeat;border: none;cursor:pointer;overflow: hidden;outline:none;height: 7%;width: 100%;color: white;font-size: x-large;font-family: cursive;font-style: normal;"/>
<input type="submit" name="action" value="C" style=" background-color: Transparent;background-repeat:no-repeat;border: none;cursor:pointer;overflow: hidden;outline:none;height: 7%;width: 100%;color: white;font-size: x-large;font-family: cursive;font-style: normal;"	/>
</form>
</div >
<div style="float: left;
    background-color: #f9f9f9;
    height: 100%;
    position: relative;
    width: 100%;
    margin: 0 12px;
    box-shadow:
   -20px 20px 0 -17px #fff,
   20px -20px 0 -17px #fff,
   20px 20px 0 -20px #c27153,
   0 0 0 2px #c27153;">
"""
MainPageEnd = """</div>
</div>
</body></html>"""
HomePage = """<div style="height: 7%;
    width: 100%;
    text-align: left;
    margin: 5px;
    line-height: 2.5;
    vertical-align: middle;
    box-shadow: 0 2px 0 0 black;
    font-size: x-large;
    font-style: normal;">"""

ObjPage = """style="background-color: Transparent;
    background-repeat: no-repeat;
    border: none;
    cursor: pointer;
    line-height: normal;
    overflow: hidden;
    outline: none;
    height: auto;
    min-height: 5%;
    position: static;
    width: 100%;
    text-align: left;
    color: black;
    font-size: larger;
    font-style: normal;
    box-shadow: 0 2px 0 0 black;" """

ViewDiv = """<div style="height: 85%;width: 100%;overflow: auto;">"""

SearchPanel = """method="get" style="margin: 15px;">
	<input type="text" name="search" placeholder="Search string" style="border: 2px solid black;width: 89%;
    height: 5%;border-radius: 21px; outline: none;">
	<input type="submit" name="action" value="search" style="border: 2px solid black;width: 10%;
    height: 5%;
    color: black;
     outline: none;
    background-color: white;
    text-decoration: none;
    padding: .8em 1em calc(.8em + 3px);
    border-radius: 21px;"/></form>"""

UserAccountControl = {"SCRIPT":1,
"ACCOUNTDISABLE":2,
"HOMEDIR_REQUIRED":8,
"LOCKOUT":16,
"PASSWD_NOTREQD":32,
"PASSWD_CANT_CHANGE":64,
"ENCRYPTED_TEXT_PWD_ALLOWED":128,
"TEMP_DUPLICATE_ACCOUNT":256,
"NORMAL_ACCOUNT":512,
"INTERDOMAIN_TRUST_ACCOUNT":2048,
"WORKSTATION_TRUST_ACCOUNT":4096,
"SERVER_TRUST_ACCOUNT":8192,
"DONT_EXPIRE_PASSWORD":65536,
"MNS_LOGON_ACCOUNT":131072,
"SMARTCARD_REQUIRED":262144,
"TRUSTED_FOR_DELEGATION":524288,
"NOT_DELEGATED":1048576,
"USE_DES_KEY_ONLY":2097152,
"DONT_REQ_PREAUTH":4194304,
"PASSWORD_EXPIRED":8388608,
"TRUSTED_TO_AUTH_FOR_DELEGATION":16777216,
"PARTIAL_SECRETS_ACCOUNT":67108864
}
	


class Web(tornado.web.RequestHandler):
	def initialize(self,Settings):
		self.Settings = Settings
		if(os.path.exists(Settings["db_name"])):
			self.ObjDb = sqlite3.connect(Settings["db_name"])
			self.ObjCursor = self.ObjDb.cursor()

	def get(self):
		if(self.request.uri == "/"):
			self.redirect("/home")
		elif(self.request.uri[:6] == "/users" or self.request.uri[:10] == "/computers" or self.request.uri[:7] == "/groups"):
			AllInputArg = self.request.arguments
			if(self.request.uri[:6] == "/users"):
				WritePage = MainPageStart + '<form action="users" ' + SearchPanel + ViewDiv
			elif(self.request.uri[:10] == "/computers"):
				WritePage = MainPageStart + '<form action="computers" ' + SearchPanel + ViewDiv
			elif(self.request.uri[:7] == "/groups"):
				WritePage = MainPageStart + '<form action="groups" ' + SearchPanel + ViewDiv
			if("count" in AllInputArg.keys() and  "offset"  in AllInputArg.keys()):
				GetArgUserCount = self.get_argument("count")
				GetArgUserOffset = self.get_argument("offset")
				if("action" in AllInputArg.keys()):
					if(self.get_argument("action") == "next"):
						GetArgUserOffset = int(GetArgUserOffset) + int(GetArgUserCount)
					elif(self.get_argument("action") == "back"):
						GetArgUserOffset = int(GetArgUserOffset) - int(GetArgUserCount)
						if(GetArgUserOffset < 0):
							GetArgUserOffset = 0
				if(self.request.uri[:6] == "/users"):
					for InfoObject in self.ObjCursor.execute("""SELECT sAMAccountName,userAccountControl,description FROM users LIMIT {0},{1}""".format(GetArgUserOffset,GetArgUserCount)):
						PrintStr = "{0}".format(InfoObject[0])
						if(UserAccountControl["ACCOUNTDISABLE"] & int(InfoObject[1]) != 0):
							PrintStr = "*ACCOUNTDISABLE* {0}".format(PrintStr)
						descriptionValue = ""
						if(InfoObject[2] != ""):
							descriptionValue = "- {0}".format(InfoObject[2])
						WritePage = WritePage + """<a style="text-decoration: none; color: black;" href="/users?action=info&object={0}"><div """.format(InfoObject[0])+ObjPage+""">{0} {1}</div></a><br>""".format(PrintStr,descriptionValue)
					NPanel = """<form action="users" method="get" style="margin: 15px; position: absolute;bottom: 0; right: 0;">"""
				elif(self.request.uri[:10] == "/computers"):
					for InfoObject in self.ObjCursor.execute("""SELECT sAMAccountName,description FROM computers LIMIT {0},{1}""".format(GetArgUserOffset,GetArgUserCount)):
						descriptionValue = ""
						if(InfoObject[1] != ""):
							descriptionValue = "- {0}".format(InfoObject[1])
						WritePage = WritePage + """<a style="text-decoration: none; color: black;" href="/computers?action=info&object={0}"><div """.format(InfoObject[0])+ObjPage+""">{0} {1}</div></a><br>""".format(InfoObject[0],descriptionValue)
					NPanel = """<form action="computers" method="get" style="margin: 15px; position: absolute;bottom: 0; right: 0;">"""
				elif(self.request.uri[:7] == "/groups"):
					for InfoObject in self.ObjCursor.execute("""SELECT sAMAccountName,description FROM groups LIMIT {0},{1}""".format(GetArgUserOffset,GetArgUserCount)):
						descriptionValue = ""
						if(InfoObject[1] != ""):
							descriptionValue = "- {0}".format(InfoObject[1])
						WritePage = WritePage + """<a style="text-decoration: none; color: black;" href="/groups?action=info&object={0}"><div """.format(InfoObject[0])+ObjPage+""">{0} {1}</div></a><br>""".format(InfoObject[0],descriptionValue)
					NPanel = """<form action="groups" method="get" style="margin: 15px; position: absolute;bottom: 0; right: 0;">"""
				NPanel = NPanel + """<input type="submit" name="action" value="back" style="border: 2px solid black;width: 70px; height: 38px;    color: black;    outline: none;    background-color: white;    text-decoration: none;    padding: .8em 1em calc(.8em + 3px);    border-radius: 21px;"/>"""
				NPanel = NPanel + """<input type="text" name="count" placeholder="Count" value="{0}" style="border: 2px solid black;width: 100px;height: 38px; border-radius: 21px; outline: none;    text-align: center;"/>""".format(GetArgUserCount)
				NPanel = NPanel + """<input type="hidden" name="offset" value="{0}"/>""".format(GetArgUserOffset)
				NPanel = NPanel + """<input type="submit" name="action" value="next" style="border: 2px solid black;width: 70px; height: 38px;    color: black;    outline: none;    background-color: white;    text-decoration: none;    padding: .8em 1em calc(.8em + 3px);    border-radius: 21px;"/></form>"""
				self.write(WritePage+"	</div>"+NPanel+MainPageEnd)
			elif("action" in AllInputArg.keys()):
				GetArgAction = self.get_argument("action")
				if(GetArgAction == "search"):
					GetArgSearch = self.get_argument("search")
					if(GetArgSearch != ""):
						if(self.request.uri[:6] == "/users"):
							WritePage = MainPageStart + '<form action="users" ' + SearchPanel + ViewDiv
						elif(self.request.uri[:10] == "/computers"):
							WritePage = MainPageStart + '<form action="computers" ' + SearchPanel + ViewDiv
						elif(self.request.uri[:7] == "/groups"):
							WritePage = MainPageStart + '<form action="groups" ' + SearchPanel + ViewDiv
						if(self.request.uri[:6] == "/users"):
							for InfoObject in self.ObjCursor.execute("""SELECT sAMAccountName,userAccountControl,description FROM users WHERE sAMAccountName LIKE '%{0}%'""".format(GetArgSearch)):
								PrintStr = "{0}".format(InfoObject[0])
								if(UserAccountControl["ACCOUNTDISABLE"] & int(InfoObject[1]) != 0):
									PrintStr = "*ACCOUNTDISABLE* {0}".format(PrintStr)
								descriptionValue = ""
								if(InfoObject[2] != ""):
									descriptionValue = "- {0}".format(InfoObject[2])
								WritePage = WritePage + """<a style="text-decoration: none; color: black;" href="/users?action=info&object={0}"><div """.format(InfoObject[0])+ObjPage+""">{0} {1}</div></a><br>""".format(PrintStr,descriptionValue)
						elif(self.request.uri[:10] == "/computers"):
							for InfoObject in self.ObjCursor.execute("""SELECT sAMAccountName,description  FROM computers WHERE sAMAccountName LIKE '%{0}%'""".format(GetArgSearch)):
								descriptionValue = ""
								if(InfoObject[1] != ""):
									descriptionValue = "- {0}".format(InfoObject[1])
								WritePage = WritePage + """<a style="text-decoration: none; color: black;" href="/computers?action=info&object={0}"><div """.format(InfoObject[0])+ObjPage+""">{0} {1}</div></a><br>""".format(InfoObject[0],descriptionValue)
						elif(self.request.uri[:7] == "/groups"):
							for InfoObject in self.ObjCursor.execute("""SELECT sAMAccountName,description  FROM groups WHERE sAMAccountName LIKE '%{0}%'""".format(GetArgSearch)):
								descriptionValue = ""
								if(InfoObject[1] != ""):
									descriptionValue = "- {0}".format(InfoObject[1])
								WritePage = WritePage + """<a style="text-decoration: none; color: black;" href="/groups?action=info&object={0}"><div """.format(InfoObject[0])+ObjPage+""">{0} {1}</div></a><br>""".format(InfoObject[0],descriptionValue)
						self.write(WritePage+"""</div>"""+MainPageEnd)
				elif(GetArgAction == "info"):
					GetArgObj = self.get_argument("object")
					if(GetArgObj != ""):
						if(self.request.uri[:6] == "/users"):
							SelectObj = self.ObjCursor.execute("""SELECT users.FullData from users where users.samaccountname='{0}'""".format(GetArgObj))
						elif(self.request.uri[:10] == "/computers"):
							SelectObj = self.ObjCursor.execute("""SELECT FullData FROM computers WHERE sAMAccountName='{0}'""".format(GetArgObj))
						elif(self.request.uri[:7] == "/groups"):
							SelectObj = self.ObjCursor.execute("""SELECT FullData FROM groups WHERE sAMAccountName='{0}'""".format(GetArgObj))
						ObjValue = SelectObj.fetchone()
						if(ObjValue != None):
							JsonObj = json.loads(ObjValue[0])
							if(self.request.uri[:6] == "/users"):
								WritePage = MainPageStart + '<form action="users" ' + SearchPanel + ViewDiv
							elif(self.request.uri[:10] == "/computers"):
								WritePage = MainPageStart + '<form action="computers" ' + SearchPanel + ViewDiv
							elif(self.request.uri[:7] == "/groups"):
								WritePage = MainPageStart + '<form action="groups" ' + SearchPanel + ViewDiv
							for CurrentKey in JsonObj.keys():
								if(isinstance(JsonObj[CurrentKey],list)):
									for CurrentValue in JsonObj[CurrentKey]:
										if(CurrentKey == "member" or CurrentKey == "memberOf"):
											WritePage = WritePage + """{0}: <a style="text-decoration: none; color: black;" href="/request?dn={1}">{1}</a><br>""".format(CurrentKey,CurrentValue)
										else:
											WritePage = WritePage + "{0}: {1}<br>".format(CurrentKey,CurrentValue)
								else:
									if(CurrentKey == "userAccountControl"):
										PrintStr = ""
										for CurrentUAC in UserAccountControl.keys():
											if(UserAccountControl[CurrentUAC] & int(JsonObj[CurrentKey]) != 0):
												PrintStr += " {0} |".format(CurrentUAC)
										WritePage = WritePage + "{0}: {1} > {2}<br>".format(CurrentKey,JsonObj[CurrentKey],PrintStr[:-1])
									else:
										WritePage = WritePage + "{0}: {1}<br>".format(CurrentKey,JsonObj[CurrentKey])
							SelectPwd = self.ObjCursor.execute("""SELECT LM,NT,pass FROM pwd WHERE sAMAccountName='{0}'""".format(GetArgObj))
							CheckPwd = SelectPwd.fetchone()
							if(CheckPwd != None):
								WritePage = WritePage + "---------------------------<br>"
								WritePage = WritePage + "{0}:{1}:{2}".format(CheckPwd[0],CheckPwd[1],CheckPwd[2])
							self.write(WritePage+"""</div>"""+MainPageEnd)
			else:
				pass
			
		elif(self.request.uri == "/home"):
			WritePage = MainPageStart
			CountUser = self.ObjCursor.execute("""SELECT count(*) FROM users""")
			CountUserValue = CountUser.fetchone()
			WritePage = WritePage + HomePage + "Users:    {0}</div>".format(CountUserValue[0])
			CountGroup = self.ObjCursor.execute("""SELECT count(*) FROM groups""")
			CountGroupValue = CountUser.fetchone()
			WritePage = WritePage + HomePage + "Groups:    {0}</div>".format(CountGroupValue[0])
			CountPC = self.ObjCursor.execute("""SELECT count(*) FROM computers""")
			CountPCValue = CountUser.fetchone()
			WritePage = WritePage + HomePage + "Computers:    {0}</div>".format(CountPCValue[0])
			self.write(WritePage+MainPageEnd)
		elif(self.request.uri[:8] == "/request"):
			AllInputArg = self.request.arguments
			if("action" in AllInputArg.keys()):
				GetArgAction = self.get_argument("action")
				if(GetArgAction == "H"):
					self.redirect("/home")
				elif(GetArgAction == "U"):
					self.redirect("/users?offset=0&count={0}".format(self.Settings["obj_count_page"]))
				elif(GetArgAction == "C"):
					self.redirect("/computers?offset=0&count={0}".format(self.Settings["obj_count_page"]))
				elif(GetArgAction == "G"):
					self.redirect("/groups?offset=0&count={0}".format(self.Settings["obj_count_page"]))
			elif("dn" in AllInputArg.keys()):
				GetArgAction = self.get_argument("dn")
				CountUser = self.ObjCursor.execute("""SELECT sAMAccountName FROM users  WHERE dn='{0}'""".format(GetArgAction))
				CountUserValue = CountUser.fetchone()
				if(CountUserValue != None):
					self.redirect("/users?action=info&object={0}".format(CountUserValue[0]))
				CountPC = self.ObjCursor.execute("""SELECT sAMAccountName FROM computers   WHERE dn='{0}'""".format(GetArgAction))
				CountPCValue = CountUser.fetchone()
				if(CountPCValue != None):
					self.redirect("/computers?action=info&object={0}".format(CountPCValue[0]))
				CountGroup = self.ObjCursor.execute("""SELECT sAMAccountName FROM groups   WHERE dn='{0}'""".format(GetArgAction))
				CountGroupValue = CountUser.fetchone()
				if(CountGroupValue != None):
					self.redirect("/groups?action=info&object={0}".format(CountGroupValue[0]))



class Reader(object):
	def __init__(self,ADInfoFilesPath,Settings):
		self.ADInfoFiles = {}
		self.Settings = Settings
		for CurrentKey in ADInfoFilesPath.keys():
			if(os.path.exists(ADInfoFilesPath[CurrentKey]) and os.path.isfile(ADInfoFilesPath[CurrentKey])):
				print("+ > {0}".format(ADInfoFilesPath[CurrentKey]))
				self.ADInfoFiles[CurrentKey] = ADInfoFilesPath[CurrentKey]
			else:
				print("- > {0}".format(ADInfoFilesPath[CurrentKey]))
				print("> File not found")

		if(os.path.isdir(Settings["db_name"])):
			sys.exit("> {0} - it directory".format(Settings["db_name"]))
		if(not os.path.exists(Settings["db_name"])):
			self.ObjDb = sqlite3.connect(Settings["db_name"])
			self.ObjCursor = self.ObjDb.cursor()
			print("> create {0}".format(Settings["db_name"]))
			self.ObjCursor.execute('''CREATE TABLE users (dn text, sAMAccountName text,userAccountControl int,description text, FullData text)''')
			self.ObjCursor.execute('''CREATE TABLE groups (dn text, sAMAccountName text,description text, FullData text)''')
			self.ObjCursor.execute('''CREATE TABLE pwd (sAMAccountName text, LM text, NT text, pass text)''')
			self.ObjCursor.execute('''CREATE TABLE computers (dn text, sAMAccountName text,userAccountControl int,description text, FullData text)''')
			self.ObjDb.commit()
			print("> create 4 tables (users,groups,computers,pwd)")
		else:
			print("> connect {0}".format(Settings["db_name"]))
			self.ObjDb = sqlite3.connect(Settings["db_name"])
			self.ObjCursor = self.ObjDb.cursor()

	def AddObjectDB(self,ADObject):
		descriptionValue = ""
		if("description" in ADObject.keys()):
			descriptionValue = ADObject["description"]
		if(int(ADObject["sAMAccountType"]) == 805306368): # user object
			SelectUser = self.ObjCursor.execute("""SELECT sAMAccountName FROM users WHERE sAMAccountName='{0}'""".format(ADObject["sAMAccountName"]))
			CheckUser = SelectUser.fetchone()
			if(CheckUser == None):
				self.ObjCursor.execute("""INSERT INTO users VALUES ('{0}','{1}',{2},'{3}','{4}')""".format(ADObject["dn"],ADObject["sAMAccountName"],ADObject["userAccountControl"],descriptionValue,json.dumps(ADObject)))
				self.ObjDb.commit()
				print("\t> add object - {0}".format(ADObject["dn"]))
			elif(len(CheckUser) == 1):
				print("\t> object exist - {0}".format(ADObject["dn"]))
			else:
				print("\t- > fail check object - {0}".format(ADObject["dn"]))
		elif(int(ADObject["sAMAccountType"]) == 805306369): # computer object
			SelectUser = self.ObjCursor.execute("""SELECT sAMAccountName FROM computers WHERE sAMAccountName='{0}'""".format(ADObject["sAMAccountName"]))
			CheckUser = SelectUser.fetchone()
			if(CheckUser == None):
				self.ObjCursor.execute("""INSERT INTO computers VALUES ('{0}','{1}',{2},'{3}','{4}')""".format(ADObject["dn"],ADObject["sAMAccountName"],ADObject["userAccountControl"],descriptionValue,json.dumps(ADObject)))
				self.ObjDb.commit()
				print("\t> add object - {0}".format(ADObject["dn"]))
			elif(len(CheckUser) == 1):
				print("\t> object exist - {0}".format(ADObject["dn"]))
			else:
				print("\t- > fail check object - {0}".format(ADObject["dn"]))
		elif(int(ADObject["sAMAccountType"]) == 536870912 or int(ADObject["sAMAccountType"]) == 268435456): # group object
			SelectUser = self.ObjCursor.execute("""SELECT sAMAccountName FROM groups WHERE sAMAccountName='{0}'""".format(ADObject["sAMAccountName"]))
			CheckUser = SelectUser.fetchone()
			if(CheckUser == None):
				self.ObjCursor.execute("""INSERT INTO groups VALUES ('{0}','{1}','{2}','{3}')""".format(ADObject["dn"],ADObject["sAMAccountName"],descriptionValue,json.dumps(ADObject)))
				self.ObjDb.commit()
				print("\t> add object - {0}".format(ADObject["dn"]))
			elif(len(CheckUser) == 1):
				print("\t> object exist - {0}".format(ADObject["dn"]))
			else:
				print("\t- > fail check object - {0}".format(ADObject["dn"]))


	def GetADObjects(self):
		if(self.Settings["format"] == "ADFind_default"):
			encodings = ['utf-8','UTF-16LE']
			for CurrentKey in self.ADInfoFiles.keys():
				if(CurrentKey != "pwd"):
					print("> check {0}".format(self.ADInfoFiles[CurrentKey]))
					for e in encodings:
						try:
							ObjFile = open(self.ADInfoFiles[CurrentKey],"r",encoding=e)
							ObjFile.readlines()
							ObjFile.seek(0)
						except UnicodeDecodeError:
							print('> got unicode error with %s , trying different encoding' % e)
						else:
							print('> opening the file with encoding:  %s ' % e)
							break
					ObjData = {}
					CheckFirstObj = False
					for CurrentLine in ObjFile:
						SplitLine = CurrentLine[:-1].split(':')
						if(len(SplitLine) == 2):
							if(CheckFirstObj == False):
								if(SplitLine[0] == "dn"):
									CheckFirstObj = True
									if(ObjData != {}):
										self.AddObjectDB(ObjData)
									ObjData = {}
									ObjData[SplitLine[0]] = SplitLine[1]
							else:
								if(SplitLine[0] == "dn"):
									if(ObjData != {}):
										self.AddObjectDB(ObjData)
									ObjData = {}
									ObjData[SplitLine[0]] = SplitLine[1]
								elif(SplitLine[0][1:] == "memberOf" 
									or SplitLine[0][1:] == "member" 
									or SplitLine[0][1:] == "servicePrincipalName"
									or SplitLine[0][1:] == "objectClass"):
									if(SplitLine[0][1:] not in ObjData.keys()):
										ObjData[SplitLine[0][1:]] = [SplitLine[1][1:]]
									else:
										ObjData[SplitLine[0][1:]].append(SplitLine[1][1:])
								else:
									ObjData[SplitLine[0][1:]] = SplitLine[1][1:]
					if(ObjData != {}):
						self.AddObjectDB(ObjData)
				elif(CurrentKey == "pwd"):
					print("> check {0}".format(self.ADInfoFiles[CurrentKey]))
					for e in encodings:
						try:
							PwdFile = open(self.ADInfoFiles[CurrentKey],"r",encoding=e)
							PwdFile.readlines()
							PwdFile.seek(0)
						except UnicodeDecodeError:
							print('> got unicode error with %s , trying different encoding' % e)
						else:
							print('> opening the file with encoding:  %s ' % e)
							break
					for CurrentLine in PwdFile:
						PwdData = re.findall(r"^([^:]*):[^:]*:([^:]*):([^:]*):\S*:\S*:(\S*)",CurrentLine)
						SelectPwd = self.ObjCursor.execute("""SELECT sAMAccountName FROM pwd WHERE sAMAccountName='{0}'""".format(PwdData[0][0]))
						CheckPwd = SelectPwd.fetchone()
						if(CheckPwd == None):
							self.ObjCursor.execute("""INSERT INTO pwd VALUES ('{0}','{1}','{2}','{3}')""".format(PwdData[0][0],PwdData[0][1],PwdData[0][2],PwdData[0][3]))
							self.ObjDb.commit()
							print("\t> add {0} hash".format(PwdData[0][0]))
						else:
							print("\t> exist {0} hash".format(PwdData[0][0]))
# ADInfo file format:
# 	- ADFind_default
#

if __name__ == "__main__":
	parser = argparse.ArgumentParser("ADContentViewer")
	parser.add_argument("-c","--computers", help="computers file path")
	parser.add_argument("-u","--users", help="users file path")
	parser.add_argument("-g","--groups", help="groups file path")
	parser.add_argument("-pwd","--pwd", help="hash file (pwd format)")
	parser.add_argument("-db", help="db file name (default: adinfo.db)")
	args = parser.parse_args()
	if(args.db == None):
		OutSqlFile = "adinfo.db"
	else:
		OutSqlFile = args.db
	Settings = {"format":"ADFind_default",
		"db_name":OutSqlFile,
		"obj_count_page":"10"}
	ADInfoFilesPath = {}
	if(args.users != None):
		ADInfoFilesPath["users"] = args.users
	if(args.groups != None):
		ADInfoFilesPath["groups"] = args.groups
	if(args.computers != None):
		ADInfoFilesPath["computers"] = args.computers
	if(args.pwd != None):
		ADInfoFilesPath["pwd"] = args.pwd
	MainReader = Reader(ADInfoFilesPath,Settings)
	MainReader.GetADObjects()
	application = tornado.web.Application([
		(r"/", Web,dict(Settings=Settings)),
		(r"/home", Web,dict(Settings=Settings)),
		(r"/request", Web,dict(Settings=Settings)),
		(r"/users", Web,dict(Settings=Settings)),
		(r"/groups", Web,dict(Settings=Settings)),
		(r"/computers", Web,dict(Settings=Settings)),
		])
	print("> go http://127.0.0.1:16600/")
	application.listen(16600)
	tornado.ioloop.IOLoop.current().start()
