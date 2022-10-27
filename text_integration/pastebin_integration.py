import requests
api_dev_key = 'db3z5MMfruGlP861SzdogQJsCBXTYZxb'
username = 'SweetSempai'
password = '99624675373564'
api_user_key = '5484f412c7f0cc4790750ba6e3962cef'

print(requests.post(
    url='https://pastebin.com/api/api_post.php',
    params={
        'api_dev_key': api_dev_key,
        'api_user_key': api_user_key,
        'api_option': 'userdetails'
    }
))