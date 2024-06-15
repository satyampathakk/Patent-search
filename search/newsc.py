#!/bin/python3

from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import re

def scrape_patent_data(query):
    options = webdriver.ChromeOptions()
    #options.add_argument('--headless')  # Enable headless mode no gui chrome will work in background 

    # Set the path to your ChromeDriver executable (if not in PATH)
    # os.environ["PATH"] += ":/path/to/chromedriver"

    driver = webdriver.Chrome(options=options)

    driver.get(f"https://patents.google.com/?q=({query})&oq={query}")
    sleep(3.5)  # Adjust wait time as needed

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
        sleep(2.5)  # Adjust wait time as needed
        text = driver.find_elements(By.XPATH, '//*[@id="text"]/abstract/div')
        text_data+=f"patent no -{arr[i]} " 
        for t in text:
            text_data+=t.text +"\n\n\n\n"      
    return text_data

    driver.quit()
