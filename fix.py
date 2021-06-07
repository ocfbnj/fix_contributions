import re
import os
import requests
import pathlib

from typing import List


def get_repos(username: str) -> List[str]:
    url = f"https://github.com/{username}?tab=repositories"
    pattern = r'<a href="\/ocfbnj\/(.*)" itemprop="name codeRepository" >'
    data = requests.get(url).text

    return re.findall(pattern, data)


def clone_to(path: str, repos: List[str]):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    os.chdir(path)

    for repo in repos:
        print(f"-> clone {repo} to {path}")
        os.popen(f"git clone https://github.com/ocfbnj/{repo}.git").read()


def change_author(wrong_email: str, new_name: str, new_email: str, repos: List[str], path: str):
    if not os.path.exists(path):
        print(f"-> {path} not exists!")
        exit(1)

    cmd = f"""
git filter-branch --env-filter '
WRONG_EMAIL="{wrong_email}"
NEW_NAME="{new_name}"
NEW_EMAIL="{new_email}"

if [ "$GIT_COMMITTER_EMAIL" = "$WRONG_EMAIL" ]
then
    export GIT_COMMITTER_NAME="$NEW_NAME"
    export GIT_COMMITTER_EMAIL="$NEW_EMAIL"
fi
if [ "$GIT_AUTHOR_EMAIL" = "$WRONG_EMAIL" ]
then
    export GIT_AUTHOR_NAME="$NEW_NAME"
    export GIT_AUTHOR_EMAIL="$NEW_EMAIL"
fi
' --tag-name-filter cat -- --branches --tags
"""

    for repo in repos:
        os.chdir(f"{path}/{repo}")
        print(f"-> change author for {repo}")

        # change author
        os.popen(cmd).read()


def push_all(repos: List[str], path: str):
    if not os.path.exists(path):
        print(f"-> {path} not exists!")
        exit(1)

    for repo in repos:
        os.chdir(f"{path}/{repo}")
        print(f"-> commit {repo}")

        os.popen("git push -f").read()


if __name__ == "__main__":
    repos = get_repos("ocfbnj")
    clone_to("/home/ocfbnj/work_space/temp_work", repos)
    change_author("1391195421@qq.com", "ocfbnj", "ocfbnj@qq.com",
                  repos, "/home/ocfbnj/work_space/temp_work")
    push_all(repos, "/home/ocfbnj/work_space/temp_work")
