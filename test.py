import requests

url = "http://172.16.101.252:5000/api/extract"

data = {
    "url": "https://news.cctv.com/2025/06/25/ARTIAEIpANSZQSsRXtCHUrgR250625.shtml?spm=C94212.P4YnMod9m2uD.ENPMkWvfnaiV.14",
    "options": {
        "browser": "chrome",
        "headless": True,
        "handle_pagination": True
    }
}

response = requests.post(url, json=data)
print(response.content.decode("utf-8"))
