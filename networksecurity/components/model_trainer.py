import os
import sys

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.enitity.artifacts import DataTransformationArtifact, ModelTrainerArtifact
from networksecurity.enitity.config_entity import ModelTrainerConfig

from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.utils.main_utils.utils import save_object, load_object, load_numpy_array_data, evaluate_model
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_metric

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier,
    AdaBoostClassifier,
    GradientBoostingClassifier,
)

import mlflow



import dagshub
dagshub.init(repo_owner='yashwanth0098', repo_name='Network_Security', mlflow=True)

# import mlflow
# with mlflow.start_run():
#   mlflow.log_param('parameter name', 'value')
#   mlflow.log_metric('metric name', 1)

class ModelTrainer:
    def __init__(self, model_trainer_config: ModelTrainerConfig, data_transformation_artifact: DataTransformationArtifact):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def track_mlflow(self,best_model,classifcationmetric):
        with mlflow.start_run():
            f1_score=classifcationmetric.f1_score
            precision_score=classifcationmetric.precision_score
            recall_score=classifcationmetric.recall_score
                
            mlflow.log_metric("f1_score",f1_score)
            mlflow.log_metric("precision_score",precision_score)
            mlflow.log_metric("recall_score",recall_score)  
            mlflow.sklearn.log_model(best_model,"model")
            

    def train_model(self, X_train, y_train, x_test, y_test):
        try:
            model = {
                "Random Forest": RandomForestClassifier(verbose=1),
                "Decision Tree": DecisionTreeClassifier(),
                "Gradient Boosting": GradientBoostingClassifier(verbose=1),
                "Ada Boost": AdaBoostClassifier(),
                "Logistic Regression": LogisticRegression(verbose=1),
            }

            params = {
                "Decision Tree": {
                    'criterion': ['gini', 'entropy', "log_loss"],
                },
                "Random Forest": {
                    "n_estimators": [8, 16, 32, 64, 128, 256]
                },
                "Gradient Boosting": {
                    "learning_rate": [0.1, 0.01, 0.05, 0.001],
                    "n_estimators": [8, 16, 32, 64, 128, 256]
                },
                "Logistic Regression": {},
                "Ada Boost": {
                    "learning_rate": [0.1, 0.01, 0.001],
                    "n_estimators": [8, 16, 32, 64, 128, 256]
                }
            }

            model_report: dict = evaluate_model(
                X_train=X_train, y_train=y_train,
                X_test=x_test, y_test=y_test,
                models=model, param=params
            )

            best_model_score = max(sorted(model_report.values()))
            best_model_name = list(model_report.keys())[list(model_report.values()).index(best_model_score)]
            best_model = model[best_model_name]

            # Training metrics
            y_train_pred = best_model.predict(X_train)
            classification_train_metric = get_classification_metric(y_true=y_train, y_pred=y_train_pred)

            ## Track the experiment with mlflow
            self.track_mlflow(best_model, classification_train_metric)

            # Testing metrics
            y_test_pred = best_model.predict(x_test)
            classification_test_metric = get_classification_metric(y_true=y_test, y_pred=y_test_pred)
            
            self.track_mlflow(best_model, classification_test_metric)


            # Load preprocessor
            preprocessor = load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)

            # Ensure directory exists
            model_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)
            if model_dir_path:  # only create if not empty
                os.makedirs(model_dir_path, exist_ok=True)

            # Save trained model (with preprocessing)
            Network_Model = NetworkModel(preprocessor=preprocessor, model=best_model)
            save_object(self.model_trainer_config.trained_model_file_path, obj=Network_Model)
            
            save_object('final_model/model.pkl', best_model)

            # Save final model in Artifacts folder
            final_model_path = os.path.join("Artifacts", "final_model.pkl")
            save_object(final_model_path, best_model)

            # Create artifact
            model_trainer_artifact = ModelTrainerArtifact(
                trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                train_metric_artifact=classification_train_metric,
                test_metric_artifact=classification_test_metric
            )

            logging.info(f'Model trainer artifact: {model_trainer_artifact}')
            return model_trainer_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        try:
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path

            # loading training array and testing array 
            train_array = load_numpy_array_data(train_file_path)
            test_array = load_numpy_array_data(test_file_path)

            x_train, y_train, x_test, y_test = (
                train_array[:, :-1],
                train_array[:, -1],
                test_array[:, :-1],
                test_array[:, -1]
            )

            model_trainer_artifact = self.train_model(x_train, y_train, x_test, y_test)
            return model_trainer_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)
