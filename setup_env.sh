sudo apt update -y
sudo apt install software-properties-common -y
sudo add-apt-repository --yes --update ppa:ansible/ansible
sudo apt install ansible -y
sudo apt install openssh-server openssh-client -y
sudo apt install sshpass -y
sudo apt install git -y
sudo apt install mysql-server mysql-client -y
sudo apt install net-tools -y
sudo apt install python3-pip -y
git clone https://github.com/gattem/copybot.git
cd copybot
pip install -r requirements.txt 
