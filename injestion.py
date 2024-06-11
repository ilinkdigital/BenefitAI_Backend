
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

    # loader1 = DirectoryLoader("D://Project//BenefitsAI//data2//gold", glob="**/*.txt")
    # Gold_docs = loader1.load()

    # loader2 = DirectoryLoader("D://Project//BenefitsAI//data2//silver", glob="**/*.txt")
    # Silver_docs = loader2.load()

    # loader3 = DirectoryLoader("D://Project//BenefitsAI//data2//bronze", glob="**/*.txt")
    # Bronze_docs = loader3.load()

    # print("Data loaded ")
    # # # Splitting into chunks

    # text_splitter = RecursiveCharacterTextSplitter(chunk_size=1400, chunk_overlap=300)
    # chunks1 = text_splitter.split_documents(Gold_docs)
    # chunks2 = text_splitter.split_documents(Silver_docs)
    # chunks3 = text_splitter.split_documents(Bronze_docs)

    # print("Chunks created ")
    # # # Helper function to convert chunks to text and metadata
    # def chunks_to_text_and_metadata(chunks):
    #     texts = [chunk.page_content for chunk in chunks]
    #     metadatas = [chunk.metadata for chunk in chunks]
    #     return texts, metadatas


    # # # # # Prepare data for each collection
    # gold_texts, gold_metadatas = chunks_to_text_and_metadata(chunks1)
    # silver_texts, silver_metadatas = chunks_to_text_and_metadata(chunks2)
    # bronze_texts, bronze_metadatas = chunks_to_text_and_metadata(chunks3)
    # # print("texts and metadata created")

    persist_directory1 = 'db4//gold'
    persist_directory2 = 'db4//silver'
    persist_directory3 = 'db4//bronze'

    client_gold = chromadb.PersistentClient('db4//gold')
    client_silver = chromadb.PersistentClient('db4//silver')
    client_bronze = chromadb.PersistentClient('db4//bronze')

    
    # print("Collection created ")
    # # Creating vectordb
    # gold_txt_vectordb = Chroma.from_texts(texts=gold_texts, ids= [str(uuid.uuid1()) for _ in chunks1], embedding=embeddings, metadatas=gold_metadatas, persist_directory = persist_directory1, collection_name='gold', client=client_gold)
    # silver_txt_vectordb = Chroma.from_texts(texts=silver_texts, ids= [str(uuid.uuid1()) for _ in chunks2], embedding=embeddings, metadatas=silver_metadatas, persist_directory = persist_directory2, collection_name='silver', client=client_silver)
    # bronze_txt_vectordb = Chroma.from_texts(texts=bronze_texts, ids= [str(uuid.uuid1()) for _ in chunks3], embedding=embeddings, metadatas=bronze_metadatas, persist_directory = persist_directory3, collection_name='bronze', client=client_bronze)

    # print("Embeddings created ")

    # Reload the vector stores from disk
    gold_vectorstore = Chroma(persist_directory=persist_directory1, collection_name="gold", client=client_gold, embedding_function=embeddings)
    silver_vectorstore = Chroma(persist_directory=persist_directory2, collection_name="silver", client=client_silver, embedding_function=embeddings)
    bronze_vectorstore = Chroma(persist_directory=persist_directory3, collection_name="bronze", client=client_bronze, embedding_function=embeddings)

    # print("retrieval Loaded ")

    # Configure db_retrievers for each vector store
    gold_retriever = gold_vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    silver_retriever = silver_vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    bronze_retriever = bronze_vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})

    # Loading coverage excel file
    # print("Starting with Coverage and Taxonomy csv file")

    # loader3 = DirectoryLoader("D://Project//BenefitsAI//csv_updated_coverage//csv//gold", glob="**/*.csv", loader_cls=CSVLoader)
    # gold_docs = loader3.load()

    # loader3 = DirectoryLoader("D://Project//BenefitsAI//csv_updated_coverage//csv//silver", glob="**/*.csv", loader_cls=CSVLoader)
    # silver_docs = loader3.load()

    # loader3 = DirectoryLoader("D://Project//BenefitsAI//csv_updated_coverage//csv//bronze", glob="**/*.csv", loader_cls=CSVLoader)
    # bronze_docs = loader3.load()

   
    # print("coverage data loaded ")
    # #Splitting into chunks- coverage excel
    # text_splitter_coverage = RecursiveCharacterTextSplitter(separators="####", chunk_size=1000, chunk_overlap=50,)
    # chunks_gold_coverage = text_splitter_coverage.split_documents(gold_docs)

    # chunks_silver_coverage = text_splitter_coverage.split_documents(silver_docs)

    # chunks_bronze_coverage = text_splitter_coverage.split_documents(bronze_docs)

    # # print("Chunks created ")
    # def chunks_to_text_and_metadata_exl(chunks):
    #     def format_metadata(metadata):
    #         if isinstance(metadata, dict):
    #             return {k: str(v) if not isinstance(v, (str, int, float, bool)) else v for k, v in metadata.items()}
    #         return {"metadata": metadata} if isinstance(metadata, str) else metadata

    #     # Update attribute names based on inspection
    #     texts = [chunk.page_content for chunk in chunks]  # Assuming 'page_content' is the correct attribute for text
    #     metadatas = [format_metadata(chunk.metadata) for chunk in chunks]

    #     return texts, metadatas

    # gold_texts_cvrg, gold_metadatas_cvrg = chunks_to_text_and_metadata_exl(chunks_gold_coverage)
    # silver_texts_cvrg, silver_metadatas_cvrg = chunks_to_text_and_metadata_exl(chunks_silver_coverage)
    # bronze_texts_cvrg, bronze_metadatas_cvrg = chunks_to_text_and_metadata_exl(chunks_bronze_coverage)
   
    # print("texts and metadata created")
    
    # print("Creating vectordb")
    # coverage excel vectordb
    # gold_coverage_vectordb = Chroma.from_texts(texts=gold_texts_cvrg, ids= [str(uuid.uuid1()) for _ in chunks_gold_coverage], embedding=embeddings, metadatas=gold_metadatas_cvrg, persist_directory = persist_directory1, collection_name='gold', client=client_gold)
    # silver_coverage_vectordb = Chroma.from_texts(texts=silver_texts_cvrg, ids= [str(uuid.uuid1()) for _ in chunks_silver_coverage], embedding=embeddings, metadatas=silver_metadatas_cvrg, persist_directory = persist_directory2, collection_name='silver', client=client_silver)
    # bronze_coverage_vectordb = Chroma.from_texts(texts=bronze_texts_cvrg, ids= [str(uuid.uuid1()) for _ in chunks_bronze_coverage], embedding=embeddings, metadatas=bronze_metadatas_cvrg, persist_directory = persist_directory3, collection_name='bronze', client=client_bronze)
    # # print("Vector embedding creaed")

    #Loading a vectorstore
    # print("Loading vectordb from local")
    gold_vectorstore = Chroma(persist_directory=persist_directory1, collection_name="gold", client=client_gold, embedding_function=embeddings)
    silver_vectorstore = Chroma(persist_directory=persist_directory2, collection_name="silver", client=client_silver, embedding_function=embeddings)
    bronze_vectorstore = Chroma(persist_directory=persist_directory3, collection_name="bronze", client=client_bronze, embedding_function=embeddings)

    # print("retrieval loaded")
    gold_retriever = gold_vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    silver_retriever = silver_vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    bronze_retriever = bronze_vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})


    return gold_retriever, silver_retriever,bronze_retriever


# print("Loaded embd: ", load_documents_and_retriever())