#%%
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
import json
import requests
from pymongo import MongoClient, errors
import ssl
import sys
import importlib
from veetility import snowflake as sf
import functions as func
importlib.reload(func)
import time
import prompts
importlib.reload(func)
importlib.reload(prompts)

#%%

ca = func.CreativeAnalytics(os.getenv('openapi_key'))
#%%
# Replace the following with your cluster's endpoints and credentials
# cluster_endpoint = "creative-analytics.cluster-czulzcunj1ry.us-east-1.docdb.amazonaws.com:27017"
cluster_endpoint = 'docdb-2024-06-13-09-28-52.cluster-czulzcunj1ry.us-east-1.docdb.amazonaws.com'
reader_endpoint = "creative-analytics.cluster-ro-czulzcunj1ry.us-east-1.docdb.amazonaws.com"
username = "creativedb"
password = "creativedb"
database_name = "openai_responses"
collection_name = "main"

# Path to the Amazon DocumentDB root certificate
ca_file_path = "global-bundle.pem"
#%%
# Connection to the cluster endpoint (for writes)
# Create a MongoClient to connect to the DocumentDB cluster via SSH tunnel
cluster_client = MongoClient(
    host=cluster_endpoint,
    tls=True,
    tlsCAFile=ca_file_path,
    tlsAllowInvalidHostnames=True,  # Ignore hostname verification
    username=username,
    password=password,
    directConnection=True,
    authSource='admin',  # Specify the authentication database
    retryWrites=False,  # Disable retryable writes
    # replicaSet="rs0",
    serverSelectionTimeoutMS=30000,  # 30 seconds
    connectTimeoutMS=30000  # 30 seconds
)
# Access the database
db = cluster_client[database_name]
collection = db[collection_name]

# find the current images already been queried so you don't do them again
image_names = collection.find({}, {'image_name': 1, '_id': 0})
cur_images_list = [doc['image_name'] for doc in image_names if 'image_name' in doc]
print(f"image_name_list = {cur_images_list}")
#%%

snowflake_connection_parameters = {
    "account": os.getenv("snowflake_account_soc"),
    "user": 'DB_READ_RIVALIQ',
    "role": 'DB_READ_RIVALIQ',
    "warehouse": os.getenv("snowflake_warehouse_soc"),
    "database": os.getenv("snowflake_database_soc"),
    "schema": os.getenv("snowflake_schema_soc"),
    "password": '#Rival1IQ!',
}
ts = sf.Snowflake(snowflake_connection_parameters)

#%%
df = ts.read_snowflake_to_df(schema='VM_RIVALIQ',table_name='"RIVALIQ_INSTAGRAM"')
  
#%%
df['url_code'] = df['post_link'].apply(lambda x: func.url_shortener(x).split('-')[2])
#%%
#'ig-p-C1sHwMKvl5L.jpg',
company_images = [x for x in os.listdir('images') if 'asda' in x]


# company_images = ['ryanair-ig-reel-Cphg1-osTPc.jpg','ryanair-ig-p-Cu1l9BQMcde.jpg','ryanair-ig-p-C5aZ2n_qUYX.jpg','ryanair-ig-p-Cy75TlfLHzX.jpg','ryanair-ig-reel-Cphg1-osTPc.jpg', 'ryanair-ig-p-Cy75TlfLHzX.jpg']
#%%

for image_name in company_images:
    
    if image_name in cur_images_list:
        continue
    # Encode the image in base 64
    base64_image = func.resize_encode_image(f'images/{image_name}')
    print(f"image_name = {image_name}")

    # Extract the url identifier from the image name
    image_url_code = image_name.split('.')[0].split('-')[3]

    # Look up the post copy of the post by finding it in the df RivalIQ posts
    message = df[df['url_code']==image_url_code]['message'].iloc[0]

    # Retrieve a JSON response from OpenAI
    json_response = ca.image_prompt_openai(base64_image, 
                                           image_name, 
                                           prompts.prompt, 
                                           message)
    
    time.sleep(2)

    
    insert_result = collection.insert_one(json_response)
    print(f"Inserted document ID: {insert_result.inserted_id}")




#%%
# with open(f"{image_name}.json", 'w') as f:
#     json.dump(json.loads(response.text), f, indent=4)

# %%
