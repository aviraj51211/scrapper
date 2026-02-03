import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys

email = "dev@wangoes.com"
password = "Wangoes@123#"


def safe_js_click(driver, element):
    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});", element
    )
    time.sleep(0.25)
    driver.execute_script("arguments[0].click();", element)


def select_from_ant_dropdown(wait, driver):
    dropdown = wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "(//div[contains(@class,'ant-dropdown')])[last()]")
        )
    )

    options = dropdown.find_elements(By.CLASS_NAME, "ant-dropdown-menu-item")

    if not options:
        print("⚠ No options found, skipping dropdown.")
        driver.find_element(By.TAG_NAME, "body").click()
        return

    print("\nAvailable options:")
    print("0. Skip this dropdown")
    for i, opt in enumerate(options, start=1):
        print(f"{i}. {opt.text.strip()}")

    while True:
        user_input = input("Choose option number: ").strip()

        if user_input == "0":
            driver.find_element(By.TAG_NAME, "body").click()
            print("⏭ Skipped")
            return

        if not user_input.isdigit():
            print("❌ Enter a valid number")
            continue

        choice = int(user_input)
        if not (1 <= choice <= len(options)):
            print(f"❌ Choose between 1 and {len(options)}")
            continue

        break

    safe_js_click(driver, options[choice - 1])
    print(f"✅ Selected: {options[choice - 1].text.strip()}")


def login_kalodata():
    options = uc.ChromeOptions()
    options.add_argument("--no-first-run")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-web-resources")

    print("Initializing undetected-chromedriver...")
    sys.stdout.flush()
    
    try:
        driver = uc.Chrome(options=options, version_main=144)
        print("✅ Driver initialized successfully!")
        sys.stdout.flush()
        driver.maximize_window()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Retrying with default settings...")
        sys.stdout.flush()
        driver = uc.Chrome(options=options)
        driver.maximize_window()

    wait = WebDriverWait(driver, 30)

    try:
        print("Opening login page...")
        driver.get("https://www.kalodata.com/login")

        wait.until(EC.presence_of_element_located((By.ID, "register_email"))).send_keys(email)
        driver.find_element(By.ID, "register_password").send_keys(password)
        safe_js_click(driver, driver.find_element(By.CSS_SELECTOR, "button[type='submit']"))

        print("Waiting for login redirect...")
        for _ in range(30):
            if "login" not in driver.current_url:
                break
            time.sleep(1)

        print("Opening product page...")
        driver.get("https://www.kalodata.com/product")

        # ----- Date -----
        safe_js_click(driver, wait.until(EC.presence_of_element_located((By.ID, "Dates_guild"))))
        time.sleep(0.5)
        for el in driver.find_elements(By.XPATH, "//*[contains(text(),'Last 7 Days')]"):
            if el.is_displayed():
                safe_js_click(driver, el)
                break

        # ----- Category -----
        safe_js_click(driver, wait.until(EC.presence_of_element_located((By.ID, "Category_guild"))))
        safe_js_click(driver, wait.until(EC.presence_of_element_located((
            By.XPATH, "//li[@title='Health']//span[contains(@class,'ant-cascader-checkbox')]"
        ))))
        safe_js_click(driver, wait.until(EC.presence_of_element_located((
            By.XPATH, "//div[contains(text(),'Apply')]"
        ))))

        time.sleep(1)

        # ----- Revenue -----
        for el in driver.find_elements(By.XPATH, "//*[contains(text(),'Revenue')]"):
            if el.is_displayed():
                safe_js_click(driver, el)
                break
        select_from_ant_dropdown(wait, driver)

        # ----- Item Sold -----
        for el in driver.find_elements(By.XPATH, "//*[contains(text(),'Item Sold')]"):
            if el.is_displayed():
                safe_js_click(driver, el)
                break
        select_from_ant_dropdown(wait, driver)

        # ----- Revenue Growth Rate -----
        for el in driver.find_elements(By.XPATH, "//*[contains(text(),'Revenue Growth Rate')]"):
            if el.is_displayed():
                safe_js_click(driver, el)
                break
        select_from_ant_dropdown(wait, driver)

        # ----- Submit -----
        try:
            safe_js_click(driver, wait.until(EC.presence_of_element_located((By.ID, "submit-btn-guild"))))
        except:
            print("⚠ Submit button not found")

        # ----- Scrape -----
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ant-table-row")))
        rows = driver.find_elements(By.CLASS_NAME, "ant-table-row")

        print(f"\nFound {len(rows)} rows:\n")
        for i, row in enumerate(rows, start=1):
            cells = row.find_elements(By.TAG_NAME, "td")
            print(f"Row {i}: {[c.text.replace(chr(10), ' ') for c in cells]}")

        input("\nPress ENTER to close browser...")

    except Exception as e:
        print("\nERROR:", e)
        print("URL:", driver.current_url)

    finally:
        try:
            driver.quit()
        except:
            pass


if __name__ == "__main__":
    login_kalodata()