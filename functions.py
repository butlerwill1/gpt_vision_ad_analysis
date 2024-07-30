#%%
import requests
import mimetypes
import os
import time
from dotenv import load_dotenv
load_dotenv()
from PIL import Image
import io
from datetime import datetime
import base64
import json
import pandas as pd
import random
#%%
def download_image_requests(image_response: requests.Response,
                             image_name: str) -> None:

    if image_response.status_code == 200:
        # Try to guess the file extension from the content type
        content_type = image_response.headers['Content-Type']
        extension = mimetypes.guess_extension(content_type)

        # If the content type cannot be guessed, default to .jpg
        if not extension:
            extension = '.jpg'

        # Construct a filename using a simple increment or a UUID
        filename = f'{image_name}{extension}'

        # Save the image to the local file system
        save_path = os.path.join("images", filename)
        with open(save_path, 'wb') as f:
            f.write(image_response.content)

        print(f"Image saved as {save_path}")
    else:
        print("Failed to download image:", image_response.status_code)

def company_name_cleaner(df: pd.DataFrame,
                         company_name_col: str):
    
    df[company_name_col] = df[company_name_col].str.lower().str.replace(r'[\d\W_]+', '', regex=True)

    return df


def url_shortener(url: str):

    if 'facebook' in url:
        platform = 'fb'
    if 'instagram' in url:
        platform = 'ig'
    if 'tiktok' in url:
        platform = 'tt'

    short_url = url.split('.com/')[1]

    if short_url.endswith('/'):
        short_url = short_url[:-1]

    short_url = short_url.replace('/', '-')

    short_url = platform + '-' + short_url

    return short_url

class CreativeAnalytics:
    def __init__(self, api_token):
        self.api_token = api_token

    def exponential_backoff_delay(self, retry_count):
        """Implements an exponential backoff delay with jitter for server response problems.
            
            Args:
                retry_count (int): The number of times the request has been retried.
                
            Side Effects:
                Introduces a time delay into the program execution.
                
            Notes:
                The delay is calculated as follows:
                    delay = (4 ** retry_count + 1) * 5
                A jitter (random noise) is also added to the delay."""
        
        delay = (4 ** retry_count + 1) * 5 # Exponential backoff
        jitter = random.uniform(0, 0.1 * delay)  # Adding jitter
        print(f"Starting exponential delay of {round(delay + jitter,2)} seconds to give server time to recover")
        time.sleep(delay + jitter)

    def run_request_with_error_handling(self, 
                                        url, 
                                        method='get',
                                        headers=None, 
                                        params=None,
                                        json=None,  
                                        max_retries=4, 
                                        stop_at_perm=False 
        ):
        """Wrapper function to execute an HTTP GET request with error handling and mutliple time delayed retries.
            
        Args:
            url (str): The URL endpoint to call.
            headers (dict): The headers to include in the request.
            params (dict, optional): The parameters to include in the request. Defaults to None.
            max_retries (int, optional): The maximum number of times to retry the request. Defaults to 5.

        Returns:
            requests.Response: The response object if the request is successful.

        Raises:
            HTTPError: If a permanent HTTP error occurs (status code 400, 401, 403).
            Exception: If an unexpected error occurs or if the request fails multiple times."""

        try:
            if method == 'get':
                response = requests.get(url=url, headers=headers, params=params)
            if method == 'post':
                response = requests.post(url=url, headers=headers, json=json)
            
            self.response = response
            response.raise_for_status()
            rate_limit_info = {
                'Limit': response.headers.get('RateLimit-Limit'),
                'Remaining': response.headers.get('RateLimit-Remaining'),
                'Reset': response.headers.get('RateLimit-Reset'),
            }

            print(f"{rate_limit_info}")

            # This is the only place anything gets returned
            if response.status_code == 200:
                self.retry_count=0
                return response

        except requests.exceptions.HTTPError as ehttp:
        
            if ehttp.response.status_code == 429:
                print(f"This is a Rate limit error code :{response.status_code}: message: {response.json()['message']}\
                            Request params are: {params}. Visit https://learn.microsoft.com/en-us/linkedin/shared/api-guide/concepts/rate-limits for more info" )
                self.exponential_backoff_delay(self.retry_count)

            elif ehttp.response.status_code in [400, 401, 403]:
                print(f"Permanent HTTP Error: {response.status_code}, message: {response.json().get('message', '')}, Request params are: {params}.")
                if stop_at_perm is True:
                    raise Exception(f"Permanent HTTP Error: {response.status_code}, message: {response.json().get('message', '')}, Request params are: {params}.")
                else:
                    self.exponential_backoff_delay(self.retry_count)

            elif ehttp.response.status_code in [429, 500, 502, 503, 504]:
                print(response.json())
                print(f'headers = {response.headers}')
                print(f"Temporary HTTP Error: {response.status_code}, message: {response.json().get('message', '')}, Request params are: {params}.")
                self.exponential_backoff_delay(self.retry_count)  # Or follow the Retry-After header if available
            
            else:
                print(f"Unexpected HTTP Error: {response.status_code}, message: {response.json().get('message', '')}, Request params are: {params}.")
                
        except Exception as e:
            # Catch all other exceptions
            print(f"An unexpected error occurred: {e}, Request params are: {params}. url = {url}")
            self.exponential_backoff_delay(self.retry_count)

        # Increment and check retries for potentially temporary issues
        self.retry_count += 1
        if self.retry_count <= max_retries:
            return self.run_request_with_error_handling(url, headers, params)
        else:
            raise Exception("Multiple Errors occured- Check Logs")
        
    def image_prompt_openai(self, base64_image, image_name, prompt, prompt_variable):
        headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }

        payload = {
        "model": "gpt-4o",
        "messages": [
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": prompt.format(prompt_variable)
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
                }
            ]
            }
        ],
        "response_format":
            {"type": "json_object"}

        }
        # print(prompt.format(prompt_variable))
        try:
            url = "https://api.openai.com/v1/chat/completions"
            # response = requests.post(url=url, headers=headers, json=payload)

            response = self.run_request_with_error_handling(url=url, 
                                                            headers=headers,
                                                            method='post',
                                                            json=payload,
                                                            )

            if response.status_code != 200:
                print(f"Error - {response.status_code} - {response.text}")
                return None


            json_output = json.loads(response.text)
            
            json_output['choices'][0]["message"]["content"] = json.loads(json_output['choices'][0]["message"]["content"])
        
        except Exception as e:
            print(f"Excaption Occured {e}")

        json_output['image_name'] = image_name
        json_output['response_date'] = datetime.now()

        print(f"Response = {json_output}")

        return json_output

def resize_encode_image(image_path, output_size=(512, 512)):
    with Image.open(image_path) as img:
        img = img.resize(output_size, Image.Resampling.LANCZOS)
        with io.BytesIO() as output:
            img.save(output, format='JPEG')
            return base64.b64encode(output.getvalue()).decode('utf-8')