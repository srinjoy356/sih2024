import cv2
import pyzbar.pyzbar as pyzbar

def scan_qr_codes(url):
    # Open video stream
    cap = cv2.VideoCapture(url)

    # Check if the video stream was opened successfully
    if not cap.isOpened():
        print(f"Error: Could not open video stream from {url}")
        return None

    while True:
        # Read a frame from the video stream
        ret, frame = cap.read()

        # Check if the frame was captured successfully
        if not ret:
            print("Error: Could not read frame")
            break

        # Resize the frame
        frame = cv2.resize(frame, (0, 0), fx=0.50, fy=0.50)

        # Decode QR codes in the frame
        qr_codes = pyzbar.decode(frame)

        # Loop through all detected QR codes
        for qr_code in qr_codes:
            # Get the QR code data and type
            qr_data = qr_code.data.decode("utf-8")
            qr_type = qr_code.type

            # Only process QR codes
            if qr_type == "QRCODE":
                # Log the QR code data
                print(f"QR Data: {qr_data} (Type: {qr_type})")

                # Return the QR code data as soon as it is detected
                cap.release()
                return qr_data

        # Instead of `cv2.waitKey()`, you can simply break the loop by setting a condition,
        # or by manually stopping the process when needed.
        # In headless mode, you might run it in a continuous loop or process specific frames.

    # Release the capture
    cap.release()

    return None  # Return None if no QR code was detected

# Example usage
# scan_qr_codes("http://192.168.142.191:8080/video")

