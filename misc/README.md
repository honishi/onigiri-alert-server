provisioning procedure
--
````
curl -s https://www.parse.com/downloads/cloud_code/installer.sh | sudo /bin/bash
parse new website
cd website
parse deploy
````
note: it seems `parse new` command does not support python 3, so use python 2 as indicated in file `python-version`.
