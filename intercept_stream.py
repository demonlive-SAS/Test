import asyncio
from playwright.async_api import async_playwright

async def intercept_streams(url):
    async with async_playwright() as p:
        # Launch browser (set headless=False if you want to see the browser window)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Listen to all network requests and filter for streaming extensions/keywords
        page.on("request", lambda request: print(f"[FOUND] {request.url}") 
                if any(ext in request.url for ext in [".m3u8", ".ts", "m3u", "playlist"]) else None)
        
        print(f"Navigating to: {url}")
        try:
            await page.goto(url, timeout=60000)
            print("Listening for stream chunks... (Press Ctrl+C to stop)")
            # Keep the script running to capture continuous live stream requests
            await asyncio.sleep(30)
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    target_url = "https://streamzline.xyz/live/Xp697Y4Kpu4l/DqNEfHKu2qsC/2071585.ts"
    asyncio.run(intercept_streams(target_url))
