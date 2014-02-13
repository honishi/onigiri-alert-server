Onigiri Alert Server
==

sequence
--
![sequence](./document/sequence.png)

setup
--
````
pyenv install 3.3.3
pyenv virtualenv 3.3.3 onigirialert-venv-3.3.3
pip install -r requirements.txt
````

monitoring example using cron
--
````
* * * * * /home/honishi/project/prod/OnigiriAlert-server/onigiri.sh monitor >> /home/honishi/project/prod/OnigiriAlert-server/log/monitor.log 2>&1
````
