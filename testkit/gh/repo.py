import dataclasses
import typing as T

from .utils import iter_connection
from .github import graphql


@dataclasses.dataclass
class Repo:
    id: str
    full_name: str
    head_sha: str
    base_branch_name: str
    labels: T.List["Label"]

    def resolve_label_id(self, name: str) -> str:
        """
        Get the id of a label from its name.

        This is important since many places in the GraphQL API expect a label
        id, not just the name of the label.
        """
        for label in self.labels:
            if label.name == name:
                return label.id
        raise ValueError(f"Label {name} does not exist on repo {self.full_name}")


@dataclasses.dataclass
class Label:
    id: str
    name: str

    FRAGMENT = """
    fragment Label on Label {
      id
      name
    }
    """

    @classmethod
    def from_graphql(cls, data: T.Dict[str, T.Any]) -> "Label":
        return cls(
            id=data["id"],
            name=data["name"],
        )


def get_repo(owner: str, name: str) -> Repo:
    res = graphql(
        """
        query ($owner: String!, $name: String!) {
            repository(owner: $owner, name: $name) {
                id
                nameWithOwner
                defaultBranchRef {
                    name
                    target {
                        oid
                    }
                }
                labels(first: 50) {
                    nodes { ...Label }
                }
            }
        }
        """
        + Label.FRAGMENT,
        variables={"owner": owner, "name": name},
    )["data"]["repository"]
    assert res["id"]
    return Repo(
        id=res["id"],
        full_name=res["nameWithOwner"],
        head_sha=res["defaultBranchRef"]["target"]["oid"],
        base_branch_name=res["defaultBranchRef"]["name"],
        labels=[Label.from_graphql(l) for l in res["labels"]["nodes"]],
    )
