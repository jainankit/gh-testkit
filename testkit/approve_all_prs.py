import argparse

import gh

parser = argparse.ArgumentParser(description="Approve all open PRs.")


def main():
    args = parser.parse_args()

    config = gh.config.get_config()
    owner, name = config["github"]["repo"].split("/")
    repo = gh.repo.get_repo(owner, name)
    print(repo)

    # Get all open PRs
    prs = gh.pr.list_repo_pull_requests(repo.id, states=["OPEN"])
    print(f"Found {len(prs)} open PRs")

    # Approve all PRs
    with gh.github.github_account("secondary"):
        for pr in prs:
            review = gh.pr.add_pull_request_review(pr.id)
            print(review)


if __name__ == "__main__":
    main()
