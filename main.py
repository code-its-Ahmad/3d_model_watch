from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bs4 import BeautifulSoup
import json
import logging
from typing import List, Dict, Optional
from urllib.parse import urljoin

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Watch Collection API", version="1.0.0")

# Pydantic model for input validation
class WatchQuery(BaseModel):
    name: str

# Pydantic model for watch data
class Watch(BaseModel):
    name: str
    image_url: str
    link: str

# Pydantic model for 3D/AR configuration
class Config3DAR(BaseModel):
    glb_url: str
    env_url: str
    tone_mapping: str
    tone_mapping_exposure: str
    category: str
    min_zoom: str
    max_zoom: str
    fov_multiplier: str
    interaction_prompt_url: str
    interaction_prompt_size: str

# Pydantic model for mode status
class ModeStatus(BaseModel):
    mode_3d: bool
    mode_ar: bool

# Pydantic model for full response
class WatchCollectionResponse(BaseModel):
    watches: List[Watch]
    config_3d_ar: Config3DAR
    mode_status: ModeStatus

# Sample HTML content (simulating input; in production, fetch from URL or file)
html_content = '''
<body class="__className_d28b8a">
<section aria-label="Notifications alt+T" tabindex="-1" aria-live="polite" aria-relevant="additions text" aria-atomic="false"></section>
<div>
    <div>
        <div class="absolute inset-0 bg-white">
            <div class="absolute inset-0 flex items-center justify-center">
                <div class="relative h-full w-full">
                    <div class="absolute h-full w-full hidden items-center justify-center">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="h-16 w-16 animate-spin"><path d="M21 12a9 9 0 1 1-6.219-8.56"></path></svg>
                    </div>
                    <shopar-3d class="absolute h-full w-full" glb-url="https://dj5e08oeu5ym4.cloudfront.net/3e/22b2468d-8bce-4f4d-951b-17469a889269.glb" env-url="https://demo.deepar.ai/env-maps/shoes.hdr" tone-mapping="Neutral" tone-mapping-exposure="1.21" category="Watches" touch-action="none" min-zoom="0.5" max-zoom="4" fov-multiplier="1.5" interaction-prompt-url="https://demo.deepar.ai/shopar/interaction-prompt.svg" interaction-prompt-size="2.75rem" style=""></shopar-3d>
                </div>
            </div>
            <div class="absolute left-0 right-0 top-0 z-20">
                <div class="z-10 m-auto flex w-full max-w-[500px] flex-col items-center">
                    <a target="_blank" class="top-0 z-50 w-fit rounded-b bg-black px-2 py-1 shadow" href="https://www.shopar.ai/"><img src="/images/shopar-logo-inverted-simple.svg" class="w-16"></a>
                </div>
            </div>
            <div class="absolute left-0 right-0 top-12 z-50 flex w-full justify-center">
                <div class="flex">
                    <button class="flex cursor-pointer items-center gap-1 rounded-l-full px-4 py-2 text-sm font-semibold transition-colors hover:bg-zink-900 bg-black text-white"><svg width="1.75rem" height="1.75rem" viewBox="0 0 903 897" fill="none" xmlns="http://www.w3.org/2000/svg"></svg>3D</button>
                    <button class="flex items-center gap-1 rounded-r-full px-4 py-2 text-sm font-semibold transition-colors bg-gray-100 text-zinc-600 hover:bg-gray-200"><svg width="1.75rem" height="1.75rem" viewBox="0 0 1000 1000" fill="none" xmlns="http://www.w3.org/2000/svg"></svg>AR</button>
                </div>
            </div>
            <div class="absolute bottom-0 left-0 right-0 z-50 flex w-full flex-col items-center justify-center pb-6 pt-6">
                <div class="mb-3 px-3 text-center text-zinc-700">
                    <h1 class="text-xl font-semibold">Hublot Mp-10 Tourbillon</h1>
                </div>
                <div class="relative mb-4 w-full overflow-x-hidden py-3 min-h-[60px]">
                    <div class="flex space-x-4 min-h-[60px]" style="transform: translateX(320px); transition: 0.5s;">
                        <div class="inline-block"><div class="flex h-16 w-16 items-center justify-center rounded-full bg-white shadow-lg cursor-pointer overflow-hidden"><img src="https://dj5e08oeu5ym4.cloudfront.net/thumb/c2a36185-19be-48dc-80ca-a40cd1e930ce.jpg" alt="Hublot MP-10 Tourbillon" class="h-full w-full object-cover"></div></div>
                        <div class="inline-block"><div class="flex h-16 w-16 items-center justify-center rounded-full bg-white shadow-lg cursor-pointer overflow-hidden"><img src="https://dj5e08oeu5ym4.cloudfront.net/thumb/34b97066-cf29-4941-9d0c-581084f5981e.png" alt="Hublot Spirit Of Big Bang Full Magic Gold" class="h-full w-full object-cover"></div></div>
                        <div class="inline-block"><div class="flex h-16 w-16 items-center justify-center rounded-full bg-white shadow-lg cursor-pointer overflow-hidden"><img src="https://dj5e08oeu5ym4.cloudfront.net/thumb/165c3844-6301-4398-b8fd-7b15f0032e16.jpg" alt="Movado Alta Super Sub Sea Automatic" class="h-full w-full object-cover"></div></div>
                        <div class="inline-block"><div class="flex h-16 w-16 items-center justify-center rounded-full bg-white shadow-lg cursor-pointer overflow-hidden"><img src="https://dj5e08oeu5ym4.cloudfront.net/thumb/12df7df7-fecd-412e-bea5-02e92c312408.webp" alt="Swatch Obsidian Ink" class="h-full w-full object-cover"></div></div>
                        <div class="inline-block"><div class="flex h-16 w-16 items-center justify-center rounded-full bg-white shadow-lg cursor-pointer overflow-hidden"><img src="https://dj5e08oeu5ym4.cloudfront.net/thumb/eb5e18b9-400c-4c14-b752-86d2be88a482.avif" alt="Swatch Caramellissima" class="h-full w-full object-cover"></div></div>
                        <div class="inline-block"><div class="flex h-16 w-16 items-center justify-center rounded-full bg-white shadow-lg cursor-pointer overflow-hidden"><img src="https://dj5e08oeu5ym4.cloudfront.net/thumb/d670348a-0aee-4916-b011-a8943b1d7496.jpg" alt="Swatch Random Ghost" class="h-full w-full object-cover"></div></div>
                        <div class="inline-block"><div class="flex h-16 w-16 items-center justify-center rounded-full bg-white shadow-lg cursor-pointer overflow-hidden"><img src="https://dj5e08oeu5ym4.cloudfront.net/thumb/425b727b-c788-46b3-adb2-4cdfb9a39c2c.png" alt="Swatch Up In Smoke" class="h-full w-full object-cover"></div></div>
                        <div class="inline-block"><div class="flex h-16 w-16 items-center justify-center rounded-full bg-white shadow-lg cursor-pointer overflow-hidden"><img src="https://dj5e08oeu5ym4.cloudfront.net/thumb/cd3708cc-75fc-4f43-a8b3-011b061dba36.webp" alt="Swatch Cobalt Lagoon" class="h-full w-full object-cover"></div></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
</body>
'''

# Provided watch links (corrected the syntax error in the last link)
watch_links = [
    'https://www.shopar.ai/collection/watches?product=66618cf59d3fb1edda45d3ba&mode=3d',
    'https://www.shopar.ai/collection/watches?product=65f48bb59ae86ec2a67a435d&mode=3d',
    'https://www.shopar.ai/collection/watches?product=657218fa3c333cddc7d2341c&mode=3d',
    'https://www.shopar.ai/collection/watches?product=66ba01a114de953c80003cfc&mode=3d',
    'https://www.shopar.ai/collection/watches?product=66ba06f314de953c8000719c&mode=3d',
    'https://www.shopar.ai/collection/watches?product=67129023c904b2a2777efe9d&mode=3d',
    'https://www.shopar.ai/collection/watches?product=6712989ac904b2a2777f39ed&mode=3d',
    'https://www.shopar.ai/collection/watches?product=66ba071914de953c8000722f&mode=3d'
]

# Function to extract watch data
def extract_watch_data(html: str, links: List[str]) -> List[Dict]:
    try:
        soup = BeautifulSoup(html, 'html.parser')
        watches = []
        watch_container = soup.find('div', class_='flex space-x-4 min-h-[60px]')
        if not watch_container:
            logger.error("Watch container not found")
            return []

        watch_items = watch_container.find_all('div', class_='inline-block')
        for i, item in enumerate(watch_items):
            img_tag = item.find('img')
            if img_tag:
                name = img_tag.get('alt', 'Unknown Watch')
                img_url = img_tag.get('src', '')
                link = links[i] if i < len(links) else ''
                watches.append({
                    'name': name,
                    'image_url': img_url,
                    'link': link
                })
            else:
                logger.warning(f"No image found for watch item {i}")
        return watches
    except Exception as e:
        logger.error(f"Error extracting watch data: {str(e)}")
        return []

# Function to extract 3D/AR configuration
def extract_3d_ar_config(html: str) -> Dict:
    try:
        soup = BeautifulSoup(html, 'html.parser')
        shopar_3d = soup.find('shopar-3d')
        if not shopar_3d:
            logger.error("shopar-3d element not found")
            return {}

        return {
            'glb_url': shopar_3d.get('glb-url', ''),
            'env_url': shopar_3d.get('env-url', ''),
            'tone_mapping': shopar_3d.get('tone-mapping', ''),
            'tone_mapping_exposure': shopar_3d.get('tone-mapping-exposure', ''),
            'category': shopar_3d.get('category', ''),
            'min_zoom': shopar_3d.get('min-zoom', ''),
            'max_zoom': shopar_3d.get('max-zoom', ''),
            'fov_multiplier': shopar_3d.get('fov-multiplier', ''),
            'interaction_prompt_url': shopar_3d.get('interaction-prompt-url', ''),
            'interaction_prompt_size': shopar_3d.get('interaction-prompt-size', '')
        }
    except Exception as e:
        logger.error(f"Error extracting 3D/AR config: {str(e)}")
        return {}

# Function to check 3D/AR mode status
def check_mode_status(html: str) -> Dict[str, bool]:
    try:
        soup = BeautifulSoup(html, 'html.parser')
        buttons = soup.find_all('button', class_='flex')
        mode_status = {'mode_3d': False, 'mode_ar': False}

        for button in buttons:
            text = button.get_text().strip()
            if '3D' in text and 'bg-black' in button.get('class', []):
                mode_status['mode_3d'] = True
            elif 'AR' in text and 'bg-gray-100' in button.get('class', []):
                mode_status['mode_ar'] = False
        return mode_status
    except Exception as e:
        logger.error(f"Error checking mode status: {str(e)}")
        return {'mode_3d': False, 'mode_ar': False}

# Function to simulate mode switch
def simulate_mode_switch(current_mode: str) -> str:
    try:
        new_mode = 'AR' if current_mode == '3D' else '3D'
        logger.info(f"Switching from {current_mode} to {new_mode}")
        return new_mode
    except Exception as e:
        logger.error(f"Error simulating mode switch: {str(e)}")
        return current_mode

# Function to process watch collection
def process_watch_collection(html: str, links: List[str]) -> Dict:
    try:
        watches = extract_watch_data(html, links)
        config = extract_3d_ar_config(html)
        mode_status = check_mode_status(html)
        current_mode = '3D' if mode_status['mode_3d'] else 'AR'
        new_mode = simulate_mode_switch(current_mode)

        logger.info(f"Extracted {len(watches)} watches")
        logger.info(f"Current mode: {current_mode}, New mode: {new_mode}")

        return {
            'watches': watches,
            'config_3d_ar': config,
            'mode_status': mode_status
        }
    except Exception as e:
        logger.error(f"Error processing watch collection: {str(e)}")
        return {}

# API endpoint to get all watch collection data
@app.get("/watches", response_model=WatchCollectionResponse)
async def get_watch_collection():
    result = process_watch_collection(html_content, watch_links)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to process watch collection")
    return result

# API endpoint to get watch by name
@app.post("/watches/by-name", response_model=Watch)
async def get_watch_by_name(query: WatchQuery):
    result = process_watch_collection(html_content, watch_links)
    watches = result.get('watches', [])
    watch_name = query.name.strip().lower()

    for watch in watches:
        if watch['name'].lower() == watch_name:
            return watch
    raise HTTPException(status_code=404, detail=f"Watch '{query.name}' not found")

# Optional: Run the FastAPI app (for local testing)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)