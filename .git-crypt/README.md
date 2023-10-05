# git-crypt

This repository uses [`git-crypt`](https://github.com/AGWA/git-crypt) to encrypt secrets.

## Install git-crypt

To install `git-crypt` with `brew` run:

    brew install git-crypt

## Generate a GPG key

To generate a GPG key, follow the [GitHub guidance](https://help.github.com/en/github/authenticating-to-github/generating-a-new-gpg-key#generating-a-gpg-key). Select the following parameters where prompted:

- key type: RSA-RSA
- key size: 4096
- key valid for: choose an appropriate non-infinite (0) expiry time
- create a passphrase

Note the email address associated with your github account is the one used to identify your key. 

## Add the GPG key to the repository

You must ask a user that already has access to add your GPG key to the repository.

To add a GPG key for another user to the repository:

1.  Ask the user to export their GPG public key:
    ```
    gpg --armor --export <email-address>
    ```

2.  Ask the user to save the file locally, for example, `/tmp/firstname.asc` and send this file to you. As this is the **public key** it is OK to send via email attachment, but please double check they are sending the public key only! The private key should stay on the user's machine.

3.  Import the key into your GPG Keychain:
    ```
    gpg --import /tmp/firstname.asc
    ```
    Alternatively, if you double click to open the `.asc` file it will automatically import to your GPG Keychain.

4.  Tell GPG that you trust the key. Enter the parameters to select the level of trust (`4: full`) and sign it:

        gpg --edit-key <email-address> trust
            # 4
            # save
            # quit
        gpg --edit-key <email-address> sign
            # you will need to type your own passphrase
            # save

5.  Confirm that `[ full ]` is shown when you list the key:

    ```
    gpg --list-keys <email-address>
    ```
    or list all keys

    ```
    gpg --list-keys
    ```
    Example expected output:

    ```
        pub rsa4096 2015-02-05 [SC]
        17818CFB47FFFC384F0CC
        uid [ full ] firstname <email-address>
        sub rsa4096 2015-02-05 [E]
    ```

6.  In this repository, create a new branch and add the key to the .git-crypt directory:

    ```
    cd data-engineering-support-rota
    git checkout -b <branch-name>
    git-crypt add-gpg-user <email-address>
    ```
    This will automatically add a new `.gpg` file under `git-crypt/keys/default/0`, for example, `50934997E3CFF98E3F0E8765C1606EC98B636725.gpg`.

7.  The change is added and committed automatically, so you just have to push the changes to GitHub:
    ```
    git push origin <branch-name>
    ```

8.  Merge your branch into develop and main as usual.

## Decrypt the repository

To decrypt the repository after your GPG has been added run:
    ```
    git pull
    git-crypt unlock
    ```
You should now be able to locally view the encrypted files, for example, `data_engineering_support_rota/data_engineering_support_rota_creds.json`.
## Merge conficts

If you get merge conflicts on files encrypted with git-crypt, by default you will not be able to see the conflicts. You can fix this behaviour by specifying this custom merge driver in your `.git/config`:

```
    [merge "git-crypt"]
        name = A custom merge driver used to merge git-crypted files.
        driver = ./gitcrypt-merge-tool.sh %O %A %B
        recursive = binary
```

See also the relevant [git-crypt issue](https://github.com/AGWA/git-crypt/issues/140#issuecomment-361031719).

When resolving conflicts you may find it useful to use `git mergetool`.
