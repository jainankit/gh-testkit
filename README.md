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

# End to end tests

## Overview

The end to end tests are written in a way to use Github API that are completely
independent of our main source code, to perform actions on a Github repository
and then measure results. Currently it is built to only work for staging
environment, but this can simply work with any environment that has a connected
MergeQueue Github app and runs the background fetch jobs.

Note: Running these tests will change your repo config on staging.

## How to run

The code for tests lives in `mergeit` directory under `testkit/tests`. There are
some prerequisites to run the tests:

- Setup your own Github repository to work in staging.mergequeue.com
- Setup the `config.json` file as described above.
- Have a local env variable set for `SQL_STAGING` pointing to the staging DB.
  Please ask @jainankit for this url.
- If you are having trouble connecting to the staging DB, make sure you do not
  have the `SQLALCHEMY_DATABASE_URI` set in your `local_overrides.py`.
- In the `testkit/` directory, create an empty pem file:

```jsx
touch mqdev-1.pem
```

- Make sure you have a label named `mq-ready` in your GH repository.
- Have virtualenv enabled for the main application:

```jsx
source venv/bin/activate
```

Then run the tests:

```jsx
./run_tests.py
```
