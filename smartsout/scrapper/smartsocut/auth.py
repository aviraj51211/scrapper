# scrapper/smartscout/auth.py
import os
import pickle
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Where to save cookies
COOKIES_PATH = Path("data/smartscout_cookies.pkl")

def get_chrome_driver(headless=True, download_dir=None):
    """Create a Chrome driver instance with download support."""
    options = Options()
    
    # CRITICAL: Disable headless for visible debugging
    headless = False  # Force visible browser
    
    if headless:
        options.add_argument("--headless")
    
    if download_dir:
        # Ensure download directory exists
        os.makedirs(download_dir, exist_ok=True)
        
        # COMPLETE DOWNLOAD PREFERENCES - THIS IS THE KEY FIX
        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,  # Don't show save dialog
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "safebrowsing.disable_download_protection": True,  # Allow "dangerous" files
            "plugins.always_open_pdf_externally": True,
            "profile.default_content_settings.popups": 0,
            "profile.default_content_setting_values.automatic_downloads": 1,  # Allow auto downloads
            "credentials_enable_service": False,  # Disable password saving popup
            "profile.password_manager_enabled": False,
            "download.extensions_to_open": "",  # Don't open files, download them
            "download_restrictions": 0,  # No restrictions
        }
        options.add_experimental_option("prefs", prefs)
        
        # Additional arguments for download support
        options.add_argument("--disable-features=DownloadBubble")  # Disable new download UI
        options.add_argument("--disable-features=DownloadBubbleV2")
        options.add_argument("--disable-browser-side-navigation")
    
    # Common Chrome options - IMPORTANT FOR DOWNLOADS
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")  # Start maximized
    
    # Disable automation flags that might block downloads
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option("useAutomationExtension", False)
    
    # Set user agent to look like a real user
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), 
        options=options
    )
def login_and_save_cookies(driver, username, password):
    """Perform fresh login and save cookies for next time."""
    wait = WebDriverWait(driver, 20)
    driver.get("https://app.smartscout.com/sessions/signin")
    
    # Wait for login page to load
    wait.until(EC.presence_of_element_located((By.ID, "username")))
    
    # Fill login form
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    
    # Wait until redirected to home
    wait.until(EC.url_contains("/app/home"))
    
    # Save cookies
    COOKIES_PATH.parent.mkdir(exist_ok=True)
    pickle.dump(driver.get_cookies(), open(COOKIES_PATH, "wb"))

def get_authenticated_driver(headless=False, username=None, password=None, download_dir=None):
    """
    Return a driver that is already logged in.
    Tries to reuse cookies; falls back to login if needed.
    """
    # Create driver with download support
    driver = get_chrome_driver(headless=headless, download_dir=download_dir)
    
    # First, try to go to home page and check if we're logged in
    driver.get("https://app.smartscout.com/app/home")
    
    # Try to restore session from cookies if they exist
    cookies_restored = False
    if COOKIES_PATH.exists():
        try:
            cookies = pickle.load(open(COOKIES_PATH, "rb"))
            
            # Need to be on the domain before adding cookies
            driver.get("https://app.smartscout.com")
            for cookie in cookies:
                # Handle cookie format
                if 'sameSite' in cookie and cookie['sameSite'] not in ['Strict', 'Lax', 'None']:
                    cookie['sameSite'] = 'Lax'
                driver.add_cookie(cookie)
            
            # Refresh to apply cookies
            driver.get("https://app.smartscout.com/app/home")
            
            # Check if we're actually logged in
            wait = WebDriverWait(driver, 10)
            try:
                # Look for a sign of being logged in (like user menu or dashboard)
                wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//*[contains(text(), 'Dashboard') or contains(text(), 'Home') or @data-testid='user-menu']")
                ))
                cookies_restored = True
                print("✅ Reused existing session (no login needed)")
            except:
                print("⚠️ Cookies loaded but not logged in")
                cookies_restored = False
                
        except Exception as e:
            print(f"⚠️ Cookie restore failed: {e}")
            cookies_restored = False
    
    # If cookies didn't work or don't exist, do fresh login
    if not cookies_restored:
        if not username or not password:
            raise ValueError("Username and password required for fresh login")
        
        print("🔑 Performing fresh login...")
        login_and_save_cookies(driver, username, password)
    
    return driver