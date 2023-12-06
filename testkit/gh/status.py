import dataclasses
import typing as T


@dataclasses.dataclass
class CheckRun:
    id: str
    name: str
    conclusion: str

    FRAGMENT = """
        fragment CheckRun on CheckRun {
            id
            name
            conclusion
        }
        """

    @classmethod
    def from_graphql(cls, data: T.Dict[str, T.Any]) -> "CheckRun":
        return cls(
            id=data["id"],
            name=data["name"],
            conclusion=data["conclusion"],
        )


@dataclasses.dataclass
class CheckSuite:
    conclusion: str
    check_runs: T.List["CheckRun"]

    FRAGMENT = (
        """
        fragment CheckSuite on CheckSuite {
            conclusion
            checkRuns(first: 50) {
                nodes {
                    ...CheckRun
                }
            }
        }
        """
        + CheckRun.FRAGMENT
    )

    @classmethod
    def from_graphql(cls, data: T.Dict[str, T.Any]) -> "CheckSuite":
        return cls(
            conclusion=data["conclusion"],
            check_runs=[
                CheckRun.from_graphql(check_run)
                for check_run in data["checkRuns"]["nodes"]
            ],
        )


@dataclasses.dataclass
class Status:
    contexts: T.List["StatusContext"]

    FRAGMENT = """
    fragment Status on Status {
        contexts {
            context
            state
            description
            createdAt
        }
    }
    """

    @classmethod
    def from_graphql(cls, data: T.Dict[str, T.Any]) -> "Status":
        return cls(
            contexts=[
                StatusContext.from_graphql(context) for context in data["contexts"]
            ],
        )


@dataclasses.dataclass
class StatusContext:
    context: str
    state: str
    description: str
    created_at: str

    FRAGMENT = """
    fragment StatusContext on StatusContext {
        context
        state
        description
        createdAt
    }
    """

    @classmethod
    def from_graphql(cls, data: T.Dict[str, T.Any]) -> "StatusContext":
        return cls(
            context=data["context"],
            state=data["state"],
            description=data["description"],
            created_at=data["createdAt"],
        )
