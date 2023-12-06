import argparse

import gh

parser = argparse.ArgumentParser(description="Close all open PRs.")
parser.add_argument(
    "-d",
    "--delete-branch",
    action="store_true",
    help="Delete the branch after closing the PR.",
)


def main():
    args = parser.parse_args()

    config = gh.config.get_config()
    owner, name = config["github"]["repo"].split("/")
    repo = gh.repo.get_repo(owner, name)
    print(repo)
    close_all(repo, args.delete_branch)


def close_all(repo: "gh.repo.Repo", delete_branch: bool):
    # Get all open PRs
    prs = gh.pr.list_repo_pull_requests(repo.id, states=["OPEN"])

    # Close all PRs
    for pr in prs:
        pr = gh.pr.close_pull_request(pr.id)
        print(pr)
        if delete_branch:
            gh.ref.mutation_delete_ref(pr.head_ref.id)
            print(pr.head_ref)


if __name__ == "__main__":
    main()
