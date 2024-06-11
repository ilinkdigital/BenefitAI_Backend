
from fastapi import FastAPI, HTTPException,WebSocket, WebSocketDisconnect
from azure.data.tables import TableServiceClient
from azure.core.exceptions import HttpResponseError
from fastapi.middleware.cors import CORSMiddleware
from azure.data.tables import UpdateMode
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from model import model, query_collection, format_output
import random
import uuid
import configparser
import uvicorn
import json
import logging

app = FastAPI()

config = configparser.ConfigParser()
config.read("config.ini")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AddMember(BaseModel):
    # PartitionKey: str(benefitsaimember)
    # RowKey: str
    MemberId: str
    PlanId: str
    DateOfBirth: str
    Firstname: str
    Lastname: str
    MemberEmail: str
    Password: str
    IsAdmin: bool
    IsActive: bool
    ModifiedDate: str  


# Configure CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_customer_table_client():
    try:
        account_name = config.get('Azure', 'account_name')
        account_key = config.get('Azure', 'account_key')
        table_name = config.get('Azure', 'table_name')
        connection_string = ("DefaultEndpointsProtocol=https;"
                             f"AccountName={account_name};"
                             f"AccountKey={account_key};"
                             "EndpointSuffix=core.windows.net")
        table_service_client = TableServiceClient.from_connection_string(conn_str=connection_string)
        table_client = table_service_client.get_table_client(table_name=table_name)
        return table_client
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error connecting to Azure Table Storage")


@app.post("/add_member/")
async def add_member(user_data: AddMember):

    # Check if MemberEmail already exists
    table_client = get_customer_table_client()
    filter_email = f"MemberEmail eq '{user_data.MemberEmail}'"
    entities_email = table_client.query_entities(filter_email)
    # print("Entities with same email:", entities_email)
    details_email= []
    for i in entities_email:
        details_email.append(i)

    # Check if MemberId already exists
    filter_id = f"MemberId eq '{user_data.MemberId}'"
    entities_id = table_client.query_entities(filter_id)
    # print("Entities with same id:", entities_id)
    details_memberid= []
    for i in entities_id:
        details_memberid.append(i)

    # if entities_email or entities_id:
    if (len(details_email)>0) or (len(details_memberid)>0) :
        # return "MemberEmail or MemberId is already exists "
        raise HTTPException(status_code=500, detail="MemberEmail or MemberId is already exists")

    else:

    # If both MemberEmail and MemberId are unique, create the entity
        entity = {
            'PartitionKey': 'benefitsaimember',
            'RowKey': str(uuid.uuid4()),
            'MemberId': user_data.MemberId,
            'PlanId': user_data.PlanId,
            'DateOfBirth': user_data.DateOfBirth,
            'MemberEmail': user_data.MemberEmail,
            'Password': user_data.Password,
            'Firstname': user_data.Firstname,
            'Lastname': user_data.Lastname,
            'IsAdmin': user_data.IsAdmin,
            'IsActive': user_data.IsActive,
            'ModifiedDate': user_data.ModifiedDate,
        }

        entity= table_client.create_entity(entity)

        # return {"message": "Entity created successfully", "entity": entity}
        raise HTTPException(status_code=200, detail="Entity created successfully")


@app.get("/login/")
async def login(MemberEmail: str, Password: str):
    try:
        table_client = get_customer_table_client()
        filter = f"MemberEmail eq '{MemberEmail}' and Password eq '{Password}'"
        entities = table_client.query_entities(filter)
        user_found = False  # Flag to track if any user is found
        for entity in entities:
            if not entity['IsActive']:
                raise HTTPException(status_code=404, detail="Member is not registered")
                # user_found = True
            # If user is active, set user_details
            user_details = {"MemberEmail": entity["MemberEmail"], 
                            "IsAdmin": entity["IsAdmin"],
                            "PlanID": entity["PlanId"]}
                  # Set the flag to True if user is found
        # If no user is found, raise HTTPException

        if user_details is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user_details

    except HTTPException as e:
        raise e  # Re-raise HTTPExceptions to avoid catching them as general exceptions
    except Exception as e:
        raise HTTPException(status_code=404, detail="Invalid Username or password")


# @app.get("/login/")
# async def login(MemberEmail: str, Password: str):
#     try:
#         table_client = get_customer_table_client()
#         filter = f"MemberEmail eq '{MemberEmail}' and Password eq '{Password}'"
#         entities = table_client.query_entities(filter)
#         user_details = None  # Initialize user_details to None

#         for entity in entities:
#             if not entity['IsActive']:
#                 raise HTTPException(status_code=404, detail="Member is not registered")
#             # If user is active, set user_details
#             user_details = {
#                 "MemberEmail": entity["MemberEmail"],
#                 "IsAdmin": entity["IsAdmin"],
#                 "PlanID": entity["PlanId"]
#             }
#             break  # Exit the loop as we found a matching and active user

#         # If user_details is still None, no matching user was found
#         if user_details is None:
#             raise HTTPException(status_code=404, detail="User not found")

#         return user_details

#     except HTTPException as e:
#         raise e  # Re-raise HTTPExceptions to avoid catching them as general exceptions
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="Invalid Username or password")



@app.get("/get_members/")
async def get_members():
    try:
        table_client = get_customer_table_client()
        entities = table_client.query_entities("")
        all_entities = []
        for entity in entities:
            MemberEmail = entity.get("MemberEmail")  # Use .get() method to avoid KeyError
            is_admin = entity.get("IsAdmin")
            if MemberEmail is not None and is_admin is not None:
                all_entities.append({
                    "Email Address": MemberEmail,
                    "Membership ID": entity["MemberId"],
                    "Plan ID": entity["PlanId"],
                    "Status": entity['IsActive'],
                    # Add more fields as needed
                })
        return all_entities
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error retrieving members")


@app.get("/Registration/")
async def User_Registration(MemberId: str, PlanId: str):
    try:
        table_client = get_customer_table_client()
        filter_query = f"MemberId eq '{MemberId}' and PlanId eq '{PlanId}'"
        entities =list(table_client.query_entities(filter_query))
        
        # If no user is found, raise HTTPException
        if len(entities)<=0:
            raise HTTPException(status_code=404, detail="Member does not found")
        
        for entity in entities:

            # Update the IsActive status to True
            entity['IsActive'] = True
            table_client.update_entity(entity=entity, mode=UpdateMode.MERGE)
            return "Member has been Registered !!"
    
    except HTTPException as e:
        # Reraise HTTPExceptions
        raise e

    except Exception as e:
        # For all other exceptions, raise a 500 error
        raise HTTPException(status_code=500, detail=str(e))


class Question(BaseModel):
    collection_name: str
    question: str

@app.post("/Chat")
async def ask_question(question: Question):
    result = query_collection(question.collection_name, question.question)
    output= format_output(result)
    # output= json.dumps(output)
    return JSONResponse(content=output)



def chat_storage_table_client():
    try:
        account_name = config.get('Azure', 'account_name')
        account_key = config.get('Azure', 'account_key')
        chat_table = config.get('Azure', 'chat_table')
        
        if not account_name or not account_key or not chat_table:
            raise ValueError("Missing Azure Storage configuration.")

        connection_string = (f"DefaultEndpointsProtocol=https;"
                                f"AccountName={account_name};"
                                f"AccountKey={account_key};"
                                "EndpointSuffix=core.windows.net")
        
        table_service_client = TableServiceClient.from_connection_string(conn_str=connection_string)
        table_client = table_service_client.get_table_client(table_name=chat_table)

        # logger.info(f"Successfully connected to Azure Table Storage: {chat_table}")
        return table_client
    
    except Exception as e:
        # logger.error("Error connecting to Azure Table Storage: %s", e)
        raise HTTPException(status_code=500, detail=f"Error connecting to Azure Table Storage: {str(e)}")


def get_plan_id(MemberEmail):
    table_client = get_customer_table_client()
    try:
        filter_query = f"PartitionKey eq 'benefitsaimember' and MemberEmail eq '{MemberEmail}'"
        # print("Filter Query:", filter_query)
        entities = list(table_client.query_entities(filter_query))
        # print("Entities: ", len(entities))
        if len(entities)<=0:
            raise HTTPException(status_code=404, detail="Member does not found")
        
        for entity in entities:
            user_details = {"MemberEmail": entity["MemberEmail"], 
                            "PlanID": entity["PlanId"]}
            
            return user_details
    
    except HTTPException as e:
        # Reraise HTTPExceptions
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error retrieving member PlanId")


# print("get_plan_id details", get_plan_id('piyush@gmail.com'))

def store_chat_log(session_id,MemberEmail, Chat_ID, plan_id, question, answer, chat_history, sources):
    try:
        table_client = chat_storage_table_client()

        if not isinstance(sources, list):
            sources = [sources]
        RowKey=str(uuid.uuid4())
        chat_log_entity = {
            'PartitionKey': 'chatsession',
            'RowKey': RowKey,  
            'SessionID': str(session_id),
            'MemberEmail': MemberEmail,
            'ChatID': str(Chat_ID),
            'PlanId': str(plan_id),
            'Question': question,
            'Answer': answer,
            'chat_history':json.dumps(chat_history),
            'Sources': json.dumps(sources)  
        }

        # logger.info(f"Attempting to store entity: {chat_log_entity}")

        table_client.create_entity(entity=chat_log_entity)
        # logger.info(f"Entity stored successfully: {chat_log_entity}")

    except Exception as e:
        # logger.error("Error storing chat log: %s", e)
        raise HTTPException(status_code=500, detail=f"Error storing chat log: {str(e)}")



@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # session = str(random.randinmain.pyt(1, 1000))
    client_address = websocket.client.host + ":" + str(websocket.client.port)
    # print(f"WebSocket connected: {client_address}, Session: {session}")

    try:
        # Simulate getting the MemberEmail from the client
        # In practice, you may get this from a login process or message from the client
        member_email = await websocket.receive_text()  # Assume first message is the email
        member_email= json.loads(member_email)
        MemberEmail=member_email['MemberEmail']
        collection_name =member_email['collection_name']
        plan_id =member_email['collection_name']
       
        # print("Member Email", MemberEmail )
        details= get_plan_id(MemberEmail)
        # print("datails",details )
        # print("Type of details",details )
        email2 = details["MemberEmail"]
        plan_id2 = details["PlanID"]
        # print("datails",email2 )
        # print("datails",plan_id2 )
        if (MemberEmail != email2) and (plan_id.lower() != plan_id2.lower()):
            await websocket.send_text(json.dumps({"error": "Invalid MemberEmail"}))
            return

        while True:
            data = await websocket.receive_text()
            
            data= json.loads(data)

            query= data['question']
            session_id= data['session_id']
            Chat_ID= data['Chat_ID']

            # print("Question", query)
            # print("Question", session_id)
            # print("Question", Chat_ID)

            # logger.info(f"Message from {client_address}: {data}")
            result = query_collection(collection_name, query)
            # print("type of result1", type(result))
            # print("Initial result", result)
            # result= json.loads(result)
            # print("type of result2 ", type(result))
            output = format_output(result)
            # output = json.loads(output)
            # print("Complete formatted Output", output)
            chat_history = output.get('Chat_History',[])
            
            # print("CHat history: ",chat_history )

            response = {
                "question": output.get('Question', ''),
                "answer": output.get('Answer', ''),
                "sources": output.get('Sources', [])
                }
            await websocket.send_text(json.dumps(response))
            
            # Store the chat log in Azure Table Storage with detailed exception handling
            try:
                store_chat_log(
                    session_id, MemberEmail, Chat_ID, plan_id, output.get('Question', ''), output.get('Answer', ''),
                    output.get('Chat_History', []), output.get('Sources', [])
                    )
            except Exception as e:
                print(f"Error storing chat log for session {session_id}: {e}")
                await websocket.send_text(json.dumps({"error": "Failed to store chat log"}))
    
    except WebSocketDisconnect:
        print(f"WebSocket disconnected: {client_address}, Session ID: {session_id}")
    except Exception as e:
        print(f"Unexpected error: {e}")



#Chat_history 

from typing import List, Optional
import ast

# Define the model for the response
class ChatHistoryResponse(BaseModel):
    plan_id: str
    session_id: str
    chat_id: str
    MemberEmail: str
    chat_history: List[str] 


def get_chat_history(MemberEmail):
    table_client = chat_storage_table_client()
    filter_query = f"PartitionKey eq 'chatsession' and MemberEmail eq '{MemberEmail}'"
    result = []
    timestamps = []
    for entity in table_client.query_entities(filter_query, headers={'Accept': 'application/json;odata=nometadata'}):
        result.append(entity)
        timestamps.append(entity._metadata["timestamp"].strftime("%Y-%m-%d %H:%M:%S.%f"))
    result = json.dumps(result)     #converted to a JSON string
    result = json.loads(result)     #JSON string is loaded back into Python objects
    for i in range(len(timestamps)):
        result[i].update({"Timestamp": timestamps[i]})
    return result

# out= get_chat_history('test12@mail1.com')
# print("Output of table", out)



import ast


def format_chat_history(user_chat_history):
    formatted_chat_history = {'chatHistory': []}
    
    chat_id_map = {}

    for chat_json in user_chat_history:
        chat_id = chat_json['ChatID']
        timestamp = chat_json['Timestamp']

        # Create chat history entry
        chat_history_entry = {
            'question': chat_json.get('Question', ''),
            'answer': chat_json.get('Answer', ''),
            'timestamp': timestamp,
            'sources': ast.literal_eval(chat_json.get('Sources', '[]'))  #convert this string into an actual list,
        }

        # Create or update the chat ID entry
        if chat_id not in chat_id_map:
            chat_id_map[chat_id] = []
        
        chat_id_map[chat_id].append(chat_history_entry)

    for chat_id, history in chat_id_map.items():
        formatted_chat_history['chatHistory'].append({chat_id: history})

    return formatted_chat_history





# def format_chat_history(user_chat_history):
#     formatted_chat_history = {'chat_history': []}
    
#     for chat_json in user_chat_history:
#         member_email = chat_json['MemberEmail']
#         chat_id = chat_json['ChatID']
#         timestamp = chat_json['Timestamp']

#         # Create chat ID entry if it doesn't exist
#         if chat_id not in formatted_chat_history['chat_history']:
#             formatted_chat_history['chat_history'][chat_id] = {'chat_history': []}

#         # Create chat history entry
#         chat_history_entry = {
#             'question': chat_json.get('Question', ''),
#             'answer': chat_json.get('Answer', ''),
#             'timestamp': timestamp,
#             'sources': ast.literal_eval(chat_json.get('Sources', '[]'))
#         }

#         # Add chat history entry to the chat ID
#         formatted_chat_history['chat_history'][chat_id].append(chat_history_entry)

#     return formatted_chat_history






# def format_chat_history(user_chat_history):
#     formatted_chat_history = {}
#     for chat_json in user_chat_history:
#         member_email = chat_json['MemberEmail']
#         session_id = chat_json['SessionID']
#         plan_id = chat_json['PlanId']
#         Timestamp = chat_json['Timestamp']

#         # Create user entry if it doesn't exist
#         if member_email not in formatted_chat_history:
#             formatted_chat_history[member_email] = {}

#         # Create session entry if it doesn't exist
#         if session_id not in formatted_chat_history[member_email]:
#             formatted_chat_history[member_email][session_id] = {'plan_id': plan_id, 'chat_history': []}

#         # Create chat history entry
#         chat_history_entry = {
#             'question': chat_json.get('Question', ''),
#             'answer': chat_json.get('Answer', ''),
#             'Timestamp': Timestamp,
#             'Sources': ast.literal_eval(chat_json.get('Sources', '[]'))
#         }

#         # Add chat history entry to the session
#         formatted_chat_history[member_email][session_id]['chat_history'].append(chat_history_entry)

#     return formatted_chat_history



@app.get("/chat_history/{MemberEmail}")
async def chat_history(MemberEmail: str):
    try:
        user_chat_history = get_chat_history(MemberEmail)
        formatted_chat_history = format_chat_history(user_chat_history)

        # chat_history_list = []
        # for data in formatted_chat_history:
        #     plan_id = data['PlanId']
        #     session_id = data['SessionID']
        #     chat_id = data['ChatID']
        #     member_email = data['MemberEmail']

        #     chat_history_str = data['chat_history']
            # try:
            #     chat_history = json.loads(chat_history_str) if chat_history_str else []
            #     if not isinstance(chat_history, list):
            #         logger.warning("chat_history is not a list: %s", chat_history)
            #         chat_history = []
            # except json.JSONDecodeError:
            #     logger.error("Error decoding chat_history: %s", chat_history_str)
            #     chat_history = []

            # chat_history_response = ChatHistoryResponse(
            #     plan_id=plan_id,
            #     session_id=session_id,
            #     chat_id=chat_id,
            #     MemberEmail=member_email,
            #     chat_history=chat_history
            # )
            # chat_history_list.append(chat_history_response)

        return formatted_chat_history

    except Exception as e:
        logger.error("Error retrieving chat history: %s", e)
        raise HTTPException(status_code=500, detail=f"Error retrieving chat history: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True, ws_ping_timeout=None)




