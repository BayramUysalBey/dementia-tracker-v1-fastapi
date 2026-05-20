from nicegui import ui
import httpx 


status_label = ui.label("Status: Waiting for click...")

async def fetch_health():
   
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/api/v1/status/health")
        data = response.json()
        status_label.set_text(f"API says: {data}")

ui.button("Check API Health", on_click=fetch_health)

ui.run(port=8080)