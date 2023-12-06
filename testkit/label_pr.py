import argparse

import gh

parser = argparse.ArgumentParser(description="Apply label(s) to PRs")
parser.add_argument(
    "-l",
    "--label",
    action="append",
    help="Label(s) to apply",
)
parser.add_argument(
    "--remove",
    action="append",
    help="Label(s) to remove",
)
parser.add_argument(
    "--relabel",
    action="store_true",
    help="Remove label(s) if they're added then re-add them.",
)
parser.add_argument(
    "target",
    nargs="*",
    help="Target PR",
)


def main():
    args = parser.parse_args()

    if not args.target:
        raise ValueError("No target PRs specified")

    config = gh.config.get_config()
    owner, name = config["github"]["repo"].split("/")
    repo = gh.repo.get_repo(owner, name)
    print(repo)

    for target in args.target:
        pr = gh.pr.get_repo_pull_request(repo.id, int(target))
        print(pr)

        to_remove = args.remove
        if args.relabel:
            to_remove.extend(args.label)
        if to_remove:
            gh.pr.remove_labels(
                pr.id, [repo.resolve_label_id(label) for label in to_remove]
            )

        if args.label:
            gh.pr.add_labels(
                pr.id, [repo.resolve_label_id(label) for label in args.label]
            )


if __name__ == "__main__":
    main()
