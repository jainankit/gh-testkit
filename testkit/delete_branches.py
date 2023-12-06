import argparse

import gh

parser = argparse.ArgumentParser(
    description=(
        "Delete all mq-qa-xxx branches. "
        "This will close any PRs that are based on or which target any branch "
        "that is deleted."
    ),
)


def main():
    config = gh.config.get_config()
    owner, name = config["github"]["repo"].split("/")
    repo = gh.repo.get_repo(owner, name)
    print(repo)

    branch_refs = gh.ref.query_list_refs(repo.id, "mq-qa-", ref_prefix="refs/heads/")
    for branch_ref in branch_refs:
        print(branch_ref)
        gh.ref.mutation_delete_ref(branch_ref.id)


if __name__ == "__main__":
    main()
