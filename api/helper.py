from p2.settings import TEXT_NGROK_URL
import requests

def format_flask_response_data(response):
    flask_response_data = response.json()
    image = flask_response_data.get('image', '')
    if not image:
        raise ValueError("Response did not contain a valid 'image'")
    return image

def handle_flask_text_post_request(request):
    prompt = request.data.get('prompt')
    flask_post_data = {
        'prompt': prompt
    }
    try:
        response = requests.post(f'{TEXT_NGROK_URL}/generate_from_text', json=flask_post_data, verify=False)
        print(response)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error communicating with Flask service: {str(e)}")
    return response