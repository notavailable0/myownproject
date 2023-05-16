import json
import random

import requests

words = open('testdata.txt', 'r').readlines()
for i in words:
    words.pop(words.index(i))
    words.append(i)

for w in words:
    w = str(w).split(":")
    print(w[0], w[1])
    url = "http://localhost:8000/add_user"
    query = json.dumps({"username":w[0]+str(random.randint(1,88)), "password":w[1][1:5], "name":"fuckingbastard"})
    #response = requests.post(url, data=query)
    #print(response.text)

url = "http://localhost:8000/add_user"
query = json.dumps({"username": "admin1", "password": "admin", "name":"strelka"})
response = requests.post(url, data=query)

if response.status_code == 200:
    print("Login successful!")
else:
    print("Login failed:", response.text)

r = requests.get("http://localhost:8000/all_users")
print(r.text)
r = requests.get("http://localhost:8000/all_words")
print(r.text)
r = requests.get("http://localhost:8000/words/as")
print(r.text)
r = requests.get("http://localhost:8000/users/as")
print(r.text)

import requests

url = 'http://example.com/api/endpoint'
data = ['as', 'of', 'and']

response = requests.delete("http://localhost:8000/delete_dictionary", json=data)
print(response.text)

