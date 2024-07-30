#%%
import os
import io
import json
from pymongo import MongoClient, errors
import functions as func
import pandas as pd
from veetility import snowflake as sf
import importlib
importlib.reload(func)
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

# Access the collection
collection = db[collection_name]

#%%
rivaliq_snowflake_params = {
    "account": os.getenv("snowflake_account_soc"),
    "user": 'DB_READ_RIVALIQ',
    "role": 'DB_READ_RIVALIQ',
    "warehouse": os.getenv("snowflake_warehouse_soc"),
    "database": os.getenv("snowflake_database_soc"),
    "schema": os.getenv("snowflake_schema_soc"),
    "password": '#Rival1IQ!',
}

soc_snowflake_params = {
    "account": os.getenv("snowflake_account_soc"),
    "user": os.getenv("snowflake_user_soc"),
    "role": os.getenv("snowflake_user_role_soc"),
    "warehouse": os.getenv("snowflake_warehouse_soc"),
    "database": os.getenv("snowflake_database_soc"),
    "schema": os.getenv("snowflake_schema_soc"),
    "password": os.getenv("snowflake_password_soc"),
}

rival_snowflake = sf.Snowflake(rivaliq_snowflake_params)
soc_snowflake = sf.Snowflake(soc_snowflake_params)
#%%
def groupby_func(x, agg_name):
    d = {}

    d[f'{agg_name}_median_impr'] = x['estimated_impressions'].median()
    d[f'{agg_name}_avg_impr'] = x['estimated_impressions'].mean()
    d[f'{agg_name}_median_applause'] = x['applause'].median()
    d[f'{agg_name}_avg_applause'] = x['applause'].mean()
    d[f'{agg_name}_post_count'] = x.shape[0]

    return pd.Series(d, index=list(d.keys()))

def extract_category(choice, extract_name):
    try:
        # Check if the list is not empty and the required keys exist
        if choice and isinstance(choice, list):
            if 'message' in choice[0] and 'content' in choice[0]['message']:
                return choice[0]['message']['content'].get(extract_name, None)
    except TypeError:
        # Handle cases where choice is not a list or indexing fails
        return None
    return None

#%%
df = rival_snowflake.read_snowflake_to_df(schema='VM_RIVALIQ',table_name='"RIVALIQ_INSTAGRAM"')

# df['url_code'] = df['post_link'].apply(lambda x: func.url_shortener(x).split('-')[2]) + ".jpg"
#%%
df = func.company_name_cleaner(df, 
                               'company_name')

df['url_code'] = df['company_name'] + "-" + df['post_link'].apply(lambda x: func.url_shortener(x)) + ".jpg"


#%%
mongo_df = pd.DataFrame(list(collection.find({})))

mongo_df['Category'] = mongo_df['choices'].apply(lambda x: extract_category(x, 'Category'))

mongo_df['Emotion'] = mongo_df['choices'].apply(lambda x: extract_category(x,'Emotion'))

mongo_df['DominantColour'] = mongo_df['choices'].apply(lambda x: extract_category(x,'DominantColour'))

mongo_df['EmotionalIntensity'] = mongo_df['choices'].apply(lambda x: extract_category(x,'EmotionalIntensity'))

mongo_df['NumberOfPeople'] = mongo_df['choices'].apply(lambda x: extract_category(x,'NumberOfPeople'))

mongo_df['GenderOfPeople'] = mongo_df['choices'].apply(lambda x: extract_category(x,'GenderOfPeople'))

mongo_df = mongo_df[['image_name','Category','DominantColour' ,'Emotion', 'EmotionalIntensity', 'NumberOfPeople']]

print(f"Mongo df sample = {mongo_df.sample(10)}")

df_combined = pd.merge(mongo_df, df, left_on='image_name', right_on='url_code', how='inner')

print(f"{df_combined.columns}")

soc_snowflake.write_df_to_snowflake(df_combined, 
                                    table_name="CREATIVE_ANALYTICS",
                                    auto_create_table=True,
                                    overwrite=True)


category_groupby = df_combined.groupby("Category").apply(lambda x: groupby_func(x, 'category'))

emotion_groupby = df_combined.groupby("Emotion").apply(lambda x: groupby_func(x, 'emotion'))

print(emotion_groupby)

print(category_groupby)
# #%%
# image_names = collection.find({}, {'image_name': 1, '_id': 0})
# #%%
# cur_images_list = [doc['image_name'].replace(".jpg", "") for doc in image_names if 'image_name' in doc]

# # %%
# print("\nAggregation result (group by content.Category):")
# pipeline = [
#     {"$unwind": "$choices"},
#     {"$group": {"_id": "$choices.message.content.Category", "count": {"$sum": 1}}}
# ]
# results = list(collection.aggregate(pipeline))
# for result in results:
#     print(result)