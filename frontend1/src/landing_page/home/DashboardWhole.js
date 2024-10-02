import React, { useState, useEffect } from "react";
import SideWhole from "../SideWhole.js";
import "./ShipmentTracker.css"; // For styling
import { ethers } from "ethers"; // ethers v6
import CardTransactionRegistry from "./CardTransactionRegistry.json"; // Import your ABI JSON
import contractConfig from '../Shipment/contractAddress.json';



const getTruckPosition = (status) => {
  switch (status) {
    case "PENDING":
      return "0%";
    case "IN_TRANSIT_WHOLESALER":
      return "25%";
    case "WHOLESALER_RECEIVED":
      return "50%";
    case "IN_TRANSIT_RETAILER":
      return "75%";
    case "DELIVERED":
      return "94%";
    default:
      return "0%";
  }
};

const getStatusClass = (status) => {
  switch (status) {
    case "PENDING":
      return "status-pending";
    case "IN_TRANSIT_WHOLESALER":
      return "status-in_transit";
    case "WHOLESALER_RECEIVED":
      return "status-received_by_wholesaler";
    case "IN_TRANSIT_RETAILER":
      return "status-in_transit";
    case "DELIVERED":
      return "status-completed";
    default:
      return "";
  }
};

function DashWhole({ qrData }) {
  const [contract, setContract] = useState(null);
  const [allTransactions, setAllTransactions] = useState([]); // Updated: use for shipment data
  const [showTracker, setShowTracker] = useState([]);
  const [animating, setAnimating] = useState([]);
  const [errorMessage, setErrorMessage] = useState("");

  const contractAddress = contractConfig.address;

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
  }, [contract]); // Adding contract as a dependency

  const loadContract = async () => {
    if (typeof window.ethereum !== "undefined") {
      await window.ethereum.request({ method: "eth_requestAccounts" });
      const provider = new ethers.BrowserProvider(window.ethereum); // Updated for ethers v6
      const signer = await provider.getSigner(); // Async getSigner in ethers v6
      const cardTransactionRegistry = new ethers.Contract(
        contractAddress,
        CardTransactionRegistry.abi,
        signer
      );
      setContract(cardTransactionRegistry); // Set the contract instance
    }
  };

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
          statuses,
        ] = await contract.getAllTransactions();

        const formattedTransactions = cardIds.map((cardId, index) => ({
          cardId,
          receiverAddressW: receiverAddressesW[index],
          receiverAddressR: receiverAddressesR[index],
          date: dates[index],
          distance: distances[index],
          pricePerUnit: pricePerUnits[index],
          status: statuses[index],
        }));

        setAllTransactions(formattedTransactions); // Update local state
        setShowTracker(Array(formattedTransactions.length).fill(false)); // Set tracking visibility state
        setAnimating(Array(formattedTransactions.length).fill(false)); // Set animation state
      } catch (error) {
        console.error(
          "Error fetching all transactions:",
          error.message || JSON.stringify(error)
        );
        setErrorMessage("Error fetching all transactions.");
      }
    }
  };

  const toggleTracker = (index) => {
    setShowTracker((prev) => {
      const updated = [...prev];
      updated[index] = !updated[index];
      return updated;
    });

    if (!showTracker[index]) {
      setAnimating((prev) => {
        const updated = [...prev];
        updated[index] = true;
        return updated;
      });

      setTimeout(() => {
        setAnimating((prev) => {
          const updated = [...prev];
          updated[index] = false;
          return updated;
        });
      }, 100); // Increased timeout for smoother effect
    }
  };

  return (
    <div className="dash-board">
      <SideWhole />
      <h1>Wholesaler Dashboard</h1>


      <div className="shipment-container">
        <h1>Shipment Table</h1>
        <table className="shipment-table">
          <thead>
            <tr>
              <th>Cart ID</th>
              <th>Wholesaler Address</th>
              <th>Retailer Address</th>
              <th>Date</th>
              <th>Distance</th>
              <th>Price</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {allTransactions.map((shipment, index) => (
              <tr key={shipment.cardId}>
                <td>{shipment.cardId}</td>
                <td>{shipment.receiverAddressW}</td>
                <td>{shipment.receiverAddressR}</td>
                <td>{shipment.date}</td>
                <td>{shipment.distance}</td>
                <td>{shipment.pricePerUnit}</td>
                <td>
                  <span className={getStatusClass(shipment.status)}>
                    {shipment.status.replace(/_/g, " ")}
                  </span>
                </td>
                <td>
                  <button
                    className={`ship-button ${
                      showTracker[index] ? "hide-tracking" : "show-tracking"
                    }`}
                    onClick={() => toggleTracker(index)}
                  >
                    {showTracker[index] ? "Hide Tracking" : "Show Tracking"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {allTransactions.map(
          (shipment, index) =>
            showTracker[index] && (
              <div key={index} className="shipment-item">
                <h3 className="h3-ship">Shipment #{shipment.cardId}</h3>
                <div className="enhanced-progress-bar">
                  <div className="progress-background"></div>
                  <div
                    className={`truck ${animating[index] ? "animate-truck" : ""}`}
                    style={{
                      left: animating[index] ? "0%" : getTruckPosition(shipment.status),
                    }}
                  >
                    <img src="media/NHC (1).png" width={95} className="truck-img" alt="truck" />
                  </div>
                  <div className="status-dot" style={{ left: "0%" }}></div>
                  <div className="status-dot" style={{ left: "25%" }}></div>
                  <div className="status-dot" style={{ left: "50%" }}></div>
                  <div className="status-dot" style={{ left: "75%" }}></div>
                  <div className="status-dot" style={{ left: "99%" }}></div>
                  <div className="status-checkpoint" style={{ left: "0%" }}>
                    Booking Received
                  </div>
                  <div className="status-checkpoint" style={{ left: "25%" }}>
                    In Transit to Wholesaler
                  </div>
                  <div className="status-checkpoint" style={{ left: "50%" }}>
                    Package Received
                  </div>
                  <div className="status-checkpoint" style={{ left: "75%" }}>
                    In Transit to Retailer
                  </div>
                  <div className="status-checkpoint" style={{ left: "100%" }}>
                    Completed
                  </div>
                </div>
              </div>
            )
        )}
      </div>
    </div>
  );
}

export default DashWhole;
