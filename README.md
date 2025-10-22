# RO11_Akinator_Robotic_Project

need to install pynaoqi-python2.7-2.8.6.23-linux64-20191127_152327.tar.gz on https://aldebaran.com/en/support/kb/nao6/downloads/nao6-software-downloads

Deployed version :         
docker-compose up --build  

Simulated version :          
docker-compose -f docker-compose_no_mic_version.yml up --build        

In this version there is no mic so open another terminal and connect to the naoqi server to send the answer after launching the docker-compose file :      
docker attach naoqi_bridge