import os
import subprocess
import sys

if "." not in sys.path:
    sys.path.insert(0, ".")

subprocess.run([sys.executable, "-m", "pydoc", "-w", "HOTEL"])


top_modules = ["db"]
for module in top_modules:
    full_name = f"HOTEL.{module}"
    print(f"Generating documentation for module {full_name}")
    subprocess.run([sys.executable, "-m", "pydoc", "-w", full_name])

packages_and_modules = {
    "HOTEL.setup":["Factory"],
    "HOTEL.common": ["Auth"],
    "HOTEL.AImodels": ["ai_model","csv_retriever"], 
    "HOTEL.controllers": ["EmailController", "FormController","SearchController"],  
    "HOTEL.entities": ["Booking", "Creditcard","Enums","FAQ","Floor","Hotel","Room","Service","User", "Staff"],  
    "HOTEL.services": ["ReceiptGenerator", "response", "RoomAvailability", "ReportGenerator","EventInvitationGenerator"],
    "HOTEL.views": ["AIRoutes", "BookingRoutes", "DetailRoutes", "InfoRoutes","PaymentRoutes","StaffRoutes","UserRoutes", "AdminRoutes", "EventRoutes"]  
}

for package, modules in packages_and_modules.items():
    print(f"Generating documentation for {package}")
    subprocess.run([sys.executable, "-m", "pydoc", "-w", package])
    
    for module in modules:
        full_name = f"{package}.{module}"
        print(f"Generating documentation for module {full_name}")
        subprocess.run([sys.executable, "-m", "pydoc", "-w", full_name])

print("Done generating documentation")