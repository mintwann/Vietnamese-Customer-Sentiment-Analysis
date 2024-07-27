import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure Chrome options
options = Options()
options.headless = True  # Enable headless mode
options.add_argument("--window-size=1920,1200")  # Set the window size

# Initialize the Chrome driver with the specified options
driver = webdriver.Chrome(options=options)

# Navigate to the dienmayxanh website
url = "https://www.dienmayxanh.com/dien-thoai"
driver.get(url)
time.sleep(2)

# Find the div containing the brand links
brand_links_div = driver.find_element(By.CLASS_NAME, "lst-quickfilter.q-manu")

# Find all the link elements within the div
brand_links = brand_links_div.find_elements(By.TAG_NAME, "a")

# Extract and store the href attributes (links)
brand_list = []
for link in brand_links:
    href = link.get_attribute("href")
    brand_list.append(href)


# --- Scraping product links for each brand ---
product_links = {}  # Store product links for each brand

for brand_url in brand_list:
    driver.get(brand_url)
    time.sleep(2)
    
    # Find the "View all products" button
    try:
        btn_view_all_products = driver.find_element(By.XPATH, "//*[@id='categoryPage']/div[3]/div[2]")
        if "hide" not in btn_view_all_products.get_attribute("class"):
            btn_view_all_products.click()
        else:
            pass
    except NoSuchElementException:
        pass
    
    # Find the ul element containing product list items
    product_list_ul = driver.find_element(By.CLASS_NAME, "listproduct")

    # Find all product link elements within the ul
    product_link_elements = product_list_ul.find_elements(By.CLASS_NAME, "main-contain")
    
    # Extract the href attributes (product links) and store them in a list
    product_links[brand_url] = [link.get_attribute("href") for link in product_link_elements]
    

# --- Scrape product data and store in Excel ---
# Create an ExcelWriter object to write data to multiple sheets
excel_writer = pd.ExcelWriter("dienmayxanh_phone_data.xlsx", engine="xlsxwriter")

for brand_url, product_urls in product_links.items():
    all_product_data = []  # Store data for all products
    
    for product_url in product_urls:
        driver.get(product_url)
        time.sleep(3)
        
        # 1. Extract Product Name
        try:
            product_name = driver.find_element(By.CSS_SELECTOR, "h1").text.strip()
        except NoSuchElementException:
            product_name = "N/A"
            
        # 2. Extract Comments and Ratings
        comments_and_ratings = []

        try:
            # Find the "View all comments" button
            btn_view_all_comments = driver.find_element(By.CSS_SELECTOR, ".btn-view-all")
            btn_view_all_comments_url = btn_view_all_comments.get_attribute("href")
            driver.get(btn_view_all_comments_url)
        except NoSuchElementException:
            pass # If the button is not found, continue on the current page
        
        # Pagination handling
        current_page = 1  # Start from page 1
        while True:
            # Find comments on the current page
            try:
                comment_elements = driver.find_elements(By.CSS_SELECTOR, "ul.comment-list li.par")
                for i in range(len(comment_elements)):
                    try:
                        # Re-find the comment element BEFORE getting text or ratings
                        comment = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, f"//ul[@class='comment-list']/li[@class='par'][{i + 1}]"))
                        )
                        comment_text = WebDriverWait(comment, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".cmt-content .cmt-txt"))
                        ).text.strip()
                    except (TimeoutException, NoSuchElementException):
                        comment_text = "N/A"

                    try:
                        # Re-find the comment element BEFORE getting the rating stars
                        comment_for_rating = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, f"//ul[@class='comment-list']/li[@class='par'][{i + 1}]"))
                        )
                        rating_stars = WebDriverWait(comment_for_rating, 10).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".cmt-top-star .iconcmt-starbuy"))
                        )
                        # rating_stars = comment_for_rating.find_elements(By.CSS_SELECTOR, ".cmt-top-star .iconcmt-starbuy")
                        rating = len(rating_stars)
                    except (TimeoutException, NoSuchElementException):
                        rating = "N/A"

                    comments_and_ratings.append({"comment": comment_text, "rating": rating})

            except (TimeoutException, NoSuchElementException):
                comments_and_ratings = [{'comment': "N/A", 'rating': "N/A"}]
            
            # Find the next page link based on page number
            current_page += 1 
            next_page_link = f"//a[@href='javascript:ratingCmtList({current_page})']"
            
            try:
                next_page_button = driver.find_element(By.XPATH, next_page_link)
                next_page_button.click()
                
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "ul.comment-list li.par"))
                )                
                time.sleep(2)
                
            except (TimeoutException, NoSuchElementException):
                print(f"Next button not clickable or timeout on page {current_page}. Moving to next product.")
                break  # Break the loop if the next page button is not found
            
        product_data = {
            'product_url': product_url,
            "product_name": product_name,
        }
        
        # Iterate and add comments and ratings as separate columns
        for i, comment_data in enumerate(comments_and_ratings):
            product_data[f"comment_{i+1}"] = comment_data["comment"]
            product_data[f"rating_{i+1}"] = comment_data["rating"]
            
        all_product_data.append(product_data)
        
    # Create a DataFrame for the current brand's data
    df = pd.DataFrame(all_product_data)
    
    # Extract brand name from the URL
    brand_name = brand_url.split("/")[-1].replace("dien-thoai-", "")

    # Write the DataFrame to a sheet named after the brand
    df.to_excel(excel_writer, sheet_name=brand_name, index=False)

# Close the browser after ALL scraping is complete
driver.quit()
    
# Save the Excel file
excel_writer.close()
