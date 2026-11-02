import requests

def inspect_stream_endpoint(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://streamzline.xyz/"
    }
    
    try:
        print(sending request to: {url})
        response = requests.get(url, headers=headers, stream=True, timeout=10, allow_redirects=True)
        
        print(f"\n--- Response Details ---")
        print(f"Final URL: {response.url}")
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        
        print("\n--- Headers ---")
        for key, value in response.headers.items():
            print(f"{key}: {value}")
            
        # If the endpoint returns text/playlist data instead of raw binary video
        content_type = response.headers.get('Content-Type', '')
        if 'text' in content_type or 'application' in content_type:
            print("\n--- Content Preview ---")
            print(response.text[:1000])
            
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    target_url = "https://streamzline.xyz/live/Xp697Y4Kpu4l/DqNEfHKu2qsC/2071585.ts"
    inspect_stream_endpoint(target_url)
