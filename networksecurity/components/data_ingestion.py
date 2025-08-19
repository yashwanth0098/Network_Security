from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

# configuration of the data Ingeastion Config
from networksecurity.enitity.config_entity import DataIngestionConfig
from networksecurity.enitity.artifacts import DataIngestionArtifact

import os
import sys
import pymongo
from sklearn.model_selection import train_test_split
from dataclasses import dataclass
import numpy as np
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")
print(MONGO_DB_URL)

import certifi
ca= certifi.where()

class DataIngestion:
    def __init__(self,data_ingestion_config:DataIngestionConfig):
        try:
           self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    def export_collection_as_dataframe(self): # This is where the mongodb connection is made and data is fetched for the Data ingestion
        """
        Read data from mongodb
        """
        try:
            database_name=self.data_ingestion_config.database_name
            collection_name=self.data_ingestion_config.collection_name
            self.mongo_client=pymongo.MongoClient(MONGO_DB_URL)
            collection=self.mongo_client[database_name][collection_name]
            
## Fetch all documents from the MongoDB collection, convert the cursor object into a list of dictionaries,
# and then load it into a Pandas DataFrame for further processing.        
            df=pd.DataFrame(list(collection.find()))
            if "_id" in df.columns.to_list():
                df=df.drop(columns=["_id"],axis=1)
                
            df.replace({"na":np.nan},inplace=True)
            return df
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def export_data_into_feature_store(self,dataframe:pd.DataFrame):
        try:
            feature_store_file_path=self.data_ingestion_config.feature_store_file_path
            dir_path=os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path,exist_ok=True)
            dataframe.to_csv(feature_store_file_path,index=False,header=True)
            return dataframe
    
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def split_data_as_train_test(self,dataframe:pd.DataFrame):
        try:
            train_data,test_data=train_test_split(dataframe,test_size=self.data_ingestion_config.train_test_split_ratio)
            
            logging.info("performed train test split on the dataframe")
            
            logging.info(
                "Exited split_data_as_train_test method of Data_ingestion class"
            )
            
            dir_path=os.path.dirname(self.data_ingestion_config.training_file_path)
            
            os.makedirs(dir_path,exist_ok=True)
            
            logging.info(f"Exporting train and test file path.")
            
            train_data.to_csv(self.data_ingestion_config.training_file_path,index=False,header=True)
            
            test_data.to_csv(self.data_ingestion_config.testing_file_path,index=False,header=True)
            
            logging.info(f"Exported train and test file path.")
            
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    
    def initiate_data_ingestion(self):
        try:
            dataframe=self.export_collection_as_dataframe()
            dataframe=self.export_data_into_feature_store(dataframe)
            self.split_data_as_train_test(dataframe)
            dataingestionartifacts=DataIngestionArtifact(
                trained_file_path=self.data_ingestion_config.training_file_path,
                test_file_path=self.data_ingestion_config.testing_file_path)
            return dataingestionartifacts
        except Exception as e:
            raise NetworkSecurityException(e,sys)