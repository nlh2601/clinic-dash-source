from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd  # <-- Added for spreadsheet export

# Set up the driver
driver = webdriver.Chrome()
driver.maximize_window()
wait = WebDriverWait(driver, 15)

# Step 1: Go to login page
driver.get("https://www.guidestar.org/Account/Login?returnUrl=https%3A%2F%2Fwww.guidestar.org%2F")

# Step 2: Enter email and password
wait.until(EC.presence_of_element_located((By.NAME, "EmailAddress"))).send_keys("85qsq@punkproof.com")
wait.until(EC.presence_of_element_located((By.NAME, "Password"))).send_keys("aSAIHS*!!YkS1231")

# Step 3: Click login
wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn-login-register"))).click()

# Step 4: Navigate to search page
wait.until(EC.url_contains("guidestar.org"))  # wait until we return to homepage
driver.get("https://www.guidestar.org/search")

# Step 5: Click on the state dropdown and select Hawaii
state_dropdown = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "chosen-choices")))
state_dropdown.click()

state_options = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".chosen-drop ul.chosen-results li")))
for option in state_options:
    if option.text.strip() == "Hawaii":
        option.click()
        break

print("State 'Hawaii' selected. Please manually complete any other filters, including organization tab stuff, then press Enter here to continue.")
input()  # Pause for manual filtering and tab selection

# Now start scraping with pagination
all_org_names = []
page_num = 1
while len(all_org_names) < 772:
    print(f"Scraping page {page_num}...")
    time.sleep(2)  # wait for results to load

    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "search-org-name")))
    org_elements = driver.find_elements(By.CLASS_NAME, "search-org-name")
    page_org_names = [org.text for org in org_elements]

    print("First 3 orgs this page:", page_org_names[:3])

    new_orgs_added = 0
    for name in page_org_names:
        if name not in all_org_names:
            all_org_names.append(name)
            new_orgs_added += 1

    print(f"Added {new_orgs_added} new orgs this page, total so far: {len(all_org_names)}")

    try:
        next_button = driver.find_element(By.CLASS_NAME, "next")
        if "disabled" in next_button.get_attribute("class"):
            print("Next button disabled. Reached last page.")
            break
        next_button.click()
    except Exception as e:
        print("No next button found or error:", e)
        break

    page_num += 1

print("\nAll scraped organization names:")
for i, org_name in enumerate(all_org_names, 1):
    print(f"{i}. {org_name}")

# Export to Excel
df = pd.DataFrame(all_org_names, columns=["Organization Name"])
df.to_excel("organizations.xlsx", index=False)
print("\nSaved to organizations.xlsx ✅")

# driver.quit()  # Uncomment to close browser when done
