from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from time import sleep
import random
import logging

logger = logging.getLogger(__name__)

def scrape_patent_data(query):
    logger.info(f"  🌐 Starting patent scrape for: {query}")
    start_time = time.time()
    
    # === Chrome options (OPTIMIZED) ===
    options = Options()
    options.add_argument("--headless")  # Run in background (faster!)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.page_load_strategy = 'eager'  # Don't wait for all resources

    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(30)  # 30 second timeout

    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
    })

    try:
        # === Open Google Patents ===
        logger.info(f"  📡 Loading Google Patents search page...")
        driver.get(f"https://patents.google.com/?q=({query})&oq={query}")
        
        # === Minimal delay ===
        time.sleep(random.uniform(0.5, 1.5))  # Reduced from 1-3 seconds

        # Wait until results load
        logger.info(f"  ⏳ Waiting for results to load...")
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "resultsContainer"))
            )
            logger.info(f"  ✅ Results container loaded")
        except:
            logger.error("  ❌ Results did not load or Google blocked the request")
            driver.quit()
            return ""
        
        sleep(2)  # Reduced from 6 seconds
        
        logger.info(f"  🔍 Finding patent numbers...")
        elements = driver.find_elements(By.XPATH, '//*[@id="resultsContainer"]//span[contains(@data-proto, "OPEN_PATENT_PDF")]')
        arr = []

        text_data = ""

        if not elements:
            logger.warning("  ⚠️  No patent number elements found")
        else:
            for span_element in elements:
                span_text = span_element.text
                arr.append(span_text)
            logger.info(f"  ✅ Found {len(arr)} patents: {arr}")
        
        # Limit to first 5 patents for speed
        arr = arr[:5]
        logger.info(f"  📄 Scraping details for {len(arr)} patents...")
        
        for i, patent_id in enumerate(arr):
            logger.info(f"  📄 Scraping patent {i+1}/{len(arr)}: {patent_id}")
            driver.get(f"https://patents.google.com/patent/{patent_id}/en")
            sleep(2)  # Reduced from 6 seconds
            
            text = driver.find_elements(By.XPATH, '//*[@id="text"]/abstract/div')
            text_data += f"Patent ID: {patent_id}\n"
            
            for t in text:
                text_data += t.text + "\n\n"
            
            logger.info(f"  ✅ Patent {i+1}/{len(arr)} scraped")
        
        elapsed = time.time() - start_time
        logger.info(f"  🎉 Scraping completed in {elapsed:.2f}s")
        
    except Exception as e:
        logger.error(f"  ❌ Scraping error: {str(e)}")
        text_data = ""
    finally:
        driver.quit()
        logger.info(f"  🔒 Browser closed")
    
    return text_data

