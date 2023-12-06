import dataclasses
import typing as T

from .commit import Commit
from .github import graphql


@dataclasses.dataclass
class Ref:
    id: str
    name: str
    target: "Commit"

    FRAGMENT = (
        """
        fragment Ref on Ref {
            name
            id
            
            target {
              ...Commit
            }
        }
        """
        + Commit.FRAGMENT
    )

    @classmethod
    def from_graphql(cls, data: dict):
        return cls(
            id=data["id"],
            name=data["name"],
            target=Commit.from_graphql(data["target"]),
        )


def mutation_create_branch_ref(repo_id: str, branch_name: str, commit_id: str) -> Ref:
    ref_name = f"refs/heads/{branch_name}"
    res = graphql(
        """
        mutation CreateBranchRef($input: CreateRefInput!) {
            createRef(input: $input) {
                ref { ...Ref }
            }
        }
        """
        + Ref.FRAGMENT,
        variables={
            "input": {
                "repositoryId": repo_id,
                "name": ref_name,
                "oid": commit_id,
            },
        },
    )
    return Ref.from_graphql(res["data"]["createRef"]["ref"])


def mutation_delete_ref(ref_id: str) -> None:
    graphql(
        """
        mutation DeleteRef($input: DeleteRefInput!) {
            deleteRef(input: $input) {
                clientMutationId
            }
        }
        """,
        variables={
            "input": {
                "refId": ref_id,
            },
        },
    )


def query_list_refs(
    repo_id: str,
    query: T.Optional[str] = None,
    *,
    ref_prefix: str = "refs/heads/",
) -> T.List[Ref]:
    res = graphql(
        """
        query ListRefs($repoId: ID!, $refPrefix: String!, $query: String) {
            node(id: $repoId) {
                ... on Repository {
                    refs(first: 100, refPrefix: $refPrefix, query: $query) {
                        nodes {
                            ...Ref
                        }
                    }
                }
            }
        }
        """
        + Ref.FRAGMENT,
        variables={
            "repoId": repo_id,
            "refPrefix": ref_prefix,
            "query": query,
        },
    )
    return [Ref.from_graphql(ref) for ref in res["data"]["node"]["refs"]["nodes"]]
