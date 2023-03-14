import json

import requests

from django_webix.contrib.sender.send_methods.skebby.enums import SkebbyBoolean, SkebbyMessageType, SkebbyEncoding
from django_webix.contrib.sender.send_methods.skebby.exceptions import SkebbyException


class Skebby:
    """
    https://developers.skebby.it
    """

    url = "https://api.skebby.it/API/v1.0/REST/"

    class Authentication:
        """
        Authentication methods

        The following are the two available methods to authenticate a user, given a username and a password
        (registration required):
        - Using a temporary session key, which expires after a certain amount of time has passed with no performed API
        calls with that key.
        - Using an authentication token, which does not expire, except when an account is deactivated or suspended.
        In both cases, the returned user_key, as well as the session key or the token, are required to be provided in
        the HTTP request headers in order to perform any API call after the login.
        """

        def __init__(self):
            self._user_key = None
            self._session_key = None
            self._access_token = None

        @property
        def headers(self):
            if self._user_key is not None and (self._session_key is not None or self._access_token is not None):
                if self._session_key is not None:
                    return {'user_key': self._user_key, 'Session_key': self._session_key,
                            'Content-type': 'application/json'}
                elif self._access_token is not None:
                    return {'user_key': self._user_key, 'Access_token': self._access_token,
                            'Content-type': 'application/json'}
            raise SkebbyException("You need to authenticate before")

        def session_key(self, username, password):
            """
            Authenticate using a session key

            The login with session key API lets you authenticate by using your username and password, and returns a
            token to be used for authenticating the next API calls. The following HTTP headers should be provided after
            the login:
            - user_key:USER_KEY
            - Session_key:SESSION_KEY
            Where USER_KEY and SESSION_KEY are the values returned by the login API.
            """

            params = {
                "username": username,
                "password": password
            }
            r = requests.get("{url}login".format(url=Skebby.url), params=params)

            if r.status_code != 200:
                raise SkebbyException("Error! http code: " + str(r.status_code) + ", body message: " + str(r.content))
            else:
                response = r.text
                user_key, session_key = response.split(';')
                self._user_key = user_key
                self._session_key = session_key

        def user_token(self, username, password):
            """
            Authenticate using a user token

            The login with token API lets you authenticate by using your username and password, and returns a token to
            be used for authenticating the next API calls. The following HTTP headers should be provided after the
            login:
            - user_key:USER_KEY
            - Access_token:ACCESS_TOKEN
            Where USER_KEY and ACCESS_TOKEN are the values returned by the login API.
            """

            params = {
                "username": username,
                "password": password
            }
            r = requests.get("{url}token".format(url=Skebby.url), params=params)

            if r.status_code != 200:
                raise SkebbyException("Error! http code: " + str(r.status_code) + ", body message: " + str(r.content))
            else:
                response = r.text
                user_key, access_token = response.split(';')
                self._user_key = user_key
                self._access_token = access_token

    class User:
        """
        User API

        The following are utility functions regarding the Authenticated User (e.g. the user status, password reset, etc)
        """

        def __init__(self, authentication):
            self._authentication = authentication

        def dashboard(self):
            """
            Dashboard

            API used to retrieve the dashboard URL of the authenticated user
            """

            r = requests.get("{url}dashboard".format(url=Skebby.url), headers=self._authentication.headers)

            if r.status_code != 200:
                raise SkebbyException("Error! http code: " + str(r.status_code) + ", body message: " + str(r.content))
            else:
                response = r.text
                return response

        def verify_session(self):
            """
            Verify session

            Checks whether the user session is still active and valid (without renewal).
            """

            r = requests.get("{url}checksession".format(url=Skebby.url), headers=self._authentication.headers)

            if r.status_code != 200:
                raise SkebbyException("Error! http code: " + str(r.status_code) + ", body message: " + str(r.content))
            else:
                response = r.text
                return response == "true"

        def reset_password(self, password):
            """
            Reset password

            Changes the authenticated user’s password
            """

            params = {
                "password": password
            }
            r = requests.get(
                "{url}pwdreset".format(url=Skebby.url),
                params=params,
                headers=self._authentication.headers
            )

            if r.status_code != 200:
                raise SkebbyException("Error! http code: " + str(r.status_code) + ", body message: " + str(r.content))
            else:
                response = r.text
                return response == "true"

        def user_status(self, get_money=SkebbyBoolean.FALSE, type_aliases=SkebbyBoolean.FALSE):
            """
            User status

            Used to retrieve the credits and other information of the user identified by the id.
            """

            if not isinstance(get_money, SkebbyBoolean):
                raise SkebbyException("getMoney allows only SkebbyBoolean enum")
            if not isinstance(type_aliases, SkebbyBoolean):
                raise SkebbyException("typeAliases allows only SkebbyBoolean enum")

            params = {
                "getMoney": get_money.value,
                "typeAliases": type_aliases.value
            }
            r = requests.get(
                "{url}status".format(url=Skebby.url),
                params=params,
                headers=self._authentication.headers
            )

            if r.status_code != 200:
                raise SkebbyException("Error! http code: " + str(r.status_code) + ", body message: " + str(r.content))
            else:
                response = r.text

                obj = json.loads(response)
                return obj

    class Contacts:
        """
        Contacts API

        This part of the API is used to manage contacts.
        """

        def __init__(self, authentication):
            self._authentication = authentication

        def add_contact(self, email, phone_number, name="", surname="", gender="", fax="", address="", city="",
                        province="", birthdate="", promotiondate="", rememberdate="", zip_code="", group_ids=None,
                        custom1="", custom2="", custom3="", custom4="", custom5="", custom6="", custom7="", custom8="",
                        custom9="", custom10=""):
            """
            Add a contact

            Add a contact to the user’s addressbook.
            """

            if group_ids is None:
                group_ids = []

            payload = {
                "email": email,
                "phoneNumber": phone_number,
            }
            if name is not None: payload["name"] = name
            if surname is not None: payload["surname"] = surname
            if gender is not None: payload["gender"] = gender
            if fax is not None: payload["fax"] = fax
            if zip_code is not None: payload["zip"] = zip_code
            if address is not None: payload["address"] = address
            if city is not None: payload["city"] = city
            if province is not None: payload["province"] = province
            if birthdate is not None: payload["birthdate"] = birthdate
            if group_ids is not None: payload["groupIds"] = group_ids
            if promotiondate is not None: payload["promotiondate"] = promotiondate
            if rememberdate is not None: payload["rememberdate"] = rememberdate
            if custom1 is not None: payload["custom1"] = custom1
            if custom2 is not None: payload["custom2"] = custom2
            if custom3 is not None: payload["custom3"] = custom3
            if custom4 is not None: payload["custom4"] = custom4
            if custom5 is not None: payload["custom5"] = custom5
            if custom6 is not None: payload["custom6"] = custom6
            if custom7 is not None: payload["custom7"] = custom7
            if custom8 is not None: payload["custom8"] = custom8
            if custom9 is not None: payload["custom9"] = custom9
            if custom10 is not None: payload["custom10"] = custom10

            payload = str(json.dumps(payload))

            r = requests.post("{url}contact".format(url=Skebby.url), headers=self._authentication.headers, data=payload)

            if r.status_code != 201:
                raise SkebbyException("Error! http code: " + str(r.status_code) + ", body message: " + str(r.content))
            else:
                response = r.text

                obj = json.loads(response)
                return obj

        def add_multiple_contacts(self):
            # TODO: to implement
            raise NotImplementedError

        def get_contact(self):
            # TODO: to implement
            raise NotImplementedError

        def get_all_contacts(self):
            # TODO: to implement
            raise NotImplementedError

        def get_contact_custom_fields(self):
            # TODO: to implement
            raise NotImplementedError

        def add_contact_to_blacklist(self):
            # TODO: to implement
            raise NotImplementedError

        def add_multiple_contacts_to_blacklist(self):
            # TODO: to implement
            raise NotImplementedError

        def add_phone_number_to_blacklist(self):
            # TODO: to implement
            raise NotImplementedError

    class ContactsGroups:
        """
        Contacts groups API

        This section describes how groups of contacts are created, updated and deleted. SMS messages can be directly
        sent to groups of contacts.
        """

        def __init__(self, authentication):
            self._authentication = authentication

        def create_contacts_group(self):
            # TODO: to implement
            raise NotImplementedError

        def modify_existing_contacts_group(self):
            # TODO: to implement
            raise NotImplementedError

        def delete_contacts_group(self):
            # TODO: to implement
            raise NotImplementedError

        def list_contact_group(self):
            # TODO: to implement
            raise NotImplementedError

        def add_contact_to_group(self):
            # TODO: to implement
            raise NotImplementedError

        def remove_contact_from_group(self):
            # TODO: to implement
            raise NotImplementedError

    class TPOA:
        """
        TPOA API

        The TPOA (Transmission Path Originating Address) API is used to deal with TPOA entries
        (i.e. “SMS sender aliases”) of the user.
        """

        def __init__(self, authentication):
            self._authentication = authentication

        def create_alias(self):
            # TODO: to implement
            raise NotImplementedError

        def get_aliases(self):
            # TODO: to implement
            raise NotImplementedError

        def get_alias(self):
            # TODO: to implement
            raise NotImplementedError

        def remove_alias(self):
            # TODO: to implement
            raise NotImplementedError

    class SmsSend:
        """
        SMS send API

        This is the part of the API that allows to send SMS messages, to single recipients, saved contacts or groups
        of contacts.
        """

        def __init__(self, authentication):
            self._authentication = authentication

        def send_sms(self, message_type: SkebbyMessageType, message, recipient, sender="", scheduled_delivery_time=None,
                     scheduled_delivery_timezone=None, order_id=None, return_credits=SkebbyBoolean.FALSE,
                     return_remaining=SkebbyBoolean.FALSE, allow_invalid_recipients=SkebbyBoolean.FALSE,
                     encoding=SkebbyEncoding.GSM, id_landing=None, campaign_name=None, max_fragments=7,
                     truncate=SkebbyBoolean.TRUE, richsms_url=None):
            """
            Send an SMS message

            Sends an SMS message to a given list of recipients.

            Landing Pages URLs
            It is possible to include a link to a published Landing Page by specifying the id_landing parameter and by
            adding the following placeholder in the message body: %PAGESLINK____________%.

            Landing pages must be first created and published in your user panel, since you will need id_landing to
            send it.
            A list of published landing pages can be retrieved by using the Landing Pages APIs

            SMS Link Analytics
            When including URLs in the message, it may be convenient to use our SMS Link Analytics short URLs service
            to limit the number of characters used in the SMS message and having statistic on clic. Our API can
            automatically generate a short link starting from a long one, and add it in the message. To use this
            feature, use the %RICHURL_______% placeholder in the message body, that will be replaced with the generated
            short link, and the respective richsms_url parameter, that should be set to a valid URL.

            Sender Alias
            Alphanumeric aliases are required to be registered first, and need to be approved both from Us and AGCOM.
            Aliases can be used only with high-quality message types.
            """

            if recipient is None:
                recipient = []
            if not isinstance(recipient, list):
                recipient = [recipient]

            payload = {
                "message_type": message_type.name,
                "message": message,
                "recipient": recipient,
            }

            if sender is not None: payload["sender"] = sender
            if scheduled_delivery_time is not None: payload["scheduled_delivery_time"] = scheduled_delivery_time
            if scheduled_delivery_timezone is not None:
                payload["scheduled_delivery_timezone"] = scheduled_delivery_timezone
            if order_id is not None: payload["order_id"] = order_id
            if return_credits is not None: payload["returnCredits"] = return_credits.value
            if return_remaining is not None: payload["returnRemaining"] = return_remaining.value
            if allow_invalid_recipients is not None: payload["allowInvalidRecipients"] = allow_invalid_recipients.value
            if encoding is not None: payload["encoding"] = encoding.value
            if id_landing is not None: payload["id_landing"] = id_landing
            if campaign_name is not None: payload["campaign_name"] = campaign_name
            if max_fragments is not None: payload["max_fragments"] = max_fragments
            if truncate is not None: payload["truncate"] = truncate.value
            if richsms_url is not None: payload["richsms_url"] = richsms_url

            payload = str(json.dumps(payload))

            r = requests.post("{url}sms".format(url=Skebby.url), headers=self._authentication.headers, data=payload)

            if r.status_code != 201:
                raise SkebbyException("Error! http code: " + str(r.status_code) + ", body message: " + str(r.content))
            else:
                response = r.text

                obj = json.loads(response)
                return obj

        def send_parametric_sms(self, message_type: SkebbyMessageType, message, recipients, sender="",
                                scheduled_delivery_time=None, scheduled_delivery_timezone=None, order_id=None,
                                return_credits=SkebbyBoolean.FALSE, return_remaining=SkebbyBoolean.FALSE,
                                allow_invalid_recipients=SkebbyBoolean.FALSE, encoding=SkebbyEncoding.GSM,
                                id_landing=None, campaign_name=None, max_fragments=7, truncate=SkebbyBoolean.TRUE,
                                richsms_url=None, richsms_mode=None):
            """
            Send a parametric SMS message

            Sends a parametric SMS message to a given list of recipients.
            With this API it is possible to put placeholders in the message body, and then, for each recipient,
            specify the values that will replace the placeholders in the message body, for that particular recipient
            message.
            Placeholders are in the form ${ParameterName}

            Landing Pages URLs
            It is possible to include a link to a published Landing Page by specifying the id_landing parameter and by
            adding the following placeholder in the message body: %PAGESLINK____________%.

            Landing pages must be first created and published in your user panel, since you will need id_landing to
            send it.
            A list of published landing pages can be retrieved by using the Landing Pages APIs

            SMS Link Analytics
            When including URLs in the message, it may be convenient to use our SMS Link Analytics short URLs service
            to limit the number of characters used in the SMS message and having statistic on clic.
            Our API can automatically generate a short link starting from a long one, and add it in the message.
            To use this feature, use the %RICHURL____________% placeholder in the message body and set the parameter
            rich_mode with one of following values:
            DIRECT_URL: in this case you must add the parameter richsms_url with the url that you want to be shortened
            RECIPIENT: in this case the url must be set in the url property for each recipient in recipients parameter.
            You could omit richsms_mode if you specify both the richsms_url params and %RICHURL__________% placeholder.

            Aliases can be used only with high-quality message types.
            """

            if recipients is None:
                recipients = {}

            payload = {
                "message_type": message_type.name,
                "message": message,
                "recipients": recipients,
            }

            if sender is not None: payload["sender"] = sender
            if scheduled_delivery_time is not None: payload["scheduled_delivery_time"] = scheduled_delivery_time
            if scheduled_delivery_timezone is not None:
                payload["scheduled_delivery_timezone"] = scheduled_delivery_timezone
            if order_id is not None: payload["order_id"] = order_id
            if return_credits is not None: payload["returnCredits"] = return_credits.value
            if return_remaining is not None: payload["returnRemaining"] = return_remaining.value
            if allow_invalid_recipients is not None: payload["allowInvalidRecipients"] = allow_invalid_recipients.value
            if encoding is not None: payload["encoding"] = encoding.value
            if id_landing is not None: payload["id_landing"] = id_landing
            if campaign_name is not None: payload["campaign_name"] = campaign_name
            if max_fragments is not None: payload["max_fragments"] = max_fragments
            if truncate is not None: payload["truncate"] = truncate.value
            if richsms_url is not None: payload["richsms_url"] = richsms_url
            if richsms_mode is not None: payload["richsms_mode"] = richsms_mode

            payload = str(json.dumps(payload))

            r = requests.post(
                "{url}paramsms".format(url=Skebby.url),
                headers=self._authentication.headers,
                data=payload
            )

            if r.status_code != 201:
                raise SkebbyException("Error! http code: " + str(r.status_code) + ", body message: " + str(r.content))
            else:
                response = r.text

                obj = json.loads(response)
                return obj

        def send_sms_to_group(self):
            # TODO: to implement
            raise NotImplementedError

        def get_sms_state(self, order_id):
            """
            Get SMS message state

            Get informations on the SMS delivery status of the given order_id.
            """

            r = requests.get("{url}sms/{order_id}".format(
                url=Skebby.url,
                order_id=order_id
            ), headers=self._authentication.headers)

            if r.status_code != 200:
                raise SkebbyException("Error! http code: " + str(r.status_code) + ", body message: " + str(r.content))
            else:
                response = r.text

                obj = json.loads(response)
                return obj

        def delete_scheduled_message(self):
            # TODO: to implement
            raise NotImplementedError

        def delete_all_scheduled_messages(self):
            # TODO: to implement
            raise NotImplementedError

    class SmsHistory:
        """
        SMS History API

        This API is used to retrieve the SMS messages sending history.
        """

        def __init__(self, authentication):
            self._authentication = authentication

        def get_sent_sms_history(self, date_from, date_to="now", timezone=None, page_number=1, page_size=10):
            """
            Get sent SMS history

            Returns the user’s SMS messages history
            """

            params = {
                "from": date_from,
                "to": date_to,
                "pageNumber": page_number,
                "pageSize": page_size
            }
            if timezone is not None:
                params['timezone'] = timezone

            r = requests.get(
                "{url}smshistory".format(url=Skebby.url),
                params=params,
                headers=self._authentication.headers
            )

            if r.status_code != 200:
                raise SkebbyException("Error! http code: " + str(r.status_code) + ", body message: " + str(r.content))
            else:
                response = r.text

                obj = json.loads(response)
                return obj

        def get_sent_sms_to_recipient(self, recipient, date_from, date_to="now", timezone=None, page_number=1,
                                      page_size=10):
            """
            Get sent SMS to a recipient

            Returns the user’s SMS messages history for the specified recipient
            """

            params = {
                "recipient": recipient,
                "from": date_from,
                "to": date_to,
                "pageNumber": page_number,
                "pageSize": page_size
            }
            if timezone is not None:
                params['timezone'] = timezone

            r = requests.get(
                "{url}rcptHistory".format(url=Skebby.url),
                params=params,
                headers=self._authentication.headers
            )

            if r.status_code != 200:
                raise SkebbyException("Error! http code: " + str(r.status_code) + ", body message: " + str(r.content))
            else:
                response = r.text

                obj = json.loads(response)
                return obj

        def get_sent_rich_sms_statistics(self, order_id):
            """
            Get sent Rich SMS statistics

            After sending an sms campaign via API containing a Rich sms shortened link, this api returns that sms
            link’s opening statistics. Keep in mind that you need to use a unique order_id when sending and store it to
            request in the near future.
            """

            params = {
                "order_id": order_id
            }
            r = requests.get(
                "{url}smsrich/statistics".format(url=Skebby.url),
                params=params,
                headers=self._authentication.headers
            )

            if r.status_code != 200:
                raise SkebbyException("Error! http code: " + str(r.status_code) + ", body message: " + str(r.content))
            else:
                response = r.text

                obj = json.loads(response)
                return obj

    class SmsBlacklist:
        """
        SMS Blacklist / Stop SMS

        This is the part of the API that allow to insert and to retrieve the list of SMS blacklist / Stop SMS.
        The SMS blacklist contains the phone numbers to which you don’t want to send any SMS.
        If the Stop SMS Service is active, any person who receive an SMS can add their phone number to the blacklist.
        """

        def __init__(self, authentication):
            self._authentication = authentication

        def add_phone_number_to_blacklist(self):
            # TODO: to implement
            raise NotImplementedError

        def add_multiple_numbers_to_blacklist(self):
            # TODO: to implement
            raise NotImplementedError

        def retrieve_phone_numbers_in_blacklist(self):
            # TODO: to implement
            raise NotImplementedError

    class ReceivedSMS:
        """
        Received SMS API

        This API allows to query the received SMS messages on the owned SIMs.
        """

        def __init__(self, authentication):
            self._authentication = authentication

        def get_new_received_messages(self):
            # TODO: to implement
            raise NotImplementedError

        def get_received_messages(self):
            # TODO: to implement
            raise NotImplementedError

        def get_received_messages_after_specified_message(self):
            # TODO: to implement
            raise NotImplementedError

        def get_mo_received_messages(self):
            # TODO: to implement
            raise NotImplementedError

    class LandingPages:
        """
        Landing pages API

        This is the part of the API that is concerned with the landing pages service.
        """

        def __init__(self, authentication):
            self._authentication = authentication

        def list_published_landing_pages(self):
            # TODO: to implement
            raise NotImplementedError

    class Subaccount:
        """
        Subaccount API

        If enabled as a superaccount, the user can create subaccounts that can be assigned to third-parties.
        Superaccounts may or may not share credits with their subaccounts.
        """

        def __init__(self, authentication):
            self._authentication = authentication

        def list_subaccounts(self):
            # TODO: to implement
            raise NotImplementedError

        def create_subaccount(self):
            # TODO: to implement
            raise NotImplementedError

        def edit_subaccount(self):
            # TODO: to implement
            raise NotImplementedError

        def change_subaccount_password(self):
            # TODO: to implement
            raise NotImplementedError

        def get_subaccount(self):
            # TODO: to implement
            raise NotImplementedError

        def get_subaccount_available_credits(self):
            # TODO: to implement
            raise NotImplementedError

        def get_subaccount_purchases(self):
            # TODO: to implement
            raise NotImplementedError

        def create_subaccount_purchase(self):
            # TODO: to implement
            raise NotImplementedError

        def delete_subaccount_purchase(self):
            # TODO: to implement
            raise NotImplementedError

    class TwoFactorAuthentication:
        """
        Two Factor Authentication API

        This is the part of the API that provides the Two Factor Authentication. The flow of 2FA is:
        1. The user specifies their number in your App.
        2. Your app sends a 2FA request via API.
        3. The platform sends a text message to the specified recipient.
        4. User receives the PIN via text message.
        5. User enters the PIN in your App.
        6. Your app sends the 2FA verify via API and receives the authorization or an invalid pin error.

        The text message is sent with the highest quality on a preferred route, to guarantee a quick delivery.
        """

        def __init__(self, authentication):
            self._authentication = authentication

        def request_2fa_pin(self):
            # TODO: to implement
            raise NotImplementedError

        def verify_2fa_pin(self):
            # TODO: to implement
            raise NotImplementedError

    def __init__(self):
        self.authentication = self.Authentication()
        self.user = self.User(self.authentication)
        self.contacts = self.Contacts(self.authentication)
        self.contacts_groups = self.ContactsGroups(self.authentication)
        self.tpoa = self.TPOA(self.authentication)
        self.sms_send = self.SmsSend(self.authentication)
        self.sms_history = self.SmsHistory(self.authentication)
        self.sms_blacklist = self.SmsBlacklist(self.authentication)
        self.received_sms = self.ReceivedSMS(self.authentication)
        self.landing_pages = self.LandingPages(self.authentication)
        self.subaccounts = self.Subaccount(self.authentication)
        self.two_factor_authentication = self.TwoFactorAuthentication(self.authentication)
