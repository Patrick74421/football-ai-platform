import requests

url = "https://inside.fifa.com/api/data-centre/matches?gender=1&year=2022&language=en&count=45"

headers = {

        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://inside.fifa.com/data-centre/matches/men?year=2022",
}

response = requests.get(url, headers = headers)

print("Status Code:", response.status_code)

if response.status_code == 200:
    print("Success!")
    data = response.json()
    print(data[0])
else:
    print("Request fail")
    print("Response:", response.text)

