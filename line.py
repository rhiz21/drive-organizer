import requests

# ------------------------------------------------------------------
# CONSTANT
# ------------------------------------------------------------------
BASE_URL = 'https://api.line.me/v2/bot/message'
ACCESS_TOKEN = 'Zcam+InT/a9aoa90brO2Uy2GT9GC+ARhaFObnRV48n5cA1O3pzcexBhveBMKanSLOdPWSCwCaHLgGRHghvg72v7qIchqQA4Rx1vHPQroK5HkMWHO/ERWFjxiLidHr2aRtZmQIySjQjYZ5HtwPS6M8QdB04t89/1O/w1cDnyilFU='
HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {ACCESS_TOKEN}'
}

# ------------------------------------------------------------------
# CLASS
# ------------------------------------------------------------------
class ResponseError(Exception):
    def __init__(self, msg, code):
        super().__init__(msg)
        self.code = code

class QuickReplyAction:
    def __init__(self, label, text, reply_type='message', image_url=''):
        self.label = label
        self.text = text
        self.type = reply_type
        self.image_url = image_url
    
    def get_json(self):
        return {
            'type': 'action',
            'imageUrl': self.image_url,
            'action': {
                'type': self.type,
                'label': self.label,
                'text': self.text
            }
        }

# ------------------------------------------------------------------
# FUNCTION
# ------------------------------------------------------------------
def push_core(data):
    url = f'{BASE_URL}/push'
    try:
        response = requests.post(url, headers=HEADERS, json=data)
        response.raise_for_status()  # HTTPエラーを例外として扱う
        return {'result': True, 'status': 'succes', 'code': response.status_code}
    except requests.exceptions.HTTPError:
        raise ResponseError(response.text, response.status_code)
    except requests.exceptions.RequestException:
        raise ResponseError(response.text, response.status_code)

def reply_core(data):
    url = f'{BASE_URL}/reply'
    try:
        response = requests.post(url, headers=HEADERS, json=data)
        response.raise_for_status()  # HTTPエラーを例外として扱う
        return {'result': True, 'status': 'succes', 'code': response.status_code}
    except requests.exceptions.HTTPError:
        raise ResponseError(response.text, response.status_code)
    except requests.exceptions.RequestException:
        raise ResponseError(response.text, response.status_code)

def push_text(user_id: str, text: str):
    data = {
        'to': user_id,
        'messages':  [{
            'type': 'text',
            'text': text
        }]
    }
    return push_core(data)

def push_text_quick_reply(user_id: str, text: str, qr_actions):
    items = []
    for action in qr_actions:
        items.append(action.get_json())
    data = {
        'to': user_id,
        'messages': [{
            'type': 'text',
            'text': text,
            'quickReply': {
                'items': items
            }
        }]
    }
    return push_core(data)

def push_texts(user_id: str, texts: str):
    messages = []
    for text in texts:
        messages.append({ 
            'type': 'text',
            'text': text
         })

    data = {
        'to': user_id,
        'messages': messages
    }
    return push_core(data)

def reply_text(reply_token, text):
    data = {
        'replyToken': reply_token,
        'messages': [{
            'type': 'text',
            'text': text
        }]
    }
    return reply_core(data)

def reply_text_quick_reply(reply_token: str, text: str, qr_actions):
    items = []
    for action in qr_actions:
        items.append(action.get_json())
    data = {
        'replyToken': reply_token,
        'messages': [{
            'type': 'text',
            'text': text,
            'quickReply': {
                'items': items
            }
        }]
    }
    return reply_core(data)

# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------
if __name__ == '__main__':
    pass