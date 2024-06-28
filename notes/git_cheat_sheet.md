# Basic git

1. Make sure your local copy of the selected branch is updated.
   1. Without overwriting anything
      - `git fetch`
   1. If you already fetched or you are ready to overwrite your local copy, then pull
      - `git pull`
1. Check your repo branches
   1. Local branches
      - `git branch`
   1. All branches on remote repo
      - `git branch -r`
   1. Both local and remote branches
      - `git branch -a`
   1. You can also add `-v` to make the commands explicitly verbose
1. Create a branch and access it
   1. Normal way
      1. `git branch new_branch`
      2. (2 ways)
         -  `git checkout new_branch`
         -  `git switch new_branch`  > Recommended option (avoid `checkout` unless necessary)
   2. Shortcut (2 ways)
      - `git checkout -b new_branch`
      - `git switch -c new_branch` > Recommended option (avoid `checkout` unless necessary)
1. Get some work done lol
1. Check the status of your work
   - `git status`
1. Did you mess up editing a file and want to restore it to how it was beforehand?
   - `git restore changed_file.txt`
1. Add changes to staging in order to prepare your commit
   1. Add a single file
      - `git add new_file.txt`
   2. Add all changed files
      - `git add . -p`
1. Did you screw up? Reset the staging
   - `git reset`
1. Commit
   - `git commit -m "This is a commit message"`
1. Check the commit history of the branch you're in
   - `git log`
   - If you wanna see some cool things with log, you can use something like this:
      - `git log --graph --oneline --all`
1. Make sure you upload your commits to the remote repo! If your local branch is brand new, you must add it to the remote repo.
    1. New branch
       - `git push -u origin new_branch`
    2. Previously existing branch
       - `git push`
1. Move to another branch
    - `git checkout another_branch`
1. Merge some branch into your current branch (assuming default behavior of pull is merge)
    - `git pull branch_that_will_be_merged_into_current_branch`

For more info check the [GitHub Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)

## Checkout vs Switch

`checkout` can be used to switch branches and/or restore working tree files, which means that you can do things like undo/restore commmits and overwrite local changes, or detach the HEAD (navigating a commit which is not the latest on its branch).

`switch` is only used for switching and creating branches. It cannot discard changes to tracked files: if you've changed a tracked file and want to switch branches, you'll need to stash or commit the changes.

# Advanced git

The following are some best practices that may be useful, taken from [this blog post](https://mislav.net/2013/02/merge-vs-rebase/), as well as [this tip](https://stackoverflow.com/questions/501407/is-there-a-git-merge-dry-run-option).

1. While working on a branch, if you need to pull commits from the remote repo to your local repo, use rebase instead of merge to reduce the amount of commits
   - `git pull --rebase`
   - If you want to make rebasing the default behavior when doing `git pull`, do so with `git config --global --bool pull.rebase true`
1. Before pushing your changes to the remote repo, perform basic housekeeping (squash related commits together, rewording messages, etc)
   - `git rebase -i @{u}`
1. Make sure that you've fetched all changes from the remote repo
   - `git fetch`
1. Simulate a merge to see any possible conflicts:
   1. Do a merge with the `--no-commit` flag from the work branch.
      - `get merge --no-commit --no-ff $GOOD_BRANCH`
   3. Examine the staged changes
      - `git diff --cached`
   4. Undo the merge
      - `git merge --abort`
3. Merge (do not rebase) changes from master/main into your branch, in order to update the branch with the latest features and solve any compatibility issues and/or conflicts
   1. `git merge main`
   2. `git pull --merge main`
4. Enforce merge commit when merging feature branch into main, even if a merge commit isn't necessary (check next point for exception), in order to make it easier to see the where and when of changes. Assuming you're in main:
   - `git merge --no-ff branch_that_will_be_merged_into_main`
5. Exception to point 4: if you only need to merge a single commit (typical for stuff such as bugfixes). Assuming you're in main:
   - `git cherry-pick branch_that_only_has_a_single_commit`
6. Delete merged branch:
   1. Delete locally 
      - `git branch -d branch_that_has_been_merged`
   1. Delete on remote repo
      - `git push origin :branch_that_has_been_merged`

# Create a remote repo (local folder as remote repo)

## Official method

_[Source](https://git-scm.com/book/en/v2/Git-on-the-Server-Getting-Git-on-a-Server)_

1. Make sure you've got a local commit. You may initialize a local repo with `git init` on any project folder and making sure that it has at least one commit, or you may use an already existing local repo.
2. On a separate folder, run:
   ```bash
   git clone --bare path/to/local/project project.git
   ```
   * This will create a folder with name `project.git` on the folder you're running the command.
   * Remote repo folders use the `.git` extension as a standard.
   * This folder is a ***bare*** repository. It does not contain a working folder, only the git files.
3. Move the `project.git` folder to the final destination. Ideally, a shared folder such as a networked drive that everyone has access to "locally".
   * You may combine steps 2 and 3 by creating the bare repo directly on the final folder.
4. You should now be able to clone the repo:
   ```bash
   git clone path/to/remote/repo/project.git
   ```
5. The original repo that we bare-cloned does not have an origin repo to push to. If you want to keep using it, set up a remote like this:
   ```bash
   git remote add origin path/to/remote/repo/project.git
   ```

## Alternative method

_[Source](https://stackoverflow.com/questions/14087667/create-a-remote-git-repo-from-local-folder)_

1. On remote folder:
   ```bash
   mkdir my_repo
   cd my_repo
   git init --bare
   ```
2. On local folder:
   ```bash
   cd my_repo
   git init
   git remote add origin ssh://myserver/my_repo
   git add .
   git commit -m "Initial commit"
   git push -u origin master
   ```