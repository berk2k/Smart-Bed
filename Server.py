from m5stack import *
from m5ui import *
from uiflow import *

# Initialize P2P communication
remoteInit()

# Set background color to dark gray
setScreenColor(0x222222)

# Create text labels to display received data
label0 = M5TextBox(116, 69, "Waiting for data...", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label1 = M5TextBox(116, 90, " ", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label2 = M5TextBox(116, 120, " ", lcd.FONT_Default, 0xFFFFFF, rotate=0)

while True:
    # Receive data via P2P
    received_data = getP2PData()
    
    if received_data is not None:
        # Split received string by '|' character into components
        parsed_data = received_data.split('|')
        
        if len(parsed_data) == 3:
            received_bed_Id = parsed_data[0]
            received_patient_name = parsed_data[1]
            received_position = parsed_data[2]
            
            # Update labels with the received data
            label0.setText(str(received_bed_Id))
            label1.setText(str(received_patient_name))
            label2.setText(str(received_position))
        else:
            # If the data format is incorrect
            print("Invalid data format received:", received_data)
    else:
        # No data received, show waiting message
        label0.setText("No data received")

    wait_ms(500)  # Wait 500 milliseconds before checking again
