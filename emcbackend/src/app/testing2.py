import requests

BASE_URL = 'http://0.0.0.0:8000'  # Replace with the base URL of your API


# Test the create_deepl_key endpoint
def test_create_deepl_key():
    endpoint = '/deepl_keys?key=ffffff'
    key_data = {
        "key": "fucking key the fuck"
    }

    response = requests.post(BASE_URL + endpoint, json=key_data)
    print("Create Deepl Key Response:")
    print(response.status_code)
    print(response.json())


# Test the read_deepl_key endpoint
def test_read_deepl_key():
    key_id = 1  # Replace with the key ID you want to test

    endpoint = f'/deepl_keys/{key_id}'
    response = requests.get(BASE_URL + endpoint)
    print("Read Deepl Key Response:")
    print(response.status_code)
    print(response.json())


# Test the update_deepl_key endpoint
def test_update_deepl_key():
    key_id = 1  # Replace with the key ID you want to test

    endpoint = f'/deepl_keys/{key_id}'
    updated_key_data = {
        "key": "updated_key",
        "accessible": True
    }

    response = requests.put(BASE_URL + endpoint, json=updated_key_data)
    print("Update Deepl Key Response:")
    print(response.status_code)
    print(response.json())


# Test the delete_deepl_key endpoint
def test_delete_deepl_key():
    key_id = 1  # Replace with the key ID you want to test

    endpoint = f'/deepl_keys/{key_id}'
    response = requests.delete(BASE_URL + endpoint)
    print("Delete Deepl Key Response:")
    print(response.status_code)
    print(response.json())


# Test the get_all_deepl_keys endpoint
def test_get_all_deepl_keys():
    endpoint = '/deepl_keys/'
    response = requests.get(BASE_URL + endpoint)
    print("Get All Deepl Keys Response:")
    print(response.status_code)
    print(response.json())


if __name__ == "__main__":
    test_create_deepl_key()
    test_read_deepl_key()
    test_update_deepl_key()
    test_delete_deepl_key()
    test_get_all_deepl_keys()
