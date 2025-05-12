// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract PropertySale is ERC721, Ownable, ReentrancyGuard {
    enum SaleStage { Initiated, NotaryVerified, TaxVerified, Completed }
    struct Sale {
        address buyer;
        address seller;
        address notary;
        address government;
        uint256 price;
        uint256 taxAmount;
        uint256 propertyId;
        SaleStage stage;
        bool fundsDeposited;
    }

    mapping(uint256 => Sale) public sales;
    mapping(uint256 => bool) public propertyMinted;

    event SaleInitiated(uint256 indexed propertyId, address buyer, address seller, uint256 price);
    event NotaryVerified(uint256 indexed propertyId, address notary);
    event TaxVerified(uint256 indexed propertyId, address government, uint256 taxAmount);
    event SaleCompleted(uint256 indexed propertyId, address buyer, address seller);

    modifier onlyBuyer(uint256 propertyId) {
        require(msg.sender == sales[propertyId].buyer, "Only buyer can call");
        _;
    }
    modifier onlyNotary(uint256 propertyId) {
        require(msg.sender == sales[propertyId].notary, "Only notary can call");
        _;
    }
    modifier onlyGovernment(uint256 propertyId) {
        require(msg.sender == sales[propertyId].government, "Only government can call");
        _;
    }
    modifier atStage(uint256 propertyId, SaleStage stage) {
        require(sales[propertyId].stage == stage, "Incorrect stage");
        _;
    }

    constructor() ERC721("PropertyTitle", "PTT") Ownable(msg.sender) {}

    function initiateSale(
        uint256 propertyId,
        address seller,
        address notary,
        address government,
        uint256 price
    ) external payable nonReentrant {
        require(!propertyMinted[propertyId], "Property already registered");
        require(msg.value >= price, "Insufficient funds deposited");

        _mint(seller, propertyId);
        propertyMinted[propertyId] = true;

        sales[propertyId] = Sale({
            buyer: msg.sender,
            seller: seller,
            notary: notary,
            government: government,
            price: price,
            taxAmount: 0,
            propertyId: propertyId,
            stage: SaleStage.Initiated,
            fundsDeposited: true
        });

        emit SaleInitiated(propertyId, msg.sender, seller, price);
    }

    function verifyNotary(uint256 propertyId)
        external
        onlyNotary(propertyId)
        atStage(propertyId, SaleStage.Initiated)
        nonReentrant
    {
        sales[propertyId].stage = SaleStage.NotaryVerified;
        emit NotaryVerified(propertyId, msg.sender);
    }

    function verifyTaxes(uint256 propertyId, uint256 taxAmount)
        external
        onlyGovernment(propertyId)
        atStage(propertyId, SaleStage.NotaryVerified)
        nonReentrant
    {
        sales[propertyId].taxAmount = taxAmount;
        sales[propertyId].stage = SaleStage.TaxVerified;
        emit TaxVerified(propertyId, msg.sender, taxAmount);
    }

    function completeSale(uint256 propertyId)
        external
        onlyBuyer(propertyId)
        atStage(propertyId, SaleStage.TaxVerified)
        nonReentrant
    {
        Sale storage sale = sales[propertyId];
        uint256 sellerAmount = sale.price - sale.taxAmount;
        (bool sentToSeller, ) = sale.seller.call{value: sellerAmount}("");
        require(sentToSeller, "Failed to send funds to seller");

        if (sale.taxAmount > 0) {
            (bool sentToGovernment, ) = sale.government.call{value: sale.taxAmount}("");
            require(sentToGovernment, "Failed to send taxes to government");
        }

        _transfer(sale.seller, sale.buyer, propertyId);
        sale.stage = SaleStage.Completed;
        emit SaleCompleted(propertyId, sale.buyer, sale.seller);
    }

    function withdrawFunds() external onlyOwner {
        uint256 balance = address(this).balance;
        (bool sent, ) = owner().call{value: balance}("");
        require(sent, "Failed to withdraw funds");
    }

    function getContractBalance() external view returns (uint256) {
        return address(this).balance;
    }
}