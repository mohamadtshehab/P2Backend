from p2.settings import NGROK_URL
import requests

def format_flask_response_data(response):
    flask_response_data = response.json()
    
    image = flask_response_data.get('image', '')
    if not image:
        raise ValueError("Response did not contain a valid 'image'")

    return image

def handle_flask_image_post_request(request):
    image = request.FILES.get('image')
    flask_post_data = {'image': ('image.jpg', image)}
    try:
        response = requests.post(f'{NGROK_URL}/generate_from_image', files=flask_post_data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error communicating with Flask service: {str(e)}")
    return response

def handle_flask_text_post_request(request):
    prompt = request.data.get('prompt')
    flask_post_data = {
        'prompt': prompt
    }
    try:
        response = requests.post(f'{NGROK_URL}/generate_from_text', json=flask_post_data, verify=False)
        print(response)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error communicating with Flask service: {str(e)}")
    return response