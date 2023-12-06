# Tools for testing MergeQueue against GitHub

## Setup

You'll need a GitHub repo and two GitHub accounts with write access to that
repo. Create a
[GitHub personal access token](https://github.com/settings/tokens) for each
account.

Copy the `config.sample.json` file to `config.json` and edit the fields:

- `github.repo` -- the name of the GitHub repository to test with (in the form
  `<owner>/<name>`).
- `github.primaryToken` -- a personal access token for the primary account (used
  to create PRs)
- `github.secondaryToken` -- a personal access token for the secondary account
  (used to approve PRs)

# Usage
Each script has it's own purpose, and are named accordingly. For instance to create
a PR, run the following command from `testkit` directory:

```jsx
> python ./new_pr.py
```
This will create a new PR with a single commit in the directory named `mq-qa`. You
can also check the usage for each script using the `--help` param:
```jsx
> python ./new_pr.py --help
usage: new_pr.py [-h] [-a] [-l LABEL] [-c COUNT] [-b BASE_BRANCH] [--n-commits N_COMMITS] [--title TITLE]

optional arguments:
  -h, --help            show this help message and exit
  -a, --approve         Approve the PR using the secondary account credentials.
  -l LABEL, --label LABEL
                        Add a label to the PR. Can be specified multiple times.
  -c COUNT, --count COUNT
                        The number of PRs to create. Defaults to 1.
  -b BASE_BRANCH, --base-branch BASE_BRANCH
                        The base branch for the PR to target. Defaults to the base branch of the repository.
  --n-commits N_COMMITS
                        The number of commits to add to each PR branch.
  --title TITLE         The title of the pull request.
```

## All commands:
- `approve_all_prs.py` - approve all open PRs
- `close_all_prs.py` - close all open PRs
- `create_merge_conflict.py` - create two PRs that conflict with each other
- `create_stacked_prs.py` - create two or more PRs stacked on top of each other
- `delete_branches.py` - delete all branches with `mq-qa-` prefix
- `generate_fake_tests.py` - generate fake tests
- `label_pr.py` - add a label to the specified PR
- `new_pr.py` - create a new PR
