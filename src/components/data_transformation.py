#transform your data into ml algorithm readable form 

import os
import sys 
from dataclasses import dataclass
import numpy as np 
import pandas as pd 
from src.utils import save_object

from sklearn.compose import ColumnTransformer 
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder,StandardScaler

from src.exception import CustomException
from src.logger import logging

@dataclass
class DataTransformationConfig:
    preprocessor_obj_file_path= os.path.join('artifacts','preprocessor.pkl')

class DataTransformation:
    '''
    This function is responsible for data transformation
    '''
    def __init__(self) -> None:
        self.data_transformation_config=DataTransformationConfig()
    
    def get_data_transformer_object(self): #to create a pkl file for the preprocessor
        try: 
            numerical_columns = ["writing_score", "reading_score"]
            categorical_columns = [
                "gender",
                "race_ethnicity",
                "parental_level_of_education",
                "lunch",
                "test_preparation_course"
            ]
            
            num_pipeline =Pipeline(
                steps=[
                    ("imputer",SimpleImputer(strategy="median")),#to handle missing values
                    ("scaler",StandardScaler())
                ]
            
            )
            
            cat_pipeline = Pipeline(
                steps=[
                    ("imputer",SimpleImputer(strategy="most_frequent")),
                    ("one_hot_encoder",OneHotEncoder())
                    # ("scaler",StandardScaler())        
                ]
            )
            logging.info(f"Numerical columns Standard scaling  done")
            
            logging.info(f"Categorical columns Encoding done")
            
            preprocessor=ColumnTransformer(
                transformers=[("num_pipeline",num_pipeline,numerical_columns),
                ("cat_pipeline",cat_pipeline,categorical_columns)]
                
            )
            logging.info(f"preprocessor {preprocessor}")
            return preprocessor
            
        except Exception as e:
            raise CustomException(e,sys)

    def initiate_data_transformation(self,train_path,test_path):
        try: 
            train_df=pd.read_csv(train_path)
            test_df=pd.read_csv(test_path)
            
            logging.info("Read train and test data completed")
            
            logging.info("Obtaining preprocessing object")
            preprocessor_obj=self.get_data_transformer_object()
            
            target_column_name="math_score"
            numerical_columns = ["writing_score", "reading_score"]
            
            input_feature_train_df=train_df.drop(columns=[target_column_name],axis=1)
            target_feature_train_df=train_df[target_column_name]
            
            input_feature_test_df = test_df.drop(columns=[target_column_name],axis=1)
            target_feature_test_df = test_df[target_column_name]
            
            logging.info(
                f"Applying preprocessing object on training dataframe and testing dataframe"

            )
            
            input_feature_train_arr=preprocessor_obj.fit_transform(input_feature_train_df)
            input_feature_test_arr=preprocessor_obj.fit_transform(input_feature_test_df)
            
            train_arr=np.c_[
                input_feature_train_arr,np.array(target_feature_train_df)
            ]
            
            test_arr = np.c_[
                input_feature_test_arr,np.array(target_feature_test_df)]
            
            save_object(
                file_path=self.data_transformation_config.preprocessor_obj_file_path,
                obj=preprocessor_obj
            )
            return (train_arr,
                    test_arr,
                    )
            
        except Exception as e :
            raise CustomException(e,sys)