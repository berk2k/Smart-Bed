from m5stack import *
from m5ui import *
from uiflow import *
import ntptime
import urequests
import time
import gc

# ========== Screen Setup and Variables ========== #
setScreenColor(0x222222)
label0 = M5TextBox(53, 31, "", lcd.FONT_DejaVu24, 0xFFFFFF)
label1 = M5TextBox(53, 74, "", lcd.FONT_Default, 0xFFFFFF)
label2 = M5TextBox(53, 112, "", lcd.FONT_Default, 0xFFFFFF)
label5 = M5TextBox(53, 151, "", lcd.FONT_Default, 0xFFFFFF)
label6 = M5TextBox(53, 189, "", lcd.FONT_Default, 0xFFFFFF)

label0.setText('Sending request...')

# ========== Constants and Initialization ========== #
smartbed_id = 905
position = "BACK"
time_counter = 0
last_change_time = 0
sent_data_flag = False
parser = '|'

# ========== NTP Setup ========== #
ntp = ntptime.client(host='cn.pool.ntp.org', timezone=8)

# ========== Helper Functions ========== #
def oracletimestamp():
    def pad(n): return f"{n:02}"
    return f"{ntp.year()}-{pad(ntp.month())}-{pad(ntp.day())}T{pad(ntp.hour())}:{pad(ntp.minute())}:{pad(ntp.second())}Z"

def get_patient_name(bed_id):
    try:
        admission = urequests.get('https://fciszjhbmsy6qgt-db1n8ia.adb.us-ashburn-1.oraclecloudapps.com/ords/iot/admission/').json()
        patients = urequests.get('https://fciszjhbmsy6qgt-db1n8ia.adb.us-ashburn-1.oraclecloudapps.com/ords/iot/patient/').json()

        patient_ids = [a.get('patientid') for a in admission['items'] if a.get('bedid') == bed_id]
        if not patient_ids:
            return None

        patient = next((p.get('first_name') for p in patients['items'] if p.get('patient_id') == patient_ids[0]), None)
        return patient

    except Exception as e:
        label0.setText(f"Error: {e}")
        return None

def send_position(position):
    try:
        data = {
            'BEDID': smartbed_id,
            'PATIENTPOSITION': position,
            'POSITIONDURATION': time_counter,
            'LOGTIME': oracletimestamp()
        }
        res = urequests.post('https://fciszjhbmsy6qgt-db1n8ia.adb.us-ashburn-1.oraclecloudapps.com/ords/iot/bedlog/', json=data, headers={'Content-Type': 'application/json'})
        res.close()
        label5.setText("Database updated")
    except Exception as e:
        label5.setText(f"Failed: {e}")

def notify_remote(position, patient_name):
    try:
        remoteInit()
        message = f"{smartbed_id}{parser}{patient_name}{parser}{position}"
        sendP2PData('4D835F7A', message)
        rgb.setColorAll(0xff0000)
    except Exception as e:
        label6.setText(f"Notify error: {e}")

# ========== Button Definitions ========== #
def handle_button(position_str):
    global position, last_change_time, time_counter, sent_data_flag
    label1.setText(f"Patient is laying on their {position_str.lower()}")
    send_position(position_str)
    last_change_time = time_counter
    time_counter = 0
    position = position_str
    sent_data_flag = False
    rgb.setColorAll(0x000000)
    label6.setText("")

btnA.wasPressed(lambda: handle_button("LEFT"))
btnB.wasPressed(lambda: handle_button("BACK"))
btnC.wasPressed(lambda: handle_button("RIGHT"))

# ========== Get Patient Information ========== #
patient_name = get_patient_name(smartbed_id)
if patient_name:
    label2.setText("Patient: " + patient_name)
else:
    label2.setText("No patient found")

# ========== Main Loop ========== #
while True:
    time_counter += 1
    label0.setText(f"time: {time_counter}")

    # Automatically send data after inactivity period
    if time_counter > 10 and not sent_data_flag:
        if patient_name:
            notify_remote(position, patient_name)
            sent_data_flag = True

    wait(1)
