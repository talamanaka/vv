 apt-get update && apt-get install docker.io python-pip python-minimal  -y
pip install pwn 
wget https://raw.githubusercontent.com/skysider/VulnPOC/292f00da0ddbd2fa20384714660ff9ece53c426a/CVE-2018-6789/exp.py
wget https://raw.githubusercontent.com/skysider/VulnPOC/292f00da0ddbd2fa20384714660ff9ece53c426a/CVE-2018-6789/Environment/conf.conf
wget https://raw.githubusercontent.com/skysider/VulnPOC/292f00da0ddbd2fa20384714660ff9ece53c426a/CVE-2018-6789/Environment/Dockerfile
wget https://raw.githubusercontent.com/talamanaka/vv/master/e.py

echo "docker run -it --name exim -p 25:25 skysider/vulndocker:cve-2018-6789"
