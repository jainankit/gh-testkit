import dataclasses
import typing as T

from .ref import Ref
from .github import graphql
from .repo import Label
from .utils import iter_connection


STATE_OPEN = "OPEN"
STATE_CLOSED = "CLOSED"
STATE_MERGED = "MERGED"


@dataclasses.dataclass
class PullRequest:
    id: str
    number: int
    state: str
    permalink: str
    head_ref: "Ref"
    labels: T.List["Label"]

    def has_label(self, label: str) -> bool:
        return label in [l.name for l in self.labels]

    FRAGMENT = (
        """
        fragment PullRequest on PullRequest {
            id
            number
            state
            permalink
            headRef { ...Ref }
            labels(first: 50) {
              nodes { ...Label }
            }
        }
        """
        + Ref.FRAGMENT
        + Label.FRAGMENT
    )

    @classmethod
    def from_graphql(cls, data: T.Dict[str, T.Any]) -> "PullRequest":
        return cls(
            id=data["id"],
            number=data["number"],
            state=data["state"],
            permalink=data["permalink"],
            head_ref=Ref.from_graphql(data["headRef"]) if data["headRef"] else None,
            labels=[Label.from_graphql(label) for label in data["labels"]["nodes"]],
        )


@dataclasses.dataclass
class PullRequestReview:
    id: str
    state: str

    FRAGMENT = """
    fragment PullRequestReview on PullRequestReview {
        id
        state
    }
    """

    @classmethod
    def from_graphql(cls, data: T.Dict[str, T.Any]) -> "PullRequestReview":
        return cls(
            id=data["id"],
            state=data["state"],
        )


def create_pull_request(
    repo_id: str,
    title: str,
    base_branch_name: str,
    head_branch_name: str,
    *,
    body: str = "",
) -> PullRequest:
    res = graphql(
        """
        mutation CreatePullRequest(
            $input: CreatePullRequestInput!
        ) {
            createPullRequest(input: $input) {
                pullRequest {
                    ...PullRequest
                }
            }
        }
        """
        + PullRequest.FRAGMENT,
        variables={
            "input": {
                "repositoryId": repo_id,
                "title": title,
                "body": body,
                "baseRefName": f"refs/heads/{base_branch_name}",
                "headRefName": f"refs/heads/{head_branch_name}",
            },
        },
    )
    return PullRequest.from_graphql(res["data"]["createPullRequest"]["pullRequest"])


def list_repo_pull_requests(
    repo_id: str, *, states: T.List[str] = None
) -> T.List[PullRequest]:
    res = graphql(
        """
        query ListRepositoryPullRequests($id: ID!, $states: [PullRequestState!]) {
            node(id: $id) {
                ... on Repository {
                    pullRequests(first: 100, states: $states) {
                        edges { 
                            node {
                                ...PullRequest
                            }
                        }
                    }
                }
            }
        }
        """
        + PullRequest.FRAGMENT,
        variables={
            "id": repo_id,
            "states": states,
        },
    )

    return [
        PullRequest.from_graphql(d)
        for d in iter_connection(res["data"]["node"]["pullRequests"])
    ]


def get_repo_pull_request(repo_id: str, number: int) -> PullRequest:
    res = graphql(
        """
        query GetRepositoryPullRequest($id: ID!, $number: Int!) {
            node(id: $id) {
                ... on Repository {
                    pullRequest(number: $number) {
                        ...PullRequest
                    }
                }
            }
        }
        """
        + PullRequest.FRAGMENT,
        variables={
            "id": repo_id,
            "number": number,
        },
    )
    return PullRequest.from_graphql(res["data"]["node"]["pullRequest"])


def close_pull_request(pr_id: str) -> PullRequest:
    res = graphql(
        """
        mutation ClosePullRequest($input: ClosePullRequestInput!) {
            closePullRequest(input: $input) {
                pullRequest {
                    ...PullRequest
                }
            }
        }
        """
        + PullRequest.FRAGMENT,
        variables={
            "input": {
                "pullRequestId": pr_id,
            },
        },
    )
    return PullRequest.from_graphql(res["data"]["closePullRequest"]["pullRequest"])


def add_labels(id: str, label_ids: T.List[str]):
    res = graphql(
        """
        mutation AddLabelsToLabelable(
            $input: AddLabelsToLabelableInput!
        ) {
            addLabelsToLabelable(input: $input) {
                labelable {
                    labels(first: 100) {
                        edges {
                            node {
                                id
                            }
                        }
                    }
                }
            }
        }
        """,
        variables={
            "input": {
                "labelableId": id,
                "labelIds": label_ids,
            },
        },
    )

    data = res["data"]["addLabelsToLabelable"]["labelable"]
    assert data
    return None


def remove_labels(id: str, label_ids: T.List[str]):
    res = graphql(
        """
        mutation RemoveLabelsFromLabelable(
            $input: RemoveLabelsFromLabelableInput!
        ) {
            removeLabelsFromLabelable(input: $input) {
                labelable {
                    labels(first: 100) {
                        edges {
                            node {
                                id
                            }
                        }
                    }
                }
            }
        }
        """,
        variables={
            "input": {
                "labelableId": id,
                "labelIds": label_ids,
            },
        },
    )

    data = res["data"]["removeLabelsFromLabelable"]["labelable"]
    assert data
    return None


def add_pull_request_review(
    pull_request_id: str,
    event: str = "APPROVE",
) -> PullRequestReview:
    res = graphql(
        """
        mutation AddPullRequestReview(
            $input: AddPullRequestReviewInput!
        ) {
            addPullRequestReview(input: $input) {
                pullRequestReview {
                    ...PullRequestReview
                }
            }
        }
        """
        + PullRequestReview.FRAGMENT,
        variables={
            "input": {
                "pullRequestId": pull_request_id,
                "event": event,
            },
        },
    )

    return PullRequestReview.from_graphql(
        res["data"]["addPullRequestReview"]["pullRequestReview"]
    )
