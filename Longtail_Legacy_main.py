import asyncio
from bleak import BleakClient, BleakScanner
strength_CharacteristicId = "955a1504-0fe2-f5aa-a094-84b8d4f3e8ad"
A_CharacteristicId = "955a1506-0fe2-f5aa-a094-84b8d4f3e8ad"
B_CharacteristicId = "955a1505-0fe2-f5aa-a094-84b8d4f3e8ad"

# Wave 1 from demo
Wave1 = ['210100',
         '210102',
         '210104',
         '210106',
         '210108',
         '21010A',
         '21010A',
         '21010A',
         '000000',
         '000000',
         '000000',
         '000000',]



async def main():
    # devices: array
    print("Start scanning:")
    devices = await BleakScanner.discover()
    BTAddress = ""
    for deviceScanner in devices:
        print(deviceScanner)
        if deviceScanner.name == "D-LAB ESTIM01":
            print("Device found")
            BTAddress = deviceScanner.address
            break

    async with BleakClient(BTAddress) as client:
        if not client.is_connected:
            print("Failed to connect.")
            return
        print(f"Connected to {BTAddress}")
        # Client operations here
        for timer in range(50):
            # I just get kicked by it 2024.08.27
            # I just get kicked by it again 2024.09.01
            # BE VERY CAREFUL CHANGING THIS VALUE !!!
            testData = bytes.fromhex("00E01C")
            await client.write_gatt_char(strength_CharacteristicId, testData)
            for waveScanner in Wave1:
                print("Writing wave: " + waveScanner)
                await client.write_gatt_char(A_CharacteristicId, bytes.fromhex(waveScanner))
                await client.write_gatt_char(B_CharacteristicId, bytes.fromhex(waveScanner))
                await asyncio.sleep(0.1)

        print("Done")

asyncio.run(main())