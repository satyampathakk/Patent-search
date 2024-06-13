from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import re

def scrape_patent_data(query="watch"):
    driver = webdriver.Chrome()
    driver.get(f"https://patents.google.com/?q=({query})&oq={query}")
    sleep(10)

    elements = driver.find_elements(By.XPATH, '//*[@id="resultsContainer"]//span[contains(@data-proto, "OPEN_PATENT_PDF")]')
    arr = []

    with open("data.txt", "w", encoding="utf-8") as file:
        print("New data file is being created or previous one data cleared.")

    if not elements:
        print("No patent number elements found.")
    else:
        for span_element in elements:
            span_text = span_element.text
            arr.append(span_text)
        print(arr)

    for i in range(len(arr)):
        driver.get(f"https://patents.google.com/patent/{arr[i]}/en")
        sleep(10)
        text = driver.find_elements(By.XPATH, '//*[@id="text"]/abstract/div')

        with open("data.txt", "a+", encoding="utf-8") as file:
            for t in text:
                file.write(t.text)
                file.write("\n\n\n\n new line start here\n\n\n")

    driver.quit()

