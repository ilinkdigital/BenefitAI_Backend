
### Data loading


import os
import openai
from dotenv import load_dotenv
load_dotenv()
import chromadb
import uuid
from langchain_chroma import Chroma
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import UnstructuredExcelLoader

# Load environment variables
os.environ["OPENAI_API_TYPE"] = openai.api_type = "azure"
os.environ["OPENAI_API_VERSION"] = openai.api_version = "2024-02-15-preview"
os.environ["AZURE_OPENAI_ENDPOINT"] = openai.azure_endpoint = "https://idocopenaigpt.openai.azure.com/"
os.environ["AZURE_OPENAI_API_KEY"] = openai.api_key = "95776649ac7a4b048c834003fd315264"

# Initialize embeddings
embeddings = AzureOpenAIEmbeddings(azure_deployment="ilinkEmbeddingModel")


def load_documents_and_retriever():

    # print('Loading CSV Data')
        # # Load CSV data and create vector databases
        
    # loader = CSVLoader("D://Project//BenefitsAI//taxonomy_csv//Gold_Plan_Benefits.csv")
    # gold_data = loader.load()

    # print("Gold Taxonomy data loaded ")
    # # #Splitting into chunks- coverage excel
    # text_splitter_coverage = RecursiveCharacterTextSplitter(separators="####", chunk_size=1400, chunk_overlap=100,)
    # chunks_gold_coverage = text_splitter_coverage.split_documents(gold_data)

    # print("Chunks created ")
    # def chunks_to_text_and_metadata_exl(chunks):
    #     def format_metadata(metadata):
    #         if isinstance(metadata, dict):
    #             return {k: str(v) if not isinstance(v, (str, int, float, bool)) else v for k, v in metadata.items()}
    #         return {"metadata": metadata} if isinstance(metadata, str) else metadata

    #     # Update attribute names based on inspection
    #     texts = [chunk.page_content for chunk in chunks]  # Assuming 'page_content' is the correct attribute for text
    #     metadatas = [format_metadata(chunk.metadata) for chunk in chunks]

    #     return texts, metadatas

    # gold_texts, gold_metadatas = chunks_to_text_and_metadata_exl(chunks_gold_coverage)
   
    # print("texts and metadata created")

    persist_directory = 'db//gold'

    client_gold = chromadb.PersistentClient('db//gold')
    
    # print("Collection created ")
    # # Creating vectordb
    # gold_txt_vectordb = Chroma.from_texts(texts=gold_texts, ids= [str(uuid.uuid1()) for _ in chunks_gold_coverage], embedding=embeddings, metadatas=gold_metadatas, persist_directory = persist_directory, collection_name='gold', client=client_gold)

    # Reload the vector stores from disk
    # print("Vector embedding creaed")
    gold_vectorstore = Chroma(persist_directory=persist_directory, collection_name="gold", client=client_gold, embedding_function=embeddings)
    silver_vectorstore = Chroma(persist_directory=persist_directory, collection_name="gold", client=client_gold, embedding_function=embeddings)
    bronze_vectorstore = Chroma(persist_directory=persist_directory, collection_name="gold", client=client_gold, embedding_function=embeddings)

    # print("retrieval Loaded ")

    # Configure db_retrievers for each vector store
    gold_retriever = gold_vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 2})
    silver_retriever = silver_vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 2})
    bronze_retriever = bronze_vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 2})

    return gold_retriever, silver_retriever,bronze_retriever


# print("Loaded embd: ", load_documents_and_retriever())


