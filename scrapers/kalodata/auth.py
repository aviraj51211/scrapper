import time
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

try:
	import undetected_chromedriver as uc
	_HAS_UC = True
except Exception:
	from selenium import webdriver
	from selenium.webdriver.chrome.service import Service
	from selenium.webdriver.chrome.options import Options
	from webdriver_manager.chrome import ChromeDriverManager
	_HAS_UC = False


def _build_options_uc(headless: bool = False):
	opts = uc.ChromeOptions()
	if headless:
		opts.add_argument("--headless=new")
	opts.add_argument("--no-first-run")
	opts.add_argument("--disable-blink-features=AutomationControlled")
	opts.add_argument("--disable-gpu")
	opts.add_argument("--start-maximized")
	opts.add_experimental_option("excludeSwitches", ["enable-automation"])
	opts.add_experimental_option('useAutomationExtension', False)
	return opts


def _build_options_selenium(headless: bool = False):
	options = Options()
	if headless:
		options.add_argument("--headless")
	options.add_argument("--start-maximized")
	options.add_argument("--disable-blink-features=AutomationControlled")
	options.add_experimental_option("excludeSwitches", ["enable-automation"])
	options.add_experimental_option('useAutomationExtension', False)
	return options


def get_kalodata_driver(email: str, password: str, headless: bool = False, timeout: int = 30):
	"""Create a Chrome driver, perform login to kalodata and return the logged-in driver.

	The function prefers `undetected_chromedriver` if available, otherwise falls back
	to Selenium + webdriver_manager. On successful login the driver is returned and
	left running (caller is responsible for quitting it).
	"""
	if _HAS_UC:
		options = _build_options_uc(headless=headless)
		driver = uc.Chrome(options=options)
	else:
		options = _build_options_selenium(headless=headless)
		driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

	wait = WebDriverWait(driver, timeout)

	try:
		driver.get("https://www.kalodata.com/login")

		# Wait for the email input and fill credentials
		wait.until(EC.presence_of_element_located((By.ID, "register_email"))).send_keys(email)
		driver.find_element(By.ID, "register_password").send_keys(password)
		driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

		# Wait until URL changes away from /login or some known post-login element appears
		for _ in range(timeout):
			if "login" not in driver.current_url:
				break
			time.sleep(1)

		# Basic verification: ensure product page loads
		driver.get("https://www.kalodata.com/product")
		wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ant-table-row")))

		return driver

	except Exception:
		try:
			driver.quit()
		except Exception:
			pass
		raise
