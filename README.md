### peoplesoft-verkada-integration

# All instructions below are supported on the MacOSX.

## Download the Code

Download the code from the repository: https://github.com/nyeddana22/psoft-command-integration

## Install python3 using Homebrew

If you don't have python3 installed on your system already, please follow the below instructions:

1. To install Homebrew, open Terminal or your favorite OS X terminal emulator and run

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
```

The script will explain what changes it will make and prompt you before the installation begins. Once you’ve installed Homebrew, insert the Homebrew directory at the top of your PATH environment variable. You can do this by adding the following line at the bottom of your ~/.profile file

```
export PATH="/usr/local/opt/python/libexec/bin:$PATH"
```

2. Install Python 3:

```
brew install python
```

## Set up a virtual environment

1. Navigate to the directory that contains the code by running

```
cd /path/to/your/project/
```

2. Create a virtual environment named venv:

```
python3 -m venv venv
```

This creates a folder named venv inside your project directory.
Inside this folder, it sets up a lightweight virtual Python environment with its own python and pip.

3. Activate your virtual environment

```
source venv/bin/activate
```

## Install Dependencies

Once you are inside the /venv folder that contains all the scripts, run:

```
pip install -r requirements.txt
```

## Set up your .env file to store your long-lived API token

1. Generate an API token from Command using this link: https://command.verkada.com/admin/org-settings/verkada-api

2. In order to securely store your long-lived API token such that the main script does not contain plain text API keys, you will need to create a .env file in the root directory of your project.

In the root directory of your project, create a file named .env. This file will contain your API key generated from Command in the following format:

```
EXTENDED_API_TOKEN="your_api_key_here"
```

This file is already added to .gitignore which will ensure your keys will remain local to your system.

## Create a launchctl file to schedule the script to run every 10 minutes

1. Create a plist file for launchd: launchd jobs are defined in Property List (plist) files. Create a plist file in the ~/Library/LaunchAgents/ directory by running the following command:

```
vim ~/Library/LaunchAgents/com.verkada.api.plist
```

2. Copy and paste the below configuration lines to the file, replacing all the values within the <string> tags with the actual paths to your Python script and virtual environment.

```
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>com.verkada.api</string>

    <key>ProgramArguments</key>
    <array>
     <string>/path/to/python3.13/in/your/venv</string>
     <string>/path/to/the/userSync.py/file/in/your/venv</string>
    </array>

    <key>WorkingDirectory</key>
    <string>/directory/to/your/project</string>

    <key>StartInterval</key>
    <integer>600</integer>

    <key>StandardOutPath</key>
    <string>/directory/to/store/output_logging/of/this/plist/file</string>

    <key>StandardErrorPath</key>
    <string>/directory/to/store/error_logging/of/this/plist/file/string>
  </dict>
</plist>
```

3. Load the plist file

```
launchctl load ~/Library/LaunchAgents/com.verkada.api.plist
```

4. Verify that the task is running

```
launchctl list | grep com.verkada.api
```

5. Monitor the log files for any errors in excecution. If there are no errors, you should see the running log of the script update periodically with every update.
