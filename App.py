import requests

url = "https://apitechsolutions.duckdns.org"


x = requests.get(url)
print(x.text)