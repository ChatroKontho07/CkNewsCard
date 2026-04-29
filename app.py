from flask import Flask, render_template, request, jsonify, send_file
import requests
from bs4 import BeautifulSoup
from io import BytesIO
from urllib.parse import quote

app = Flask(__name__)

# Route to serve the main HTML page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pro')
def indexpro():
    return render_template('indexpro.html')


@app.route('/do_pro')
def indexpro1():
    return render_template('indexpro1.html')

 
# Updated Fetch Route: Automatically wraps the image in a proxy URL
@app.route('/fetch-news', methods=['POST'])
def fetch_news():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({"success": False, "error": "No URL provided"})

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')

        # 1. Scrape Title (OG tag priority)
        og_title = soup.find("meta", property="og:title")
        title = og_title["content"] if og_title else (soup.title.string if soup.title else "No Title Found")

        # 2. Scrape Image (OG tag priority)
        og_image = soup.find("meta", property="og:image")
        image_url = og_image["content"] if og_image else ""

        # 3. Modify Image URL to use our Proxy
        # This allows your existing HTML to load the image without CORS issues
        if image_url:
            # We return a link to our own /proxy-image route
            proxied_image_url = f"/proxy-image?url={quote(image_url)}"
        else:
            proxied_image_url = ""

        return jsonify({
            "success": True,
            "title": title.strip(),
            "image": proxied_image_url
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# The Proxy Route: This does the heavy lifting for the canvas
@app.route('/proxy-image')
def proxy_image():
    target_url = request.args.get('url')
    if not target_url:
        return "URL is required", 400

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        img_response = requests.get(target_url, headers=headers, stream=True)
        img_response.raise_for_status()

        # Wrap the image content in a BytesIO object and send it back
        return send_file(
            BytesIO(img_response.content),
            mimetype=img_response.headers.get('Content-Type', 'image/jpeg')
        )
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    # Ensure your project folder has 'templates' for index.html 
    # and 'static' for logo.png
    app.run(debug=True, port=5000)


