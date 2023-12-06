import argparse
import random
import time

import gh

parser = argparse.ArgumentParser(
    description=("Create two PRs with a merge conflict."),
)
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


def main():
    args = parser.parse_args()

    conf = gh.config.get_config()
    repo_owner, repo_name = conf["github"]["repo"].split("/")
    repo = gh.repo.get_repo(repo_owner, repo_name)
    print(repo)

    id = str(random.randint(1, 100000))
    file = f"mq-qa/merge-conflict.{id}.txt"
    for n in range(2):
        create_pr(repo, id, n, approve=args.approve, labels=args.label)


def create_pr(
    repo: gh.repo.Repo, id: str, n: int, *, approve=False, labels=None
) -> gh.pr:
    branch_name = f"mq-qa-merge-conflict-{id}-{n}"
    pr_name = f"MQ QA: Merge Conflict: {id}-{n}"

    # create a branch
    branch = gh.ref.mutation_create_branch_ref(repo.id, branch_name, repo.head_sha)
    print(branch)

    # create a commit
    branch_commit = gh.commit.mutation_create_commit_on_branch(
        branch.id,
        repo.head_sha,
        pr_name,
        additions=[
            gh.commit.Addition(f"mq-qa/{id}.merge-conflict.txt", str(time.time())),
        ],
    )
    print(branch_commit)

    # open a pr
    pr = gh.pr.create_pull_request(
        repo.id,
        pr_name,
        repo.base_branch_name,
        branch_name,
    )
    print(pr)

    # approve the pr
    if approve:
        with gh.github.github_account("secondary"):
            approval = gh.pr.add_pull_request_review(pr.id, "APPROVE")
            print(approval)

    # add labels
    if labels:
        label_ids = [repo.resolve_label_id(label) for label in labels]
        gh.pr.add_labels(pr.id, label_ids)

    return pr


if __name__ == "__main__":
    main()
