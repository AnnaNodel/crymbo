import datetime
import json
import logging
import random
from time import sleep, gmtime, strftime, time
import requests

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG,  # If smth wrong, change to 'DEBUG'
                    filename="crymbo_balance.log")  # Name of log file
logger = logging.getLogger("Crymbo")
timeout = 15  # Timeout for APIs check (login not included!), in seconds
loop_time = 60  # Time between every loop, in second

# wallter credentials
wallter_token_API = 'https://test-wallter.eu.auth0.com/oauth/token'
wallter_payload = {"grant_type": "password",
                   "username": "customer@inx.com",
                   "password": "Inx@2023",
                   "audience": "https://api.wallter.services",
                   "scope": "openid profile email offline_access",
                   "client_id": "IZR8D7mTqHKZudqaSUfuWleoQ6mSKeie"}

# redirect credentials
redirect_API = "https://crymbo-integ.wallter.com/api/v2/auth/redirect"

# m2m_login credentials
m2mlogin_API = "https://crymbo-integ.wallter.com/api/v2/auth/token"

# get account balance credentials
getAccount_API = "https://crymbo-integ.wallter.com/api/v2/account?currency=USD"


def main_flow_create():
    # getting wallter token
    with requests.Session() as s:
        try:
            wallterLogin_response = s.post(wallter_token_API, data=wallter_payload)
            wallter_token = wallterLogin_response.json().get("access_token")

            if wallterLogin_response.status_code in (200, 201, 202, 204):
                logger.info("Successfully logged in to Wallter!")
            else:
                logger.info(wallterLogin_response.status_code)

        except requests.exceptions.RequestException as e:
            logger.exception(e)

        # redirect to crymbo
        accountID_array = ["LT233200000034830587", "LT393200000037080893", "LT843200000037293580",
                           "LT663200017372090184",
                           "LT433200085830579059"]

        for accountID in accountID_array:
            redirect_payload = {
                "initiator_account_id": accountID,
                "b2b_account_id": "63e3c750b1a81f5cac644529",
                "broker_name": "crymbo"
            }
            try:
                response_redirect = s.post(redirect_API, headers={'Authorization': "Bearer " + wallter_token},
                                           json=redirect_payload, verify=False)
                result = json.loads(response_redirect.content)
                ref_id = result.get("redirect_url").split("?session_id=")[1]  # retain ref id from redirect url

                if response_redirect.status_code in (201, 202, 204, 200):
                    logger.info("Successfully redirected to Crymbo!")
                    logger.info(ref_id)
                else:
                    logger.info(response_redirect.status_code)

            except requests.exceptions.RequestException as e:
                logger.exception(e)

            # m2m_login credentials
            m2m_payload = {
                "client_id": "aIhaP0NjIQFgKPPb35iWmIijgl3owE1D",
                "client_secret": "LO1O3uBGUXBQWzmI91NftM3nd2mSQZJ80WDqxGVvMFgonkG05OJUAw0PgRUOCGUI",
                "session_id": ref_id  # ref_id from a previous step
            }

            try:
                crymboLogin_response = s.post(m2mlogin_API, json=m2m_payload)
                crymbo_token = crymboLogin_response.json().get("access_token")

                if crymboLogin_response.status_code in (201, 202, 204, 200):
                    logger.info("Successfully logged in to Crymbo!")
                else:
                    logger.info(crymboLogin_response.status_code)

            except requests.exceptions.RequestException as e:
                logger.exception(e)

            # get balance

            try:
                getAccount_response = s.get(getAccount_API, headers={'Authorization': "Bearer " + crymbo_token},
                                            verify=False)
                accountBalance = getAccount_response.json().get("balance")
                if getAccount_response.status_code in (200, 201, 202, 204):
                    logger.info(accountID)
                    logger.info(accountBalance)
                else:
                    logger.info(getAccount_response.status_code)
            except requests.exceptions.RequestException as e:
                logger.exception(e)


main_flow_create()
