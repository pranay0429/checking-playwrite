from flask import Flask, jsonify
import asyncio
import nest_asyncio  # ADD THIS
from playwright.async_api import async_playwright

nest_asyncio.apply()  # PATCHES the loop

app = Flask(__name__)

async def scrape_data(playwright):
    browser = await playwright.chromium.launch(headless=False)  # use headless=False for debugging
    page = await browser.new_page()

    url = "https://www.glassdoor.co.in/Interview/Google-Project-Manager-Interview-Questions-EI_IE9079.0,6_KO7,22_IP2.htm?filter.jobTitleFTS=Project+Manager"
    await page.goto(url)

    # Wait longer to ensure content loads
    await page.wait_for_timeout(5000)

    # Collect cards
    company_cards = await page.locator('[data-test^="Interview"][data-test$="Container"]').all()
    print(company_cards)
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
    app.run(debug=True)
