import requests

url = "https://aerodatabox.p.rapidapi.com/flights/search/term"

querystring = {"q": "KL30"}

headers = {
    "x-rapidapi-key": "d6f0412555msh2fb6890010465b7p15be83jsnb7a1bfb94f64",
    "x-rapidapi-host": "aerodatabox.p.rapidapi.com",
    "Content-Type": "application/json",
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())
