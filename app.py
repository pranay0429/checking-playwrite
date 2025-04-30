from flask import Flask, jsonify
import asyncio
import nest_asyncio  # ADD THIS
from playwright.async_api import async_playwright

nest_asyncio.apply()  # PATCHES the loop

app = Flask(__name__)

async def scrape_data(playwright):
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36")
    page = await context.new_page()

    await page.set_viewport_size({"width": 1280, "height": 800})

    url = "https://www.glassdoor.co.in/Interview/Google-Project-Manager-Interview-Questions-EI_IE9079.0,6_KO7,22.htm"
    print("Navigating to page...")
    await page.goto(url, wait_until='load')
    print("Page loaded!")

    print("Waiting for the interview containers...")
    await page.wait_for_selector('[data-test^="Interview"][data-test$="Container"]', timeout=60000)
    print("Interviews found!")
    await page.mouse.wheel(0, 3000)  # scroll to trigger JS
    await page.wait_for_timeout(3000)

    company_cards = await page.locator('[data-test^="Interview"][data-test$="Container"]').all()

    results = []
    for card in company_cards:
        try:
            company_name = await card.locator(
                '.truncated-text_truncate__021Uu.interview-details_textStyle__gmhSJ'
            ).first.text_content(timeout=2000) or "N/A"

            results.append({"Company": company_name.strip()})
        except Exception as e:
            print("Error:", e)
    
    await browser.close()
    return results
@app.route("/scrape", methods=["GET"])
def scrape_route():
    try:
        data = asyncio.run(run_playwright())
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

async def run_playwright():
    async with async_playwright() as playwright:
        return await scrape_data(playwright)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
    # app.run(debug=True)
