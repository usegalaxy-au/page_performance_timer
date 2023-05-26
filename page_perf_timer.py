import argparse
import functools
import os
import sys
import time
import uuid

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


class EndStepReached(Exception):
    """
    Raised when a specific action step has been reached
    """

    pass


def clock_action(action_name):
    """
    Decorator to measure time taken to perform
    a function. The timing is stored in the wrapped
    object, assumed to be first args to wrapped function.
    :return:
    """

    def wrap(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            obj = args[0]
            start = time.time()
            retval = func(*args, **kwargs)
            elapsed = time.time() - start
            obj.timings[action_name] = {
                "elapsed": elapsed,
                # unix time
                "timestamp": time.time_ns(),
            }
            if obj.end_step == action_name:
                raise EndStepReached(action_name)
            return retval

        return wrapper

    return wrap


class PagePerfTimer(object):
    def __init__(
        self, server, username, password, end_step=None, run_id=None, workflow_name=None
    ):
        self.run_id = run_id or uuid.uuid4()
        self.server = server
        self.username = username
        self.password = password
        self.end_step = end_step
        self.workflow_name = workflow_name
        self.timings = {}

        """Start web driver"""
        chrome_options = webdriver.ChromeOptions()
        if os.environ.get("SELENIUM_HEADLESS"):
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(options=chrome_options)
        # self.driver = webdriver.Firefox()
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

    @clock_action("login_page_load")
    def load_galaxy_login(self):
        # Open Galaxy window
        self.driver.get(f"{self.server}/login")
        # Wait for username entry to appear
        self.wait.until(self.is_able_to_login)

    @clock_action("home_page_load")
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
        # Wait for tool panel to load
        self.wait.until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, "//div[@class='tool-panel-section']//a[@class='title-link' and contains(., 'Get Data')]")
            )
        )

    @clock_action("tool_search_load")
    def search_for_tool(self):
        # Select tool search box
        tool_search = self.driver.find_element(
            By.XPATH, "//input[@placeholder='search tools']"
        )
        tool_search.click()
        # Search for BWA
        tool_search.send_keys("bwa")
        # Wait for BWA tool to appear
        self.wait.until(
            expected_conditions.presence_of_element_located(
                (
                    By.XPATH,
                    "//a[starts-with(@href, '/tool_runner?tool_id=toolshed.g2.bx.psu.edu%2Frepos%2Fdevteam%2Fbwa%2Fbwa%2F0.7')]",
                )
            )
        )

    @clock_action("tool_form_load")
    def load_tool_form(self):
        # Select BWA tool
        bwa_tool = self.driver.find_element(
            By.XPATH,
            "//a[starts-with(@href,'/tool_runner?tool_id=toolshed.g2.bx.psu.edu%2Frepos%2Fdevteam%2Fbwa%2Fbwa%2F0.7')]",
        )
        bwa_tool.click()
        # Wait for tool form to load and execute button to appear
        self.wait.until(
            expected_conditions.presence_of_element_located((By.ID, "execute"))
        )

    @clock_action("shared_histories_page_load")
    def load_shared_histories(self):
        # Request history page
        self.driver.get(f"{self.server}/histories/list_shared")

        # Wait for history page to load
        self.wait.until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, "//h2[contains(., 'Histories shared with you by others')]")
            )
        )

    @clock_action("import_shared_history")
    def import_shared_history(self):
        # Select relevant history
        import_history_btn = self.driver.find_element(
            By.XPATH,
            f"//tbody[@id='grid-table-body']//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{self.workflow_name.lower()}_input_data')]",
        )
        import_history_btn.click()

        # View history details
        view_history_menu_item = self.driver.find_element(
            By.XPATH,
            f"//div[@id='{import_history_btn.get_attribute('id')}-menu']//a[contains(., 'View')]",
        )
        view_history_menu_item.click()
        self.wait.until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, f"//h3[contains(., '{self.workflow_name.lower()}_input_data')]")
            )
        )
        # Invoke copy history dialogue
        import_history_btn = self.driver.find_element(
            By.XPATH,
            f"//button[@title='Import this history' and contains(., 'Import this history')]",
        )
        import_history_btn.click()

        # Set new history name
        history_name_box = self.driver.find_element(By.ID, "copy-modal-title")
        history_name_box.clear()
        history_name_box.send_keys(f"{self.workflow_name}_Input_data_{self.run_id}")
        self.driver.find_element(
            By.XPATH,
            f"//button[contains(., 'Copy History')]",
        ).click()
        # Wait for history panel to load with new history
        self.wait.until(
            expected_conditions.presence_of_element_located(
                (
                    By.XPATH,
                    f"//div[@id='current-history-panel']//h3[contains(., '{self.workflow_name}_Input_data')]",
                )
            )
        )

    @clock_action("workflow_list_page")
    def load_workflow_list(self):
        # Request workflows list page
        self.driver.get(f"{self.server}/workflows/list")
        # Wait for workflow page to load and import button to appear
        self.wait.until(
            expected_conditions.presence_of_element_located((By.ID, "workflow-import"))
        )

    @clock_action("workflow_run_page")
    def load_workflow_run_form(self):
        # Select relevant workflow
        run_workflow_btn = self.driver.find_element(
            By.XPATH,
            f"//table[@id='workflow-table']//tr[contains(., '{self.workflow_name}')]//button[@title='Run workflow']",
        )
        run_workflow_btn.click()
        # Wait for workflow form to load and run button to appear
        self.wait.until(
            expected_conditions.presence_of_element_located((By.ID, "run-workflow"))
        )

    @clock_action("run_workflow")
    def run_workflow(self):
        if self.workflow_name == "Selenium_test_1":
            # Select relevant choice
            input_1_select = self.driver.find_element(
                By.XPATH,
                "//a[@class='select2-choice' and contains(., 'Subsample of reads from')]",
            )
            input_1_select.click()
            # Select relevant choice
            input_1_select = self.driver.find_element(
                By.XPATH,
                "//div[@id='select2-drop']//ul/li/div[contains(., 'Subsample of reads from human exome R1')]",
            )
            input_1_select.click()
            workflow_wait = 14400
        elif self.workflow_name == "Selenium_test_2":
            workflow_wait = 14400
        elif self.workflow_name == "Selenium_test_3":
            # Select relevant choice
            input_1_select = self.driver.find_element(
                By.XPATH,
                "//div[@step-label='Forward Reads']//a[@class='select2-choice']",
            )
            input_1_select.click()
            # Select relevant choice
            input_1_select = self.driver.find_element(
                By.XPATH,
                "//div[@id='select2-drop']//ul/li/div[contains(., 'ERR019289_1.fastq.gz')]",
            )
            input_1_select.click()
            workflow_wait = 14400
        elif self.workflow_name == "Selenium_test_4":
            input_select = self.driver.find_element(
                By.XPATH,
                "//div[@step-label='ARTIC primers to amplicon assignments']//a[@class='select2-choice']",
            )
            input_select.click()
            # Select relevant choice
            input_select = self.driver.find_element(
                By.XPATH,
                "//div[@id='select2-drop']//ul/li/div[contains(., 'ARTIC_SARS_CoV-2_amplicon_info_v3.tsv')]",
            )
            input_select.click()
            workflow_wait = 14400
        else:
            raise Exception(f"Workflow name not in known list: {self.workflow_name}")

        # Run the workflow
        self.driver.find_element(By.ID, "run-workflow").click()
        # Wait for view reports button to appear (workflow to finish)
        with SeleniumCustomWait(self.driver, workflow_wait):
            self.wait.until(
                expected_conditions.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[@id='center']//a[@class='invocation-report-link' and contains(., 'View Report')]",
                    )
                )
            )

    def run_test_sequence(self):
        self.load_galaxy_login()
        self.login_to_galaxy_homepage()
        self.search_for_tool()
        self.load_tool_form()
        self.load_shared_histories()
        self.import_shared_history()
        self.load_workflow_list()
        self.load_workflow_run_form()
        self.run_workflow()

    def measure_timings(self):
        self.timings = {}
        try:
            try:
                self.run_test_sequence()
            except EndStepReached:
                pass
        finally:
            self.driver.quit()

    def print_timings(self):
        for action, data in self.timings.items():
            print(
                f"user_flow_performance,server={self.server},action={action},run_id={self.run_id},end_step={self.end_step},workflow_name={self.workflow_name} time_taken={data.get('elapsed')} {data.get('timestamp')}"
            )


def from_env_or_required(key):
    return {"default": os.environ[key]} if os.environ.get(key) else {"required": True}


def create_parser():
    parser = argparse.ArgumentParser(
        description="Measure time taken for a typical user flow from login to tool execution in Galaxy."
    )
    parser.add_argument(
        "-s",
        "--server",
        default=os.environ.get("GALAXY_SERVER") or "https://usegalaxy.org.au",
        help="Galaxy server url",
    )
    parser.add_argument(
        "-u",
        "--username",
        **from_env_or_required("GALAXY_USERNAME"),
        help="Galaxy username to use (or set GALAXY_USERNAME env var)",
    )
    parser.add_argument(
        "-p",
        "--password",
        **from_env_or_required("GALAXY_PASSWORD"),
        help="Password to use (or set GALAXY_PASSWORD env var)",
    )
    parser.add_argument(
        "--end_step",
        default="tool_form_load",
        help="Stop performance timer at a specific step",
    )
    parser.add_argument(
        "--run_id",
        default=None,
        help="A unique id for this timing run. If not specified, a uuid is generated",
    )
    parser.add_argument(
        "--workflow_name",
        default="Selenium_test_1",
        help="The name of the workflow to run. Must be Selenium_test_1 through 4",
    )
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    perf_timer = PagePerfTimer(
        args.server,
        args.username,
        args.password,
        args.end_step,
        args.run_id,
        args.workflow_name,
    )
    perf_timer.measure_timings()
    perf_timer.print_timings()
    return 0


if __name__ == "__main__":
    sys.exit(main())
