from __future__ import annotations

from typing import List, Optional

from monzo.authentication import Authentication
from monzo.endpoints.balance import Balance
from monzo.endpoints.monzo import Monzo
from monzo.exceptions import MonzoHTTPError

ACCOUNT_TYPES = [
    'uk_retail',
    'uk_retail_joint',
]


class Account(Monzo):
    __slots__ = ['_account_id', '_auth', '_balance', '_created', '_description', '_has_balance']

    def __init__(self, auth: Authentication, account_id: str, description: str, created: str):
        """
        Standard init

        Args:
            account_id: ID of the account
            description: Description of the account
            created: Date and time the account was created
        """
        self._auth = auth
        self._account_id = account_id
        self._balance: Optional[Balance] = None
        self._created = created
        self._description = description
        self._has_balance: bool = True
        super().__init__(auth=auth)

    @property
    def account_id(self) -> str:
        """
        Property for account_id.

        Returns:
            Account ID for the account
        """
        return self._account_id

    @property
    def balance(self) -> Optional[Balance]:
        """
        Property for balance.

        Returns:
            Balance object
        """
        if not self._balance and self._has_balance:
            try:
                self._balance = Balance.fetch(auth=self._auth, account_id=self._account_id)
            except MonzoHTTPError:
                self._has_balance = False
        return self._balance

    @property
    def created(self) -> str:
        """
        Property for created.

        Returns:
            When the account was created
        """
        return self._created

    @property
    def description(self) -> str:
        """
        Property for description.

        Returns:
            Description for the account
        """
        return self._description

    @classmethod
    def fetch(cls, auth: Authentication, account_type: str = None) -> List[Account]:
        """
        Implements and instantiates a Account object

        Args:
             auth: Monzo authentication object
             account_type: Optional type of account required, must be in ACCOUNT_TYPES

        Returns:
            List of instantiated Account objects
        """
        data = {}
        if account_type and account_type.lower() in ACCOUNT_TYPES:
            data['account_type'] = account_type.lower()
        res = auth.make_request(path='/accounts', data=data)
        account_list = []
        for account_item in res['data']['accounts']:
            account = cls(
                auth=auth,
                account_id=account_item['id'],
                description=account_item['description'],
                created=account_item['created']
            )
            account_list.append(account)
        return account_list