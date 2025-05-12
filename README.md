# smart-contract-101

## node
curl -fsSL https://deb.nodesource.com/setup_23.x -o nodesource_setup.sh
sudo -E bash nodesource_setup.sh
sudo apt-get install -y nodejs
npm install @openzeppelin/contracts

## python
pip install web3 py-solc-x
pip install solc-select
solc-select install 0.8.20
solc-select use 0.8.20

