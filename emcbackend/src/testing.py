import requests

# Base URL of the API
base_url = 'https://api.dbi-visual.eu'

# Test login endpoint
def test_login():
    url = f'{base_url}/login'
    data = {
        'login': 'your_username',
        'password': 'your_password'
    }
    response = requests.post(url, json=data)
    print(response.status_code)
    print(response.json())

# Test search endpoint
def test_search():
    url = f'{base_url}/search'
    params = {
        'word': 'your_search_word'
    }
    response = requests.get(url, params=params)
    print(response.status_code)
    print(response.json())

# Test view user data endpoint
def test_view_user_data():
    url = f'{base_url}/user-data'
    params = {
        'username': 'your_username'
    }
    response = requests.get(url, params=params)
    print(response.status_code)
    print(response.json())

# Test save word endpoint
def test_save_word():
    url = f'{base_url}/save-word'
    data = {
        'word': 'your_word_to_save'
    }
    response = requests.post(url, json=data)
    print(response.status_code)
    print(response.json())

# Test endpoints
test_login()
test_search()
test_view_user_data()
test_save_word()

