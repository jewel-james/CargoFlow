import urllib.request
import urllib.parse
import time

BASE_URL = "http://127.0.0.1:5000"

def test_page(url, name, expected_text=None, data=None):
    print(f"Testing {name}...")
    try:
        if data:
            data = urllib.parse.urlencode(data).encode()
            req = urllib.request.Request(url, data=data)
        else:
            req = urllib.request.Request(url)
        
        with urllib.request.urlopen(req) as response:
            assert response.getcode() == 200
            content = response.read().decode()
            if expected_text:
                if expected_text not in content:
                    print(f"FAILED: '{expected_text}' not in response for {name}")
                    return False
            print(f"{name} OK.")
            return True
    except Exception as e:
        print(f"FAILED: {name} error: {e}")
        return False

if __name__ == "__main__":
    # Wait for server to be ready
    time.sleep(2)
    
    success = True
    success &= test_page(BASE_URL, "Home", "CargoFlow")
    
    booking_data = {
        'sender': 'Test Sender',
        'receiver': 'Test Receiver',
        'origin': 'Test City',
        'destination': 'Target City',
        'weight': '15.5'
    }
    success &= test_page(f"{BASE_URL}/book", "Booking", "Confirmed", booking_data)
    
    success &= test_page(f"{BASE_URL}/admin/shipments", "Admin Shipments", "Shipment Management")
    success &= test_page(f"{BASE_URL}/admin/shipments", "Search Result", "Test Sender")
    
    driver_data = {'name': 'New Driver', 'license': 'LIC-111', 'phone': '555-555'}
    success &= test_page(f"{BASE_URL}/admin/drivers", "Add Driver", "New Driver", driver_data)
    
    vehicle_data = {'model': 'New Truck', 'plate': 'PL-999', 'capacity': '5 Tons'}
    success &= test_page(f"{BASE_URL}/admin/vehicles", "Add Vehicle", "New Truck", vehicle_data)
    
    success &= test_page(f"{BASE_URL}/admin/analytics", "Analytics", "Business Analytics")
    
    if success:
        print("\nAll tests passed successfully!")
    else:
        print("\nSome tests failed.")
        exit(1)
