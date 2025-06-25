import requests

url = "http://172.16.100.56:5000/crawl"

headers = { "Content-Type: application/json" }

data = {
    "url": "https://news.baidu.com",
    "wait_time": 30
}

response = requests.post(url, headers=headers, json=data)
print(response.text)

# curl -X POST http://172.16.100.56:5000/crawl \
#   -H "Content-Type: application/json" \
#   -d '{"url":"https://news.baidu.com", "wait_time":30}'