import requests


def get_text_api(api_paste_key: str):
    api_dev_key = 'db3z5MMfruGlP861SzdogQJsCBXTYZxb'
    token = 'f4d630137d38644be8929ad54247b188'
    data = {
        'api_dev_key': api_dev_key,
        'api_user_key': token,
        'api_paste_key': api_paste_key,
        'api_option': 'show_paste'
    }
    r = requests.post("https://pastebin.com/api/api_raw.php", data=data)
    return r.text

