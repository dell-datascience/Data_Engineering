## Install and setup Gcloud SDK

1. Download Gcloud SDK [from this link](https://cloud.google.com/sdk/docs/install) and install it according to the instructions for your OS.
1. Initialize the SDK [following these instructions](https://cloud.google.com/sdk/docs/quickstart).
    1. Run `gcloud init` from a terminal and follow the instructions.
    1. Make sure that your project is selected with the command `gcloud config list`

## Creating a VM instance

1. From your project's dashboard, go to _Cloud Compute_ > _VM instance_
1. Create a new instance:
    * Manual setup:
        * Any name of your choosing
        * Pick your favourite region. You can check out the regions [in this link](https://cloud.google.com/about/locations).
        * Pick a _E2 series_ instance. A _e2-standard-4_ instance is recommended (4 vCPUs, 16GB RAM)
        * Change the boot disk to _Ubuntu_. The _Ubuntu 20.04 LTS_ version is recommended. Also pick at least 30GB of storage.
        * Leave all other settings on their default value and click on _Create_.
    * Gcloud SDK setup:
        ```sh
        gcloud compute instances create dezoomcamp --zone=europe-west1-b --image-family=ubuntu-2004-lts --image-project=ubuntu-os-cloud --machine-type=e2-standard-4 --boot-disk-size=30GB
        ```
1. When you create an instance, it will be started automatically. You can skip to step 3 of the next section.

## Set up SSH access

1. Start your instance from the _VM instances_ dashboard.
1. In your local terminal, make sure that gcloud SDK is configured for your project. Use `gcloud config list` to list your current config's details.
    1. If you have multiple google accounts but the current config does not match the account you want:
        1. Use `gcloud config configurations list` to see all of the available configs and their associated accounts.
        1. Change to the config you want with `gcloud config configurations activate my-project`
    1. If the config matches your account but points to a different project:
        1. Use `gcloud projects list` to list the projects available to your account (it can take a while to load).
        1. use `gcloud config set project my-project` to change your current config to your project.
3. Set up the SSH connection to your VM instances with `gcloud compute config-ssh`
    * Inside `~/ssh/` a new `config` file should appear with the necessary info to connect.
    * If you did not have a SSH key, a pair of public and private SSH keys will be generated for you.
    * The output of this command will give you the _host name_ of your instance in this format: `instance.zone.project` ; write it down.
4. You should now be able to open a terminal and SSH to your VM instance like this:
   * `ssh instance.zone.project`
5. In VSCode, with the Remote SSH extension, if you run the [command palette](https://code.visualstudio.com/docs/getstarted/userinterface#_command-palette) and look for _Remote-SSH: Connect to Host_ (or alternatively you click on the Remote SSH icon on the bottom left corner and click on _Connect to Host_), your instance should now be listed. Select it to connect to it and work remotely.

### (Optional) Starting your instance with gcloud sdk after you shut it down.

1. List your available instances.
    ```sh
    gcloud compute instances list
    ```
2. Start your instance.
    ```sh
    gcloud compute instances start <instance_name>
    ```
3. Set up ssh so that you don't have to manually change the IP in your config files.
    ```sh
    gcloud compute config-ssh
    ```

## Install stuff

1. Run this first in your SSH session: `sudo apt update && sudo apt -y upgrade`
    * It's a good idea to run this command often, once per day or every few days, to keep your VM up to date.
### Anaconda:
1. In your local browser, go to the [Anaconda download page](https://www.anaconda.com/products/individual), scroll to the bottom, right click on the _64 bit x86 installer_ link under Linux and copy the URL.
    * At the time of writing this gist, the URL is https://repo.anaconda.com/archive/Anaconda3-2021.11-Linux-x86_64.sh
1. In your SSH session, type `wget <anaconda_url>` to download the installer.
1. Find the filename of the installer with `ls`
1. Run the installer with `bash <filename>` (you can start typing the name and then press the Tab key to autocomplete)
1. Follow the on-screen instructions. Anwer `yes` to all _yes/no_ questions and leave all other default values.
1. Log out of your current SSH session with `exit` and log back in. You should now see a `(base)` at the beginning of your command prompt.
1. You may now remove the Anaconda installer with `rm <filename>`
### Docker:
1. Run `sudo apt install docker.io` to install it.
1. Change your settings so that you can run Docker without `sudo`:
    1. Run `sudo groupadd docker`
    1. Run `sudo gpasswd -a $USER docker`
    1. Log out of your SSH session and log back in.
    1. Run `sudo service docker restart`
    1. Test that Docker can run successfully with `docker run hello-world`
### Docker compose:
1. Go to https://github.com/docker/compose/releases and copy the URL for the  `docker-compose-linux-x86_64` binary for its latest version.
    * At the time of writing, the last available version is `v2.2.3` and the URL for it is https://github.com/docker/compose/releases/download/v2.2.3/docker-compose-linux-x86_64
1. Create a folder for binary files for your Linux user:
    1. Create a subfolder `bin` in your home account with `mkdir ~/bin`
    1. Go to the folder with `cd ~/bin`
1. Download the binary file with `wget <compose_url> -O docker-compose`
    * If you forget to add the `-O` option, you can rename the file with `mv <long_filename> docker-compose`
    * Make sure that the `docker-compose` file is in the folder with `ls`
1. Make the binary executable with `chmod +x docker-compose`
    * Check the file with `ls` again; it should now be colored green. You should now be able to run it with `./docker-compose version`
1. Go back to the home folder with `cd ~`
1. Run `nano .bashrc` to modify your path environment variable:
    1. Scroll to the end of the file
    1. Add this line at the end:
        ```bash
        export PATH="${HOME}/bin:${PATH}"
        ```
    1. Press `CTRL` + `o` in your keyboard and press Enter afterwards to save the file.
    1. Press `CTRL` + `x` in your keyboard to exit the Nano editor.
1. Reload the path environment variable with `source .bashrc`
1. You should now be able to run Docker compose from anywhere; test it with `docker-compose version`
### Terraform:
1. Run `curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -`
1. Run `sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"`
1. Run `sudo apt-get update && sudo apt-get install terraform`

## Upload/download files to/from your instance

1. Download a file.
    ```sh
    # From your local machine
    scp <instance_name>:path/to/remote/file path/to/local/file
    ```

1. Upload a file.
    ```sh
    # From your local machine
    scp path/to/local/file <instance_name>:path/to/remote/file
    ```

1. You can also drag & drop stuff in VSCode with the remote extension.

1. If you use a client like Cyberduck, you can connect with SFTP to your instance using the `instance.zone.project` name as server, and adding the generated private ssh key.