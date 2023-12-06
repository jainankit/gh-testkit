import dataclasses
import textwrap
import typing as T

from gh.github import graphql


@dataclasses.dataclass
class IssueComment:
    id: str
    author: "Author"
    body: str

    @dataclasses.dataclass
    class Author:
        login: str

    FRAGMENT = textwrap.dedent(
        """
        fragment IssueComment on IssueComment {
            id
            author {
                login
            }
            body
        }
        """
    )

    @classmethod
    def from_graphql(cls, data: T.Dict[str, T.Any]) -> "IssueComment":
        return cls(
            id=data["id"],
            author=cls.Author(
                login=data["author"]["login"],
            ),
            body=data["body"],
        )


def add_comment(subject_id: str, body: str) -> "IssueComment":
    res = graphql(
        """
        mutation ($input: AddCommentInput!) {
            addComment(input: $input) {
                commentEdge {
                    node {
                        ...IssueComment
                    }
                }
            }
        }
        """
        + IssueComment.FRAGMENT,
        {
            "input": {
                "subjectId": subject_id,
                "body": body,
            }
        },
    )
    return IssueComment.from_graphql(res["data"]["addComment"]["commentEdge"]["node"])
