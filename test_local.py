import urllib.request

try:
    response = urllib.request.urlopen("http://localhost:8080/")
    html = response.read().decode('utf-8')
    print("HTML length:", len(html))
    print("Does it contain id=\"app\"?", 'id="app"' in html)
except Exception as e:
    print("Error:", e)
