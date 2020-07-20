import mysql.connector
import os


db= mysql.connector.connect(
host= os.getenv('host'),
user= os.getenv('username'),
password= os.getenv('password'),
port= os.getenv('port')
)

dbCursor = db.cursor()
dbCursor.execute("USE "+ os.getenv('dbname'))

def formatResponse(mlResponse):
  response = {
    "fulfillmentText": mlResponse,
    "fulfillmentMessages": [
      {
        "text": {
          "text": [
            mlResponse
          ]
        }
      }
    ],    
    "payload": {
      "google": {
        "expectUserResponse": 'true',
        "richResponse": {
          "items": [
            {
              "simpleResponse": {
                "textToSpeech": mlResponse
              }
            }
          ]
        }
      }
    }
   }  
  return response
   
 

def generateResponse(intent, newPrice, propertyCode, roomID, phoneNum, status, decision): 

    if intent == "Default Welcome Intent":      
        return 'Hi '+getUserDetails(phoneNum)+', I am Rentaly.\n\nI found your properties:\n'+getPropertyDetails(phoneNum)+'\nHow can I help?'

    elif intent == "About":
        return "Hi, I am Rentaly Bot.\nI can help you to make updates to your rooms"

    elif intent == "Update Vacancy": 
        if status!= '' and roomID!='':
          return 'Are you sure you want update the status of Property '+propertyCode.upper()+' - Room '+roomID+' to '+status.capitalize()+'?'
        else:
          return 'Got it! Here are the rooms for property: '+propertyCode.upper()+'\n\n'+getRooms(propertyCode)+'\nWhich room do you want to make changes to?'

    elif intent == "Update Vacancy - getRoomNumber": 
      return 'What is the vacancy status of this room?'

    elif intent == "Update Vacancy - getRoomStatus":
      return 'Are you sure you want update the vacancy of Property '+propertyCode.upper()+' - Room '+roomID+' to '+status.capitalize()+'?'


    elif intent == "Update Rent":
        if newPrice!= '' and roomID!='':  
          return 'Are you sure you want update the rent of Property '+propertyCode.upper()+' - Room '+roomID+' to $'+newPrice+'?'       
        else:
          return 'Got it! Here are the rooms for property: '+propertyCode.upper()+'\n\n'+getRooms(propertyCode)+'\nWhich room do you want to make changes to?'

    elif intent == "Update Rent - getRoomNumber": 
      return 'What is the new rent?'

    elif intent == "Update Rent - getRoomCost": 
      return 'Are you sure you want update the rent of Property '+propertyCode.upper()+' - Room '+roomID+' to $'+newPrice+'?'

    elif intent == "Update Rent - Confirmation" or intent == "Update Rent - Steps Confirmation":  
        if decision == 'yes':   
          updatePrice(newPrice, propertyCode, roomID)
          return "Rent was successfully updated"
        else:
            return "Ok, how else can I assist?"

    elif intent == "Update Vacancy - Confirmation" or intent == "Update Vacancy - Steps Confirmation":
        if decision == 'yes': 
          updateOccupancy(propertyCode, status, roomID)
          return 'Room vacancy status successfully updated'
        else:
            return "Ok, how else can I assist?"
      
    else:
        return 'Sorry, I did not get that. Please try again'

def getUserDetails(phoneNum):    
    sql="SELECT * FROM users WHERE id ='" + phoneNum+"'"
    dbCursor.execute(sql)
    row = dbCursor.fetchone()
    rowDict =  dict(zip([c[0] for c in dbCursor.description], row)) #converting list to dictionary    
    print('log: '+sql)
    return rowDict['fname']
    
def updatePrice(newPrice, propertyCode, roomID):
  room_number_to_update=int(roomID) - 1
  room_number_to_update = str(room_number_to_update)
  sql= str("UPDATE rooms "+
           "INNER JOIN (SELECT id from rooms where property_id = '"+propertyCode.upper()+"' order by id limit " +room_number_to_update+",1) as r using (`id`) "+
           "SET rooms.rent = '"+newPrice+"'"
          )
  print('log: '+sql)
  
  dbCursor.execute(sql)           
  db.commit()
  

def getPropertyDetails(phoneNum):
  dbCursor.execute("SELECT * from properties where user_id = '"+phoneNum+"'")
  records = dbCursor.fetchall()
  properties=''
  for row in records:
    properties=properties+str(''
                              +row[0]+ ' - '+row[1]+', '+row[2]+'\n'
                             )
  return properties
 
def getRooms(propertyCode):
  dbCursor.execute("select (@cnt := @cnt + 1) AS room_number, bathroom, kitchen, rent, rooms.status "+
                    "from rooms "+
                    "CROSS JOIN (SELECT @cnt := 0) as dummy "+
                    "where property_id='"+propertyCode.upper()+"'"
                  )
  records = dbCursor.fetchall()
  rooms=''
  for row in records:
    roomNum=int(row[0])
    roomNum=str(roomNum)
    price = str(row[3])
    rooms= rooms+str('Room ' +roomNum+'\n'
                 +row[1].capitalize()+' Bathroom, '+row[2].capitalize()+' Kitchen \n'
                'Rent: $'+price+'\n'
                'Status: '+row[4].capitalize()+'\n\n'
                )
 
  # rowDict =  dict(zip([c[0] for c in dbCursor.description], row)) #converting list to dictionary
  return rooms



def updateOccupancy(propertyCode, status, roomID):
    room_number_to_update=int(roomID) - 1
    room_number_to_update = str(room_number_to_update)
    sql= str("UPDATE rooms "+
           "INNER JOIN (SELECT id from rooms where property_id = '"+propertyCode.upper()+"' order by id limit " +room_number_to_update+",1) as r using (`id`) "+
           "SET rooms.status = '"+status+"'"
          )
    print('log: '+sql)
    dbCursor.execute(sql)
    db.commit()
 