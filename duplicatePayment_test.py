# create 2 identical transactions.
# The first one is created successfully
# The second one is getting response status 400 (duplicate payment)
# The first one is canceled

import datetime
import json
import logging
import random
from time import sleep, gmtime, strftime, time
import requests

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG,  # If smth wrong, change to 'DEBUG'
                    filename="duplicate_payments.log")  # Name of log file
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
redirect_payload = {
    "initiator_account_id": "LT233200000034830587",
    "b2b_account_id": "63e3c750b1a81f5cac644529",
    "broker_name": "crymbo"
}

# m2m_login credentials
m2mlogin_API = "https://crymbo-integ.wallter.com/api/v2/auth/token"

# payment initiate credentials
paymentInit_API = "https://crymbo-integ.wallter.com/api/v2/payments/initiate"

# get account balance credentials
getAccount_API = "https://crymbo-integ.wallter.com/api/v2/account?currency=USD"

# payment cancel credentials
paymentCancel_API = "https://crymbo-integ.wallter.com/api/v2/payments/"


def main_flow():
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

        # m2m_login to Crymbo

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

        # DEBIT payment initiate
        amount = random.uniform(1, 10)
        fee = random.uniform(0.5, 2)

        paymentInit_payload = {
            "provider_name": "INX",
            "provider_account": "LT483200086036669146",
            "direction": "DEBIT",
            "provider_currency": "USD",
            "amount": amount,
            "fee": fee
        }
        offset = 0
        while offset < 2:
            try:
                paymentInit_response = s.post(paymentInit_API, headers={'Authorization': "Bearer " + crymbo_token},
                                          json=paymentInit_payload, verify=False)
                paymentId = paymentInit_response.json().get("result")

                if (paymentInit_response.status_code in (200, 201, 202, 204)) and (paymentId is not None):
                    logger.info("DEBIT Transaction is created")
                    logger.info(paymentId)
                    logger.info(amount)
                    logger.info(fee)
                elif (paymentInit_response.status_code in (200, 201, 202, 203, 204)) and (paymentId is None):
                    logger.info(paymentInit_response.text)
                else:
                    logger.info(paymentInit_response.status_code)
                    logger.info(paymentInit_response.text)
            except requests.exceptions.RequestException as e:
                logger.exception(e)
            offset +=1


main_flow()