import argparse
import imaplib
import os
import sys
import time
import uuid

from bioblend import galaxy

import tenacity

# Generated by Selenium IDE
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


class SeleniumCustomWait(object):
    """
    Example usage:

    with SeleniumCustomWait(driver, 0):
        driver.find_element(By.ID, 'element-that-might-not-be-there')
    """

    def __init__(self, driver, new_wait=0):
        self.driver = driver
        self.original_wait = driver.timeouts.implicit_wait
        self.new_wait = new_wait

    def __enter__(self):
        self.driver.implicitly_wait(self.new_wait)

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.driver.implicitly_wait(self.original_wait)


class RegistrationEmailVerifier(object):
    def __init__(
        self,
        server,
        username,
        password,
        email,
        imap_server,
        imap_port,
        imap_username,
        imap_password,
        api_key,
    ):
        self.run_id = uuid.uuid4()
        self.server = server
        self.username = username
        self.password = password
        self.email = email
        self.imap_username = imap_username
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.imap_password = imap_password
        self.api_key = api_key
        self.timings = {}

        """Start web driver"""
        chrome_options = webdriver.ChromeOptions()
        if os.environ.get("SELENIUM_HEADLESS"):
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(180)
        self.wait = WebDriverWait(self.driver, 180)

    def find_login_button(self):
        with SeleniumCustomWait(self.driver, 0):
            try:
                return self.driver.find_element(By.NAME, "login")
            except NoSuchElementException:
                return None

    def find_sign_in_with_email(self):
        with SeleniumCustomWait(self.driver, 0):
            try:
                return self.driver.find_element(
                    By.XPATH, "//a[contains(., 'Sign in with email')]"
                )
            except NoSuchElementException:
                return None

    def is_able_to_login(self, driver):
        if self.find_login_button():
            return True
        elif self.find_sign_in_with_email():
            return True
        else:
            return False

    def load_galaxy_login(self):
        # Open Galaxy window
        self.driver.get(f"{self.server}/login")
        # Wait for username entry to appear
        self.wait.until(self.is_able_to_login)

    def login_to_galaxy_homepage(self):
        elem = self.find_sign_in_with_email()
        # if sign in with email is available, this is galaxy-au's customised page.
        if elem:
            elem.click()
        # Click username textbox
        self.driver.find_element(By.NAME, "login").click()
        # Type in username
        self.driver.find_element(By.NAME, "login").send_keys(self.username)
        # Type in password
        self.driver.find_element(By.NAME, "password").send_keys(self.password)
        # Submit login form
        self.driver.find_element(By.NAME, "password").send_keys(Keys.ENTER)
        # Wait for tool search box to appear
        self.wait.until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, "//input[@placeholder='search tools']")
            )
        )

    def register_new_account_for_user(self, email, password, public_name):
        self.driver.find_element(By.NAME, "email").click()
        self.driver.find_element(By.NAME, "email").send_keys(email)
        self.driver.find_element(By.NAME, "password").send_keys(password)
        self.driver.find_element(By.NAME, "confirm").send_keys(password)
        self.driver.find_element(By.NAME, "username").send_keys(public_name)
        self.driver.find_element(By.NAME, "username").send_keys(Keys.ENTER)

    def toggle_registration_page(self):
        self.driver.find_element(By.ID, "register-toggle").click()
        self.wait.until(
            expected_conditions.presence_of_element_located((By.NAME, "email"))
        )

    def register_new_account(self):
        self.toggle_registration_page()
        self.register_new_account_for_user(
            email=self.email, password=self.password, public_name=self.username
        )

    def delete_test_account(self):
        gi = galaxy.GalaxyInstance(url=self.server, key=self.api_key)
        user = gi.users.get_users(f_name=self.username)[0]
        if user["email"] == self.email:
            gi.users.delete_user(user["id"])
            gi.users.delete_user(user["id"], purge=True)

    @tenacity.retry(
        retry=tenacity.retry_if_result(lambda result: not result),
        wait=tenacity.wait_fixed(int(os.environ.get("IMAP_POLL_SECONDS", 10))),
        stop=tenacity.stop_after_attempt(
            int(os.environ.get("IMAP_MAX_POLL_ATTEMPTS", 12))
        ),
        retry_error_callback=(lambda _: False),
    )
    def verify_email_received(self):
        imap_server = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
        imap_server.login(self.imap_username, self.imap_password)

        try:
            # Select the inbox folder
            imap_server.select("inbox")

            # Search for messages that match the specified criteria
            criteria = f'TO "{self.email}" SUBJECT "Galaxy Account Activation"'
            _, message_ids = imap_server.search(None, criteria)
            return bool(message_ids[0])
        finally:
            # Close the IMAP connection
            imap_server.close()
            imap_server.logout()

    def run_test_sequence(self):
        self.load_galaxy_login()
        self.register_new_account()
        start = time.time()
        verified = self.verify_email_received()
        elapsed = time.time() - start
        if self.api_key:
            self.delete_test_account()
        return verified, elapsed

    def time_registration_email(self):
        self.timings = {}
        try:
            verified, elapsed = self.run_test_sequence()
            result = "success" if verified else "failure"
            print(
                f"email_verification,server={self.server},email={self.email},status={result} result={elapsed} {time.time_ns()}"
            )
            print("")
        finally:
            self.driver.quit()


def from_env_or_required(key):
    return {"default": os.environ[key]} if os.environ.get(key) else {"required": True}


def create_parser():
    parser = argparse.ArgumentParser(
        description="Register a user, and check whether a registration email is received."
    )
    parser.add_argument(
        "-s",
        "--server",
        default=os.environ.get("GALAXY_SERVER") or "https://usegalaxy.org.au",
        help="Galaxy server url",
    )
    parser.add_argument(
        "-e",
        "--email",
        **from_env_or_required("GALAXY_EMAIL"),
        help="Email address to use when registering the user (or set GALAXY_EMAIL env var)",
    )
    parser.add_argument(
        "-u",
        "--username",
        **from_env_or_required("GALAXY_USERNAME"),
        help="Username to use when registering the user (or set GALAXY_USERNAME env var)",
    )
    parser.add_argument(
        "-p",
        "--password",
        **from_env_or_required("GALAXY_PASSWORD"),
        help="Password to use when registering the user (or set GALAXY_PASSWORD env var)",
    )
    parser.add_argument(
        "-i",
        "--imap_server",
        **from_env_or_required("IMAP_SERVER"),
        help="IMAP server to use when checking for receipt of email (or set IMAP_SERVER env var)",
    )
    parser.add_argument(
        "-o",
        "--imap_port",
        **from_env_or_required("IMAP_PORT"),
        help="IMAP port to use when checking for receipt of email (or set IMAP_PORT env var)",
    )
    parser.add_argument(
        "-m",
        "--imap_username",
        **from_env_or_required("IMAP_USERNAME"),
        help="IMAP username to use when checking for receipt of email (or set IMAP_USERNAME env var)",
    )
    parser.add_argument(
        "-a",
        "--imap_password",
        **from_env_or_required("IMAP_PASSWORD"),
        help="IMAP password to use when checking for receipt of email (or set IMAP_PASSWORD env var)",
    )
    parser.add_argument(
        "-k",
        "--api_key",
        default=os.environ.get("GALAXY_API_KEY"),
        help="Galaxy API key. If specified, the created user will be deleted at the end of the test run",
    )
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    reg_email_verifier = RegistrationEmailVerifier(
        args.server,
        args.username,
        args.password,
        args.email,
        args.imap_server,
        args.imap_port,
        args.imap_username,
        args.imap_password,
        args.api_key,
    )
    reg_email_verifier.time_registration_email()
    return 0


if __name__ == "__main__":
    sys.exit(main())
