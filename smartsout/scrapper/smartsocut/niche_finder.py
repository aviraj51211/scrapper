# scrapper/smartscout/scraper.py
import traceback
import time
import os
import glob
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from .auth import get_authenticated_driver
from .bob_url import debug_blob_issue


def setup_download_directory(download_path: str = None):
    """Setup download directory and return path"""
    if download_path is None:
        # Create a downloads directory in the project
        download_path = os.path.join(os.path.dirname(__file__), "..", "downloads")
    
    os.makedirs(download_path, exist_ok=True)
    return download_path


def get_latest_downloaded_file(download_path: str, pattern: str = "*.csv"):
    """Get the most recently downloaded CSV file"""
    # Wait for download to complete
    time.sleep(5)
    
    files = glob.glob(os.path.join(download_path, pattern))
    if not files:
        return None
    
    # Get the most recent file
    latest_file = max(files, key=os.path.getctime)
    return latest_file


def send_csv_file(file_path: str, search_text: str):
    """
    Send the CSV file via email or other method.
    You'll need to implement this based on your needs.
    """
    try:
        # TODO: Implement your file sending logic here
        # Examples: Email, FTP, Cloud Storage, etc.
        
        # For now, just print file info
        file_size = os.path.getsize(file_path)
        print(f"📤 Sending file: {os.path.basename(file_path)}")
        print(f"   Size: {file_size} bytes")
        print(f"   Search term: {search_text}")
        
        # Example email sending (you'll need to install and configure)
        # send_email_with_attachment(file_path, search_text)
        
        return True
    except Exception as e:
        print(f"❌ Error sending file: {e}")
        return False


def cleanup_file(file_path: str):
    """Delete the downloaded file after sending"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ Cleaned up file: {os.path.basename(file_path)}")
            return True
    except Exception as e:
        print(f"❌ Error cleaning up file: {e}")
    return False

def run_niche_finder_export(
    search_text: str, 
    username: str, 
    password: str,
    download_path: str = None,
    send_file: bool = True,
    cleanup: bool = True
) -> dict:
    """
    Full workflow:
    1. Get authenticated browser
    2. Go to Niche Finder tab
    3. Apply subcategory filter
    4. Click export CSV
    5. Download file
    6. Send file (optional)
    7. Clean up (optional)
    """
    # Setup download directory
    download_path = setup_download_directory(download_path)
    
    # Configure Chrome to download to our directory
    driver = get_authenticated_driver(
        headless=False, 
        username=username, 
        password=password,
        download_dir=download_path  # You'll need to update auth.py to accept this
    )
    
    wait = WebDriverWait(driver, 25)
    downloaded_file = None

    try:
        # Step 1: Go to subcategories page
        print("Step 1: Loading page...")
        driver.get("https://app.smartscout.com/app/subcategories")
        time.sleep(10)
        
        # Step 2: Click 'Niche Finder' tab
        print("Step 2: Locating Niche Finder tab...")
        niche_tab = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[contains(@class, 'mat-tab-label-content') and contains(., 'Niche Finder')]")
            )
        )
        niche_tab.click()
        time.sleep(10)
        print("✓ Niche Finder tab clicked")
        
        # Step 3: Open Filters panel
        print("Step 3: Opening Filters panel...")
        filters_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Filters']]"))
        )
        filters_button.click()
        time.sleep(10)
        print("✓ Filters panel opened")
        
        # Step 4: Click "Subcategory" group header to expand it
        print("Step 4: Clicking 'Subcategory' filter group...")
        subcategory_header = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[.//span[text()='Subcategory'] and contains(@class, 'ag-group-title-bar')]")
            )
        )
        subcategory_header.click()
        time.sleep(10)
        print("✓ Subcategory filter expanded")
        
        # Step 5: Wait for input field to appear and type into it
        print("Step 5: Waiting for filter input field...")
        filter_input = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//input[contains(@class, 'ag-input-field-input') and @placeholder='Filter...']")
            )
        )
        
        print(f"✓ Found input field with id: {filter_input.get_attribute('id')}")
        
        # Clear the input
        filter_input.clear()
        time.sleep(1)
        
        # Type the search text
        filter_input.send_keys(search_text)
        print(f"✓ Typed into filter: '{search_text}'")
        time.sleep(3)
        
        # Step 6: Two-step export process
        print("Step 6: Triggering export and download...")
        
        # First: Click Excel side button
        print("  Clicking Excel side button...")
        excel_side_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(@class, 'ag-side-button-button') and .//img[contains(@src, 'excel')]]")
            )
        )
        excel_side_button.click()
        time.sleep(5)
        print("  ✓ Excel side button clicked")
        
        # Second: Click CSV image/icon
        print("  Clicking CSV export image...")
        csv_image = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//img[contains(@src, 'csv.ico') and @mattooltip='Export as CSV']")
            )
        )
        csv_image.click()
        debug_blob_issue(driver)
        # Wait longer for download to complete
        print("  Waiting for download to complete...")
        time.sleep(15)
        print("  ✓ Download initiated")
        
        # Get the downloaded file
        downloaded_file = get_latest_downloaded_file(download_path)
        if not downloaded_file:
            time.sleep(10)
            downloaded_file = get_latest_downloaded_file(download_path)
        if not downloaded_file:
            raise Exception("No CSV file was downloaded")
        
        print(f"✓ File downloaded: {os.path.basename(downloaded_file)}")
        
        result = {
            "status": "success",
            "message": f"Export completed for '{search_text}'",
            "file_path": downloaded_file,
            "file_name": os.path.basename(downloaded_file),
            "file_size": os.path.getsize(downloaded_file) if downloaded_file else 0
        }
        
        # Send the file if requested
        if send_file and downloaded_file:
            print("📤 Sending file...")
            send_success = send_csv_file(downloaded_file, search_text)
            result["sent"] = send_success
            result["sent_time"] = datetime.now().isoformat()
        
        # Clean up if requested
        if cleanup and downloaded_file:
            print("🧹 Cleaning up...")
            cleanup_success = cleanup_file(downloaded_file)
            result["cleaned_up"] = cleanup_success
            result["file_deleted"] = cleanup_success
        
        return result

    except Exception as e:
        error_msg = f"Scraping failed: {str(e)}"
        print(error_msg)
        print(f"Traceback:\n{traceback.format_exc()}")
        
        # Try to save screenshot for debugging
        try:
            screenshot_path = os.path.join(download_path, f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            driver.save_screenshot(screenshot_path)
            print(f"Saved screenshot: {screenshot_path}")
        except:
            pass
            
        raise Exception(error_msg) from e

    finally:
        driver.quit()