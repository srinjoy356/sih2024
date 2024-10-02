
import React, { useState, useEffect,useContext,createContext } from "react";
import { ethers } from 'ethers'; // ethers v6
import axios from 'axios';
import CardTransactionRegistry from "./CardTransactionRegistry.json"; // Import your ABI JSON
import SideWhole from "../SideWhole";
import SideManu from "../SideManu";
import DashManu from "../home/DashboardManu";
import './Shipment.css'; // Import the CSS file

import contractConfig from './contractAddress.json';



export default function Dashboard() {
  
  const [walletAddress, setWalletAddress] = useState(null);// for storing connected wallet addresss
  const [contract, setContract] = useState(null);
  const [formInput, setFormInput] = useState({
    cardId: "",
    receiverAddressW: "",
    receiverAddressR: "",
    date: "",
    distance: "",
    pricePerUnit: "",
    
  });
  const [errorMessage, setErrorMessage] = useState(""); // For showing errors related to transactions
  
   const [allTransactions, setAllTransactions] = useState([]); // State to store all transactions


  const contractAddress = contractConfig.address; /// your contract address

  
  useEffect(() => {
    const init = async () => {
      await loadContract();
    };
    init();
  }, []);

  useEffect(() => {
    if (contract) {
      fetchAllTransactions(); // Call this only after the contract is set
    }
  }, [contract]); // Adding contropact as a dependency

  const loadContract = async () => {
    if (typeof window.ethereum !== "undefined") {
      const accounts = await window.ethereum.request({ method: "eth_requestAccounts" });
      setWalletAddress(accounts[0]); // Store the first account (the connected wallet)
      
      const provider = new ethers.BrowserProvider(window.ethereum);
      const signer = await provider.getSigner();
      const cardTransactionRegistry = new ethers.Contract(
        contractAddress,
        CardTransactionRegistry.abi,
        signer
      );
      setContract(cardTransactionRegistry);
    }
  };
   

   // Function to register a new card transaction
   const registerCardTransaction = async () => {
    if (contract) {
      const { cardId, receiverAddressW,receiverAddressR, date, distance, pricePerUnit } = formInput;
      try {
        setErrorMessage(""); // Clear any previous error messages
        const transaction = await contract.registerCardTransaction(
          cardId,
          walletAddress,
          receiverAddressR,
          date,
          distance,
          pricePerUnit
        );
        await transaction.wait(); // Wait for the transaction to be mined
        setFormInput({ cardId: "", receiverAddressW: "",receiverAddressR: "", date: "", distance: "", pricePerUnit: "" });
        fetchAllTransactions(); // Refresh the all transactions list after registering
      } catch (error) {
        const errorMsg = error.message || JSON.stringify(error);
        if (errorMsg.includes("Transaction with this card ID already exists")) {
          setErrorMessage("Transaction with this card ID already exists!"); // Display friendly error message
        } else {
          console.error("Error registering card transaction:", errorMsg);
          setErrorMessage(errorMsg);
        }
      }
    }
  };
  
  
   
   // Function to fetch all transactions
   const fetchAllTransactions = async () => {
    if (contract) {
        try {
            const [
                cardIds,
                receiverAddressesW,
                receiverAddressesR,
                dates,
                distances,
                pricePerUnits,
                statuses
            ] = await contract.getAllTransactions();

            // Format the transactions into an array of objects for easier rendering
            const formattedTransactions = cardIds.map((cardId, index) => ({
                cardId,
                receiverAddressW: receiverAddressesW[index],
                receiverAddressR: receiverAddressesR[index],
                date: dates[index],
                distance: distances[index],
                pricePerUnit: pricePerUnits[index],
                status: statuses[index]  // This will now be a string
            }));
         
            setAllTransactions(formattedTransactions);
            setErrorMessage("");  // Clear error messages
        } catch (error) {
            console.error("Error fetching all transactions:", error.message || JSON.stringify(error));
            setErrorMessage("Error fetching all transactions.");
        }
    }
};



  // Function to fetch transactions by multiple fields for wholesaler
  const fetchCardTransactionW = async () => {
    if (contract) {
      const { cardId, receiverAddressW,receiverAddressR, date, distance, pricePerUnit } = formInput;
      try {
        const transactionData = await contract.searchCardTransactionW(
          cardId,
          date,
          distance,
          walletAddress,
          receiverAddressR,
          pricePerUnit,
          
        );
        await transactionData.wait(); // Wait for the transaction to be mined
       
        fetchAllTransactions(); // Refresh the all transactions list after registering
        setErrorMessage(""); // Clear any previous error messages
      } catch (error) {
        console.error("Error fetching card transaction:", error.message || JSON.stringify(error));
        setErrorMessage("Error fetching transaction details . Details mismatched malpractice detected!!");
      }
    }
  };

  // Function to fetch transactions by multiple fields for wholesaler
  const fetchCardTransactionWR = async () => {
    if (contract) {
      // const { cardId, receiverAddress, date, distance, pricePerUnit, status } = formInput;
      const { cardId, receiverAddressW,receiverAddressR, date, distance, pricePerUnit } = formInput;
      try {
        const transactionData = await contract.searchCardTransactionWR(
          cardId,
          date,
          distance,
           walletAddress,
          receiverAddressR,
          pricePerUnit,
          
        );
        await transactionData.wait(); // Wait for the transaction to be mined
       
        fetchAllTransactions(); // Refresh the all transactions list after registering
        setErrorMessage(""); // Clear any previous error messages
      } catch (error) {
        console.error("Error fetching card transaction:", error.message || JSON.stringify(error));
        setErrorMessage("Error fetching transaction details . Details mismatched malpractice detected!!");
      }
    }
  };

  // Function to fetch transactions by multiple fields for retail
  const fetchCardTransactionR = async () => {
    if (contract) {
      // const { cardId, receiverAddress, date, distance, pricePerUnit, status } = formInput;
      const { cardId, receiverAddressW,receiverAddressR, date, distance, pricePerUnit } = formInput;
      try {
        const transactionData = await contract.searchCardTransactionR(
          cardId,
          date,
          distance,
          walletAddress,
          receiverAddressR,
          pricePerUnit,
          
        );
        await transactionData.wait(); // Wait for the transaction to be mined
       
        fetchAllTransactions(); // Refresh the all transactions list after registering
        setErrorMessage(""); // Clear any previous error messages
      } catch (error) {
        console.error("Error fetching card transaction:", error.message || JSON.stringify(error));
        setErrorMessage("Error fetching transaction details . Details mismatched malpractice detected!!");
      }
    }
  };



  const scanQrCode = async () => {
    try {
      const response = await axios.post("http://127.0.0.1:5000/scan_qr");
      const qrDataString = response.data.qr_data; // Get the string response
      const qrData = JSON.parse(qrDataString);

      const {
        cart_id: cardId,
        recivers_addressW: receiverAddressW,
        recivers_addressR: receiverAddressR,
        Date: date,
        Distance: distance,
        Price_per_Unit: pricePerUnit
        
      } = qrData;

      setFormInput({
        cardId: cardId || "",
        receiverAddressW: receiverAddressW || "",
        receiverAddressR: receiverAddressR || "",
        date: date || "",
        distance: distance || "",
        pricePerUnit: pricePerUnit || "",
        
      });
    } catch (error) {
      console.error("Error scanning QR code:", error.message || JSON.stringify(error));
      setErrorMessage("Error scanning QR code. Please try again.");
    }
  };

  

  return (
    <>


      <SideManu />
      <div className="dash-board">
      <div className="dashboard-cont">

      <div className="connect-button"  onClick={loadContract}>
  Connected Wallet: {walletAddress ? walletAddress : "No wallet connected"}
</div>    
{/*          
          
          <div className="dashboard-content" >
          <h2 className="dashboard-heading">Fetch Cart Transaction</h2>
          card id
          <input
            className="dashboard-input"
            placeholder="Card ID"
            value={formInput.cardId}
            onChange={(e) => setFormInput({ ...formInput, cardId: e.target.value })}
          />
           receiverAddressW
          <input
            disabled={true}
            className="dashboard-input"
            placeholder="Receiver Addressw"
            value={walletAddress}
            onChange={(e) => setFormInput({ ...formInput, receiverAddressW: e.target.value })}
          />
           receiverAddressR
          <input
            className="dashboard-input"
            placeholder="Receiver AddressR"
            value={formInput.receiverAddressR}
            onChange={(e) => setFormInput({ ...formInput, receiverAddressR: e.target.value })}
          />
          date
          <input
            type="date"
            className="dashboard-input"
            placeholder="Date"
            value={formInput.date}
            onChange={(e) => setFormInput({ ...formInput, date: e.target.value })}
          />
          distance
          <input
            className="dashboard-input"
            placeholder="Distance"
            value={formInput.distance}
            onChange={(e) => setFormInput({ ...formInput, distance: e.target.value })}
          />
          pricePerUnit
          <input
            className="dashboard-input"
            placeholder="Price Per Unit"
            value={formInput.pricePerUnit}
            onChange={(e) => setFormInput({ ...formInput, pricePerUnit: e.target.value })}
          />
          
          <button className="dashboard-button" onClick={fetchCardTransactionWR}>Validate QR as Wholesaler</button>
          <button className="dashboard-button" onClick={fetchCardTransactionW}>Forward Shipment</button>
          <button className="dashboard-button" onClick={fetchCardTransactionR}>Validate QR as Retailer</button>
          <button className="dashboard-register-button" onClick={registerCardTransaction}>Register QR</button>
          {errorMessage && <p className="dashboard-error-message">{errorMessage}</p>}
          </div> */}
          




        
{/* New table to display all transactions */}
<div className="dashboard-content">
            <h1 className="dashboard-subheading">All Transactions</h1>
            <table className="shipment-tracking-table">
              <thead>
                <tr>
                  <th>Card ID</th>
                  <th>Wholesaler Address </th>
                  <th>Retailer Address</th>
                  <th>Date</th>
                  <th>Distance</th>
                  <th>Price</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {allTransactions.map((tx, index) => (
                  <tr key={index}>
                    <td>{tx.cardId}</td>
                    <td>{tx.receiverAddressW}</td>
                    <td>{tx.receiverAddressR}</td>
                    <td>{tx.date}</td>
                    <td>{tx.distance}</td>
                    <td>{tx.pricePerUnit}</td>
                    <td>{tx.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
         


             
          <div className="dashboard-content dashboard-qr-data">
          <h1 className="dashboard-heading" style={{marginTop:"0px"}}>QR Data</h1>
          {formInput ? (
            <div>
              <p>Cart ID: {formInput.cardId}</p>
              <p>Wholesaler Address: {formInput.receiverAddressW}</p>
              <p>Retailer Address: {formInput.receiverAddressR}</p>
              <p>Date: {formInput.date}</p>
              <p>Distance: {formInput.distance}</p>
              <p>Price: {formInput.pricePerUnit}</p>
              
            </div>
          ) : (
            <p>Loading data...</p>
          )}
        </div>
<div className="button-qr-scan">
        <button className="dashboard-scan-button" onClick={scanQrCode}>Scan QR</button>
        <button className="dashboard-register-button" onClick={registerCardTransaction}>Register QR</button> 
        </div>
        
          

        
      </div>
      </div>
    </>
  );
}