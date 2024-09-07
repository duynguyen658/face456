import asyncio
import websockets

async def send_data():
    try:
        async with websockets.connect("ws://127.0.0.1:8000/ws/attendance") as websocket:
            # Gửi dữ liệu
            with open('D:/nckh2024/nckh2/API/Database/Minh Duy.jpg', 'rb') as f:
                data = f.read()
            await websocket.send(data)

            # Nhận phản hồi
            try:
                response = await websocket.recv()
                print(response)
            except websockets.exceptions.ConnectionClosedError:
                print("Connection closed before receiving response")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(send_data())



#%%
