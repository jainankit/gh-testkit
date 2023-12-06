import argparse
import random
import time

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
    default=1,
    help=("The number of PRs to create. Defaults to 1."),
)
parser.add_argument(
    "-b",
    "--base-branch",
    help=(
        "The base branch for the PR to target. "
        "Defaults to the base branch of the repository."
    ),
)
parser.add_argument(
    "--n-commits",
    type=int,
    default=1,
    help=("The number of commits to add to each PR branch. "),
)
parser.add_argument(
    "--title",
    help="The title of the pull request.",
)


def main():
    args = parser.parse_args()

    conf = gh.config.get_config()
    repo_owner, repo_name = conf["github"]["repo"].split("/")
    repo = gh.repo.get_repo(repo_owner, repo_name)
    print(repo)

    mqid = random.randint(1, 100000)
    for n in range(args.count):
        print("\n\nCreating PR #{}/{}".format(n + 1, args.count))
        create_new_pr(repo, f"mq-qa-{mqid}-{n+1}", args)


def create_new_pr(repo: "gh.repo.Repo", branch_name: str, args):
    pr_title = f"{branch_name}"
    if args.title:
        pr_title += f": {args.title}"

    # create a branch
    branch = gh.ref.mutation_create_branch_ref(repo.id, branch_name, repo.head_sha)
    print(branch)

    # create a commit
    head_sha = repo.head_sha
    for n in range(args.n_commits):
        commit_headline = pr_title if args.n_commits == 1 else f"{pr_title} [{n+1}]"
        file_name = (
            f"mq-qa/{branch_name}-{n+1}.txt"
            if args.n_commits > 1
            else f"mq-qa/{branch_name}.txt"
        )
        branch_commit = gh.commit.mutation_create_commit_on_branch(
            branch.id,
            head_sha,
            commit_headline,
            additions=[
                gh.commit.Addition(file_name, str(time.time())),
            ],
        )
        print(branch_commit)
        head_sha = branch_commit.sha

    # open a pr
    base_branch = args.base_branch or repo.base_branch_name
    pr = gh.pr.create_pull_request(
        repo.id,
        pr_title,
        base_branch,
        branch_name,
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
    return pr


if __name__ == "__main__":
    main()
