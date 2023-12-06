import base64
import dataclasses
import typing as T

from .github import graphql
from .status import Status, CheckSuite


@dataclasses.dataclass
class Commit:
    id: str
    sha: str
    message: str
    check_suites: T.List["CheckSuite"]
    status: T.Optional["Status"]

    FRAGMENT = (
        """
        fragment Commit on Commit {
            id
            sha: oid
            message
            status { ...Status }
            checkSuites(first: 50) {
                nodes {
                    ...CheckSuite
                }
            }
        }
        """
        + Status.FRAGMENT
        + CheckSuite.FRAGMENT
    )

    @classmethod
    def from_graphql(cls, data: dict) -> "Commit":
        return cls(
            id=data["id"],
            sha=data["sha"],
            message=data["message"],
            status=Status.from_graphql(data["status"]) if data["status"] else None,
            check_suites=[
                CheckSuite.from_graphql(check_suite)
                for check_suite in data["checkSuites"]["nodes"]
            ],
        )


@dataclasses.dataclass
class Addition:
    path: str
    content: str


def mutation_create_commit_on_branch(
    branch_id: str,
    expected_head_sha: str,
    headline: str,
    additions: T.List[Addition],
) -> Commit:
    res = graphql(
        """
        mutation CreateCommitOnBranch($input: CreateCommitOnBranchInput!) {
            createCommitOnBranch(input: $input) {
                commit { ...Commit }
            }
        }
        """
        + Commit.FRAGMENT,
        variables={
            "input": {
                "branch": {"id": branch_id},
                "expectedHeadOid": expected_head_sha,
                "message": {
                    "headline": headline,
                },
                "fileChanges": {
                    "additions": [
                        {
                            "path": add.path,
                            "contents": base64.b64encode(add.content.encode()).decode(),
                        }
                        for add in additions
                    ],
                },
            }
        },
    )
    return Commit.from_graphql(res["data"]["createCommitOnBranch"]["commit"])


def get_branch_commits(
    repo_id: str, branch_name: str, *, first: int = 50
) -> T.List[Commit]:
    res = graphql(
        """
        query ($repoId: ID!, $name: String!, $first: Int!) {
          node(id: $repoId) {
            ... on Repository {
              ref(qualifiedName: $name) {
                target {
                  ... on Commit {
                    history(first: $first) {
                      nodes { ...Commit }
                    }
                  }
                }
              }
            }
          }
        }
        """
        + Commit.FRAGMENT,
        variables={
            "repoId": repo_id,
            "name": f"refs/heads/{branch_name}",
            "first": first,
        },
    )
    return [
        Commit.from_graphql(node)
        for node in res["data"]["node"]["ref"]["target"]["history"]["nodes"]
    ]
