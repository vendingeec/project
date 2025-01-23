from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for orders (replace with database in production)
orders = []

# Add this after the orders list
machine_status = {
    "waterLevel": 80,
    "cupsBalance": 100,
    "blenderActive": False,
    "isDispensing": False,
    "flavors": {
        "Cola": 1000,
        "Orange": 1000,
        "Lemon": 1000,
        "Grape": 1000,
        "Water": 1000,
        "Coffee": 1000,
        "Tea": 1000,
        "Energy": 1000,
        "Sprite": 1000
    }
}

class VendingOrder(BaseModel):
    cupType: str
    flavor: str
    waterQuantity: str

@app.get("/api/machine-status")
async def get_machine_status():
    return machine_status

@app.post("/api/process-order")
async def process_order(order: VendingOrder):
    try:
        logger.info(f"Received order: {order}")
        
        if order.flavor not in machine_status["flavors"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid flavor. Available flavors: {list(machine_status['flavors'].keys())}"
            )

        # Update machine status
        machine_status["blenderActive"] = True
        machine_status["isDispensing"] = True
        machine_status["waterLevel"] = max(0, machine_status["waterLevel"] - 5)
        machine_status["cupsBalance"] = max(0, machine_status["cupsBalance"] - 1)
        machine_status["flavors"][order.flavor] = max(0, machine_status["flavors"][order.flavor] - 50)

        # Simulate processing time
        await asyncio.sleep(2)
        
        # Reset status
        machine_status["blenderActive"] = False
        machine_status["isDispensing"] = False
        
        # Store the order
        order_record = {
            "timestamp": datetime.now().isoformat(),
            "cup_type": order.cupType,
            "flavor": order.flavor,
            "water_quantity": order.waterQuantity
        }
        orders.append(order_record)
        
        return {
            "status": "success",
            "message": "Order processed successfully",
            "order_details": order_record
        }
    except Exception as e:
        logger.error(f"Error processing order: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orders")
async def get_orders():
    return orders
