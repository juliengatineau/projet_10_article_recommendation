import azure.functions as func
import datetime
import json
import logging
import pandas as pd
import numpy as np
from azure.storage.blob import BlobServiceClient
import os
import io


app = func.FunctionApp()


def get_list_all_reco(userID, clicks, dico, n_reco=5):
    '''Return 5 recommended articles ID to user'''
    try:
        userID = int(userID)
        # Get the list of articles viewed by the user
        var = clicks.loc[clicks['user_id'] == userID]['article_id'].to_list()

        list_of_reco = []

        for article in var:
            article_ids = list(dico[article])
            for article_id in article_ids:
                if article_id in var:
                    article_ids.remove(article_id)
            list_of_reco.extend(article_ids)

        # Convert the list to a pandas Series
        example_series = pd.Series(list_of_reco)

        # Get reco for the last article
        last_reco = list_of_reco[:n_reco]

        # Count the number of occurrences of each
        value_counts = example_series.value_counts()
        filtered_value_counts = value_counts[value_counts > 1]

        if len(filtered_value_counts) >= n_reco:
            # get the n_reco most common articles
            reco = filtered_value_counts.index[:n_reco].tolist()
        else:
            # get the n_reco most common articles and complete with the last reco
            reco = filtered_value_counts.index.tolist()
            last_reco = list_of_reco[:n_reco]
            i = 0
            while len(reco) < n_reco and i < len(last_reco):
                if last_reco[i] not in reco:
                    reco.append(last_reco[i])
                i += 1

        return reco
    except KeyError as e:
        logging.error(f"Error: Article ID {e} not found in recommendation dictionary.")
        return []
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        return []

@app.route(route="reco", auth_level=func.AuthLevel.ANONYMOUS)
def reco(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    user_id = req.params.get('userID')
    if not user_id:
        try:
            req_body = req.get_json()
            user_id = req_body.get('userID')
        except ValueError:
            return func.HttpResponse(
                "Invalid JSON in request body.",
                status_code=400
            )

    if user_id:
        try:
            # Connect to Azure Blob Storage
            connection_string = os.getenv("AzureWebJobsStorage")
            if not connection_string:
                raise EnvironmentError("AzureWebJobsStorage environment variable is not set.")
            
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            container_name = "projet10"

            # Download the clicks and embeddings data from Blob Storage
            clicks_blob_client = blob_service_client.get_blob_client(container=container_name, blob="clicks_storage.csv")
            reco_blob_client = blob_service_client.get_blob_client(container=container_name, blob="reco_by_article.pkl")

            clicks_data = clicks_blob_client.download_blob().readall()
            reco_data = reco_blob_client.download_blob().readall()

            clicks = pd.read_csv(io.BytesIO(clicks_data))
            reco_by_article = pd.read_pickle(io.BytesIO(reco_data))

            # Get recommendations
            recommendations = get_list_all_reco(user_id, clicks, reco_by_article)

            # Convert recommendations to native Python types
            recommendations = [int(reco) for reco in recommendations]

            logging.info(f'Recommendations: {recommendations}')

            return func.HttpResponse(
                json.dumps({"Recommended articles": recommendations}),
                status_code=200,
                mimetype="application/json"
            )

        except EnvironmentError as e:
            logging.error(str(e))
            return func.HttpResponse(
                "Internal server error: Configuration issue.",
                status_code=500
            )
        except Exception as e:
            logging.error(f"Error processing request: {str(e)}")
            return func.HttpResponse(
                "Internal server error.",
                status_code=500
            )
    else:
        return func.HttpResponse(
            "Please pass a userID on the query string or in the request body.",
            status_code=400
        )