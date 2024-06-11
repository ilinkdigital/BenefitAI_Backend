# model_setup.py

from langchain_openai import AzureChatOpenAI

# from langchain.chat_models import AzureChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from prompt import qa_prompt
from injestion import load_documents_and_retriever
import re


# Load the retrievers
gold_retriever, silver_retriever, bronze_retriever = load_documents_and_retriever()

model = AzureChatOpenAI(
    azure_endpoint="https://idocopenaigpt.openai.azure.com/",
    api_version="2023-03-15-preview",
    azure_deployment='chatllm16k',
    api_key="95776649ac7a4b048c834003fd315264",
    openai_api_type="azure",
    temperature=0
)

memory = ConversationBufferMemory(memory_key="chat_history", output_key='answer', return_messages=False)

gold_chain = ConversationalRetrievalChain.from_llm(
    llm=model,
    chain_type="stuff",
    retriever=gold_retriever,
    get_chat_history=lambda c:c,
    combine_docs_chain_kwargs={"prompt": qa_prompt},
    return_source_documents=True,
    memory=memory,
#     return_generated_question=True,
    verbose=False,
)

silver_chain = ConversationalRetrievalChain.from_llm(
    llm=model,
    chain_type="stuff",
    retriever=silver_retriever,
    get_chat_history=lambda c:c,
    combine_docs_chain_kwargs={"prompt": qa_prompt},
    return_source_documents=True,
    memory=memory,
#     return_generated_question=True,
    verbose=False,
)


bronze_chain = ConversationalRetrievalChain.from_llm(
    llm=model,
    chain_type="stuff",
    retriever=bronze_retriever,
    get_chat_history=lambda c:c,
    combine_docs_chain_kwargs={"prompt": qa_prompt},
    return_source_documents=True,
    memory=memory,
#     return_generated_question=True,
    verbose=False,
)

def query_collection(collection_name, user_query):
    if collection_name == "gold":
        chain = gold_chain
    elif collection_name == "silver":
        chain = silver_chain
    elif collection_name == "bronze":
        chain = bronze_chain
    else:
        raise ValueError("Invalid collection name")

    response = chain.invoke({"question": user_query})
    return response



def format_output(input_data):
    greeting_words = ["hi", "hello", "hey", "hellow","no","nothing", "got it", "superb", "nice", "good", "great", "awesome", "ok", "sorry"]

    user_query = input_data['question'].lower()

    # Check for exact greeting words in the query
    if any(word in user_query.split() for word in greeting_words):
        return {
            "Question": input_data['question'],
            "Answer": "Hey, I am Document AI assistance Let me know how can i help you",
            "Chat_History": "",
        }
    

    partings = [
        "thanks", "bye", "goodbye", "good bye", "thank you", "thnks","thnkx", "thanks for your help", "thanks for help"
    ]
    if user_query.lower() in partings:
        return {"Question": user_query, 
                "Answer": "No problem! Let me know if you have any further queries.", 
                "Chat_History": []}
    


    # Retrieve other parts of the input data
    question = input_data.get('question')
    answer = input_data.get('answer')
    chat_history = input_data.get('chat_history', '')


    # sources = []
    # if input_data.get('source_documents'):
    #     for doc in input_data['source_documents']:
    #         if isinstance(doc, dict):
    #             if 'source' in doc:
    #                 sources.append(doc['source'])
    #             elif 'metadata' in doc and 'source' in doc['metadata']:
    #                 sources.append(doc['metadata']['source'])
    #         elif hasattr(doc, 'metadata') and 'source' in doc.metadata:
    #             sources.append(doc.metadata['source'])
    #         else:
    #             print("Document object does not contain required metadata.")
    # else:
    #     print("No source documents found")
    sources = []
    disallowed_phrases = ("i'm sorry", "i don't", "thank you", "i'm an ai assistant", "i can assist")
    
    # if not answer.lower().startswith(("i'm sorry", "i don't", "Thank you", "I'm an AI assistant","I can assist")):
    if not any(answer.lower().startswith(phrase) for phrase in disallowed_phrases):
        if input_data.get('source_documents'):
            for doc in input_data['source_documents']:
                if isinstance(doc, dict):
                    if 'source' in doc:
                        sources.append(doc['source'])
                    elif 'metadata' in doc and 'source' in doc['metadata']:
                        sources.append(doc['metadata']['source'])
                elif hasattr(doc, 'metadata') and 'source' in doc.metadata:
                    sources.append(doc.metadata['source'])
                else:
                    print("Document object does not contain required metadata.")
        else:
            print("No source documents found")
    
    # print("Added source", sources)


    sources= [source.split("\\")[-1] if "\\" in source else source.split("//")[-1] for source in sources]
    sources= list(set(sources))

    # Construct the formatted output
    formatted_output = {
        "Question": question,
        "Answer": answer,
        "Chat_History": chat_history,
        "Sources": sources
    }

    return formatted_output


# print("Output", format_output(dic3))

