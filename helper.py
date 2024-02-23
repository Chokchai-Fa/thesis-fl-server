import git

def git_clone(git_repo_url: str, repo_path: str):
        repo_url = git_repo_url
        repo = git.Repo.clone_from(repo_url, repo_path)
        return repo

def git_push(branch_name: str, file: str, repo: str, commit_message: str):
    if branch_name not in repo.git.branch():
        repo.git.branch(branch_name)

    repo.git.checkout(branch_name)
    repo.git.add(file)
    repo.git.commit('-m', commit_message)
    repo.git.push('origin', branch_name)
    return print("Push file successfully")
   