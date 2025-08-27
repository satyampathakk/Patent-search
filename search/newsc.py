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

def scrape_patent_data(query):
    # === Chrome options ===
    options = Options()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    service = Service()
    driver = webdriver.Chrome(service=service, options=options)

    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
    })

    # === Open Google Patents ===
    driver.get(f"https://patents.google.com/?q=({query})&oq={query}")
    
    # === Random scrolling & mouse movement AFTER driver is defined ===
    actions = ActionChains(driver)
    actions.move_by_offset(random.randint(0,100), random.randint(0,100)).perform()
    time.sleep(random.uniform(1,3))

    # Wait until results load
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "resultsContainer"))
        )
    except:
        print("Results did not load or Google blocked the request")
        driver.quit()
        return ""
    sleep(6)  
    elements = driver.find_elements(By.XPATH, '//*[@id="resultsContainer"]//span[contains(@data-proto, "OPEN_PATENT_PDF")]')
    arr = []

    text_data=""

    if not elements:
        print("No patent number elements found.")
    else:
        for span_element in elements:
            span_text = span_element.text
            arr.append(span_text)
        print(arr)
    for i in range(len(arr)):
        driver.get(f"https://patents.google.com/patent/{arr[i]}/en")
        sleep(6)  # Adjust wait time as needed
        text = driver.find_elements(By.XPATH, '//*[@id="text"]/abstract/div')
        text_data+=f"patent no -{arr[i]} " 
        for t in text:
            text_data+=t.text +"\n\n\n\n"      
    
    driver.quit()
    return text_data
