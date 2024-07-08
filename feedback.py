from fastapi import FastAPI, HTTPException
# from main import chat_storage_table_client
from azure.data.tables import UpdateMode
from azure.data.tables import TableServiceClient
import json
import uuid
import configparser
import logging
config = configparser.ConfigParser()
config.read("config.ini")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

        logger.info(f"Successfully connected to Azure Table Storage: {chat_table}")
        return table_client
    
    except Exception as e:
        logger.error("Error connecting to Azure Table Storage: %s", e)
        raise HTTPException(status_code=500, detail=f"Error connecting to Azure Table Storage: {str(e)}")


def store_chat_log(session_id,MemberEmail, Chat_ID, Query_ID, plan_id, question, answer, chat_history, sources, Rating,feedback):
    try:
        table_client = chat_storage_table_client()

        if not isinstance(sources, list):
            sources = [sources]
                # Check if an entity with the given session_id already exists
        # filter_query=f"PartitionKey eq 'chatsession' and SessionID eq '{session_id}'"
        # existing_entities = list(table_client.query_entities(filter_query))

        # if existing_entities:
        #     # If the entity exists, update it with the feedback and rating
        #     for entity in existing_entities:
        #         if Rating is not None:
        #             entity['Rating'] = Rating
        #         if feedback is not None:
        #             entity['Feedback'] = feedback
        #         table_client.update_entity(entity=entity, mode=UpdateMode.MERGE)
        # else:          
        RowKey=str(uuid.uuid4())
        chat_log_entity = {
            'PartitionKey': 'chatsession',
            'RowKey': RowKey,  
            'SessionID': str(session_id),
            'MemberEmail': MemberEmail,
            'ChatID': str(Chat_ID),
            'Query_ID': str(Query_ID),
            'PlanId': str(plan_id),
            'Question': question,
            'Answer': answer,
            'chat_history':json.dumps(chat_history),
            'Sources': json.dumps(sources),
            'Rating':Rating,
            'Feedback': feedback 
        }

        logger.info(f"Attempting to store entity: {chat_log_entity}")

        table_client.create_entity(entity=chat_log_entity)
        logger.info(f"Entity stored successfully: {chat_log_entity}")

    except Exception as e:
        logger.error("Error storing chat log: %s", e)
        raise HTTPException(status_code=500, detail=f"Error storing chat log: {str(e)}")



def update_chat_log_with_feedback(session_id,Query_ID, Rating, feedback):
    try:
        table_client = chat_storage_table_client()

        # Query for the existing entity by session_id
        filter_query = f"SessionID eq '{session_id}' and Query_ID eq '{Query_ID}'"
        existing_entities = list(table_client.query_entities(filter_query))

        if existing_entities:
            # Update the existing entity with Rating and Feedback
            for entity in existing_entities:
                if Rating is not None:
                    entity['Rating'] = Rating
                if feedback is not None:
                    entity['Feedback'] = feedback
                table_client.update_entity(entity=entity, mode=UpdateMode.MERGE)
        else:
            raise Exception(f"No existing entity found for session ID: {session_id}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating chat log: {str(e)}")

