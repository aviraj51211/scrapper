# scrapper/smartscout/scraper2.py
import traceback
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from auth import get_authenticated_driver

def run_rank_maker_search(asin: str, username: str, password: str) -> dict:
    """
    Full workflow for Rank Maker tool:
    1. Get authenticated browser
    2. Navigate to home
    3. Open 'Keyword Tools' menu (active state)
    4. Click on 'Rank Maker' submenu item
    5. Input the provided ASIN and search
    Returns the status of the operation.
    """
    # Use headless=False initially to see and debug the process
    driver = get_authenticated_driver(headless=False, username=username, password=password)
    wait = WebDriverWait(driver, 20)  # Wait up to 20 seconds for elements

    try:
        # Step 1: Already authenticated and on home page via auth.py
        print("Step 1: On Home Page - " + driver.current_url)
        time.sleep(3) # Let the page settle
        
        div_with_svg = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'menu-item-container-active') and .//path[@fill='#6227CE']]"))
        )
        print("we had find it")
        div_with_svg.click()
        


    except Exception as e:
        error_msg = f"Rank Maker workflow failed: {str(e)}"
        print(error_msg)
        print(f"Traceback:\n{traceback.format_exc()}")
        
        # Take error screenshot
        try:
            error_screenshot = f"rank_maker_error_{time.strftime('%Y%m%d_%H%M%S')}.png"
            driver.save_screenshot(error_screenshot)
            print(f"Saved error screenshot: {error_screenshot}")
        except:
            pass
            
        raise Exception(error_msg) from e

    finally:
        # Comment out during debugging
        # driver.quit()
        print("\nWorkflow complete. Browser remains open for inspection.")

# Test the function with your credentials
if __name__ == "__main__":
    result = run_rank_maker_search("B07VPWR7YY", "dev@wangoes.com", "Wangoes@123#")
    print("\n" + "="*50)
    print("FINAL RESULT:")
    print(result)