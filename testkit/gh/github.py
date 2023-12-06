import contextlib
import contextvars
import dataclasses
import json
import textwrap
import typing as T

import requests

from .config import get_config


account_ctx = contextvars.ContextVar("github_account", default="primary")


@contextlib.contextmanager
def github_account(account: str):
    token = account_ctx.set(account)
    try:
        yield
    finally:
        account_ctx.reset(token)


@dataclasses.dataclass
class GraphQLErrorsException(Exception):
    errors: T.List[dict]
    query: str

    def __str__(self):
        return f"{self.__class__.__name__}({self.errors!r})" + textwrap.indent(
            self.query, "  "
        )


def graphql(query, variables: T.Optional[dict] = None, *, raise_graphql_errors=True):
    config = get_config()
    account = account_ctx.get()
    token = (
        config["github"]["primaryToken"]
        if account == "primary"
        else config["github"]["secondaryToken"]
    )
    res = requests.post(
        "https://api.github.com/graphql",
        headers={
            "Authorization": f"Bearer {token}",
        },
        data=json.dumps(
            {
                "query": query,
                "variables": variables or {},
            }
        ),
    )
    res.raise_for_status()
    payload = res.json()
    if raise_graphql_errors and payload.get("errors", None):
        raise GraphQLErrorsException(payload["errors"], query)
    return payload


def query_viewer_login(account="primary") -> str:
    return graphql(
        """
        query {
            viewer {
                login
            }
        }
        """,
        account=account,
    )["data"]["viewer"]["login"]
