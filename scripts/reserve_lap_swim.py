import logging
import os
import time
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

USERNAME = os.environ["BCYF_USERNAME"]
PASSWORD = os.environ["BCYF_PASSWORD"]

logging.basicConfig(
    filename="lap_registration.log",
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
)
logging.write = lambda msg: logging.info(msg) if msg != "\n" else None

if __name__ == "__main__":
    with redirect_stderr(logging):
        with redirect_stdout(logging):
            print("Attempting lap swim registration...")
            service = Service(executable_path=GeckoDriverManager().install())

            with Firefox(service=service) as driver:
                # maximize to avoid responsive UI
                driver.maximize_window()
                wait = WebDriverWait(driver, 60)

                # open registration
                print("Opening webpage...")
                today = datetime.today()
                driver.get(
                    "https://bcyf.perfectmind.com/25235/Clients/BookMe4EventParticipants"
                    "?eventId=61d62d71-2f43-18f1-8a1d-135ca17860df"
                    "&widgetId=e99962b0-f669-408a-ac7f-61fe3e463f9b"
                    "&locationId=689f96f5-baba-40c7-8c97-3b5264be6146"
                    "&waitListMode=False"
                    f"&occurrenceDate={today.strftime('%Y%m%D')}"
                )

                # login
                print("Logging in...")
                wait.until(
                    lambda d: d.find_element(By.ID, "textBoxUsername")
                ).send_keys(USERNAME)
                driver.find_element(By.ID, "textBoxPassword").send_keys(PASSWORD)
                driver.find_element(By.ID, "logonform").submit()

                # check if registration is possible
                print("Confirming registration window...")
                metadata = wait.until(
                    lambda d: d.find_elements(
                        By.CSS_SELECTOR, ".event-info-column > label"
                    )
                )
                if (
                    metadata[0].text != today.strftime("%m/%D/%y")
                    or metadata[1].text != "12:15 pm - 01:00 pm"
                    or metadata[2].text == "Full"
                ):
                    print("No spots available from 12:15 - 1pm was available today. :(")
                    print("Exiting...")
                    exit()

                # hold registration and accept conditions
                print("Registering...")
                for _ in range(2):
                    wait.until(
                        lambda d: d.find_element(By.CSS_SELECTOR, '[title="Next"]')
                    ).click()

                # register
                wait.until(
                    lambda d: driver.find_element(By.ID, "checkoutButton")
                ).click()
                wait.until(
                    lambda d: d.find_element(By.CLASS_NAME, "process-now")
                ).click()

                print("Success!")
                time.sleep(10)
