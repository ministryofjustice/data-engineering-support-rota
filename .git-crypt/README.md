# git-crypt

This repository uses [`git-crypt`](https://github.com/AGWA/git-crypt) to encrypt secrets.

## Install git-crypt

To install `git-crypt` with `brew` run:

    brew install git-crypt

## Generate a GPG key

To generate a GPG key, follow the [GitHub guidance](https://help.github.com/en/github/authenticating-to-github/generating-a-new-gpg-key#generating-a-gpg-key).

## Add the GPG key to the repository

You must ask a user that already has access to add your GPG key to the repository.

To add a GPG key for another user to the repository:

1.  Ask the user to export their GPG public key:

        gpg --armor --export firstname.lastname@justice.gov.uk

2.  Save the file locally, for example, `/tmp/firstname.asc`.
3.  Import the key into your GPG keyring:

        gpg --import /tmp/firstname.asc

4.  Tell GPG that you trust the key and sign it:

        gpg --edit-key "firstname.lastname@justice.gov.uk" trust
            # 4
            # save
            # quit
        gpg --edit-key "firstname.lastname@justice.gov.uk" sign
            # you will need to type your own passphrase
            # save

5.  Confirm that `[ full ]` is shown when you list the key:

    gpg --list-keys
    pub rsa4096 2015-02-05 [SC]
    17818CFB47FFFC384F0CC
    uid [ full ] firstname <firstname.lastname@justice.gov.uk>
    sub rsa4096 2015-02-05 [E]

6.  In this repository, create a new branch and add the key to the .git-crypt directory:

    cd analytical-platform-data-engineering
    git checkout -b branch-name develop
    git-crypt add-gpg-user firstname.lastname@justice.gov.uk

7.  The change is committed automatically, so you just have to push the changes to GitHub:

    git push origin branch-name

8.  Merge your branch into develop and main as usual.

## Decrypt the repository

To decrypt the repository after your GPG has been added run:

    git pull
    git-crypt unlock

## Merge conficts

If you get merge conflicts on files encrypted with git-crypt, by default you will not be able to see the conflicts. You can fix this behaviour by specifying this custom merge driver in your `.git/config`:

    [merge "git-crypt"]
        name = A custom merge driver used to merge git-crypted files.
        driver = ./gitcrypt-merge-tool.sh %O %A %B
        recursive = binary

See also the relevant [git-crypt issue](https://github.com/AGWA/git-crypt/issues/140#issuecomment-361031719).

When resolving conflicts you may find it useful to use `git mergetool`.
