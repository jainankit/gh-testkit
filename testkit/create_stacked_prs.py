import argparse
import random
import time
import typing as T
import pydantic

import gh

parser = argparse.ArgumentParser()
parser.add_argument(
    "-a",
    "--approve",
    action="store_true",
    help=("Approve the PR using the secondary account credentials."),
)
parser.add_argument(
    "-l",
    "--label",
    action="append",
    help=("Add a label to the PR. Can be specified multiple times."),
)
parser.add_argument(
    "-c",
    "--count",
    type=int,
    default=2,
    help=("The number of PRs to create. Must be >= 2. Defaults to 2."),
)
parser.add_argument(
    "-u",
    "--update-original",
    action="store_true",
    help=(
        "Update the original PR with a new commit after creating the dependent"
        "PR. This is useful for testing that subsequent PRs in the stack are "
        "updated correctly when the first PR changes."
    ),
)
parser.add_argument(
    "--unique-files",
    action="store_true",
    help=(
        "If set, every PR in the stack will create its own unique file "
        "(rather than appending to the same file)."
    ),
)
parser.add_argument(
    "--merge",
    action="store_true",
    help=(
        "If set, merge the PR by commenting `/aviator stack merge` on the top "
        "PR in the stack."
    ),
)


class AvPRMetadata(pydantic.BaseModel):
    parent: str
    parent_head: T.Optional[str] = pydantic.Field(None, alias="parentHead")
    parent_pull: T.Optional[int] = pydantic.Field(None, alias="parentPull")
    trunk: str

    class Config:
        # see: https://stackoverflow.com/a/69308755
        populate_by_name = True


def main(args: T.Optional[argparse.Namespace] = None) -> T.List["gh.pr.PullRequest"]:
    args = args or parser.parse_args()

    conf = gh.config.get_config()
    repo_owner, repo_name = conf["github"]["repo"].split("/")
    repo = gh.repo.get_repo(repo_owner, repo_name)
    print(repo)

    tpl = f"mq-qa-stacked-{random.randint(0, 100000)}"
    base_branch = None
    base_sha = None
    root_branch, root_sha = None, None

    prs: T.List["gh.pr.PullRequest"] = []

    for n in range(1, args.count + 1):
        print("\n\nCreating PR #{}/{}".format(n, args.count))
        base_branch_name = base_branch.name if base_branch else repo.base_branch_name
        parent_pr_number = prs[-1].number if prs else None
        pr, base_branch, base_sha = create_new_pr(
            repo, tpl, n, base_branch_name, base_sha, parent_pr_number, args
        )
        prs.append(pr)
        if not root_branch:
            root_branch = base_branch
            root_sha = base_sha

    if args.update_original:
        update_original(root_branch, root_sha, tpl)

    if args.merge:
        print("\n\nPosting merge comment on top of stack")
        # Sleep for a few seconds to make sure that the queue has had the chance
        # to register the PR as a stacked PR
        time.sleep(3)
        comment = gh.issue.add_comment(prs[-1].id, "/aviator stack merge")
        print(comment)

    return prs


def create_new_pr(
    repo: "gh.repo.Repo",
    tpl: str,
    n: int,
    base_branch: str,
    base_sha: T.Optional[str],
    base_pr_number: T.Optional[int],
    args,
) -> T.Tuple["gh.pr.PullRequest", "gh.ref.Ref", str]:
    branch_name = f"{tpl}-{n}"
    pr_name = f"{tpl} [{n}]"

    branch_sha = base_sha if base_sha else repo.head_sha

    # create a branch
    branch = gh.ref.mutation_create_branch_ref(repo.id, branch_name, branch_sha)
    print(branch)

    # create a commit
    file_name = f"mq-qa/{tpl}-{n}.txt" if args.unique_files else f"mq-qa/{tpl}.txt"
    branch_commit = gh.commit.mutation_create_commit_on_branch(
        branch.id,
        branch_sha,
        pr_name,
        additions=[
            gh.commit.Addition(file_name, make_contents(tpl, n)),
        ],
    )
    print(branch_commit)

    # open a pr
    metadata = AvPRMetadata(
        parent=base_branch,
        parent_head=base_sha,
        parent_pull=base_pr_number,
        trunk=repo.base_branch_name,
    )
    pr = gh.pr.create_pull_request(
        repo.id,
        pr_name,
        base_branch,
        branch_name,
        body=(
            "Hidden Stacked PRs body below!\n\n"
            "<!-- av pr metadata\n"
            "```\n"
            f"{metadata.json(exclude_none=True, by_alias=True)}\n"
            "```\n"
            "-->"
        ),
    )
    print(pr)

    # approve the pr
    if args.approve:
        with gh.github.github_account("secondary"):
            approval = gh.pr.add_pull_request_review(pr.id, "APPROVE")
            print(approval)

    # add labels
    if args.label:
        label_ids = [repo.resolve_label_id(label) for label in args.label]
        gh.pr.add_labels(pr.id, label_ids)

    return pr, branch, branch_commit.sha


def make_contents(tpl: str, n: int) -> str:
    return "".join([f"{tpl} #{idx}\n" for idx in range(1, n + 1)])


def update_original(base_ref: "gh.ref.Ref", base_sha: str, tpl: str):
    contents = "this line was added in the root pr of the stack\n" + make_contents(
        tpl, 1
    )
    branch_commit = gh.commit.mutation_create_commit_on_branch(
        base_ref.id,
        base_sha,
        "update original",
        additions=[
            gh.commit.Addition(f"mq-qa/{tpl}.txt", contents),
        ],
    )
    print("\nUpdating original branch with new commit")
    print(branch_commit)


if __name__ == "__main__":
    main()
