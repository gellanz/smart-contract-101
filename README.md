# smart-contract-101

Four-stage house buy/sell transaction registry (buyer initiation, notary verification, government tax check, property transfer) on the Avalanche blockchain using Python

## How the Contract Works
1. Buyer Initiation (initiateSale):
    The buyer calls initiateSale, providing the property ID, seller, notary, and government addresses, and the sale price.

    The buyer deposits the full sale price (in AVAX) into the contract.

    An ERC-721 NFT is minted to the seller, representing the property title.

    The sale is recorded with stage Initiated.

2. Notary Verification (verifyNotary):
    The notary calls verifyNotary to confirm legal documents (e.g., title, permits) are valid.

    Only the designated notary can call this function, and only at the Initiated stage.

    The stage updates to NotaryVerified.

3. Government Tax Check (verifyTaxes):
    The government authority calls verifyTaxes, specifying the tax amount (e.g., based on sale price or local laws).

    Only the designated government address can call this, and only at the NotaryVerified stage.

    The stage updates to TaxVerified.

4. Property Transfer (completeSale):
    The buyer calls completeSale to finalize the transaction.

    Only the buyer can call this, and only at the TaxVerified stage.

5. The contract:
    Sends the sale price (minus taxes) to the seller.

    Sends the tax amount to the government.

    Transfers the property NFT to the buyer.

    The stage updates to Completed.



## node
```
curl -fsSL https://deb.nodesource.com/setup_23.x -o nodesource_setup.sh
sudo -E bash nodesource_setup.sh
sudo apt-get install -y nodejs
npm install @openzeppelin/contracts
```
## python
```
pip install web3 py-solc-x
pip install solc-select
solc-select install 0.8.20
solc-select use 0.8.20
```
