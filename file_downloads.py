#%%
import requests
import mimetypes
import os
import time
from dotenv import load_dotenv
load_dotenv()
import random
import pandas as pd
import functions as func
from functions import CreativeAnalytics
from veetility import snowflake as sf, linkedin_api as li_api

ca = CreativeAnalytics(os.getenv('openapi_key'))

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
df['company_name'].value_counts().head(50)

#%%
# Remove punctuation and whitespace from company name 
df = func.company_name_cleaner(df, 
                               'company_name')

#%%
def groupby_country(x):
    d = {}

    d['post_count'] = x['post_id'].nunique()
    d['impressions_sum'] = x['estimated_impressions'].sum()
    d['impressions_avg'] = round(x['estimated_impressions'].mean(),0)
    d['impressions_median'] = x['estimated_impressions'].median()
    d['applause_total'] = x['applause'].sum()
    d['applause_avg'] = round(x['applause'].mean(),0)
    d['applause_median'] = x['applause'].median()

    return pd.Series(d, index=list(d.keys()))

company_groupby = df.groupby('company_name').apply(groupby_country).reset_index()

company_groupby.sort_values('impressions_median', ascending=False).head(50)
#%%
df_sample = df[df['company_name']=='asos'].sample(200)


#%%
for index, row in df_sample.iterrows():

    post_url = row['post_link']
    image_url = row['image']
    response = requests.get(url=image_url)

    url_id = func.url_shortener(post_url)

    image_name = row['company_name'] + '-' + url_id

    func.download_image_requests(response, image_name)

    time.sleep(5)


# %%

# %%
