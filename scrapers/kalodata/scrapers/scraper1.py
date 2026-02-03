"""
Kalodata Scraper - Click Category and Simple divs after login
"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def click_category_and_simple(driver, wait_timeout: int = 20, click_delay: float = 0.5):
    """
    Click the Category div and a Simple div on kalodata.
    
    Args:
        driver: Selenium WebDriver (assumed to be logged in)
        wait_timeout: Timeout in seconds for WebDriverWait
        click_delay: Delay in seconds between clicks
    
    Returns:
        dict with click results: {"category_clicked": bool, "simple_clicked": bool}
    """
    wait = WebDriverWait(driver, wait_timeout)
    results = {
        "category_clicked": False,
        "simple_clicked": False,
    }

    # Click an element whose text contains 'Category'
    try:
        cat = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[contains(text(),'Category') or contains(.,'Category')]")
            )
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", cat)
        time.sleep(10)
        driver.execute_script("arguments[0].click();", cat)
        results["category_clicked"] = True
        print("✅ Category div clicked")
        time.sleep(10)
    except Exception as e:
        print(f"⚠️ Could not click Category: {e}")

    # Click a div containing 'simple' (case-insensitive)
    try:
        simple = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//div[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'simple')]",
                )
            )
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", simple)
        time.sleep(click_delay)
        driver.execute_script("arguments[0].click();", simple)
        results["simple_clicked"] = True
        print("✅ Simple div clicked")
        time.sleep(click_delay)
    except Exception as e:
        print(f"⚠️ Could not click Simple: {e}")

    return results
