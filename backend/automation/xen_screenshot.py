"""Xen Orchestra screenshot automation using Playwright"""
import os
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional
import asyncio

logger = logging.getLogger(__name__)

class XenScreenshot:
    """Automate screenshots from Xen Orchestra web interface"""
    
    def __init__(
        self,
        xo_url: str = "http://localhost:8080",
        username: str = "admin@admin.net",
        password: str = "admin"
    ):
        self.xo_url = xo_url
        self.username = username
        self.password = password
        self.screenshot_dir = Path("/app/golden_dataset/screenshots")
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    async def capture_screenshots(
        self,
        task_id: str,
        model_short_name: str
    ) -> Dict[str, str]:
        """Capture all required screenshots for a task
        
        Args:
            task_id: Task identifier (e.g., 'c1_2')
            model_short_name: Model short name (e.g., 'deepseek_r1')
            
        Returns:
            Dict mapping screenshot types to file paths
        """
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            logger.error("Playwright not installed. Install with: pip install playwright && playwright install")
            return self._generate_placeholder_screenshots(task_id, model_short_name)
        
        screenshots = {}
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(viewport={"width": 1920, "height": 1080})
                page = await context.new_page()
                
                # Login to Xen Orchestra
                logger.info(f"Logging into Xen Orchestra at {self.xo_url}")
                await page.goto(self.xo_url, wait_until="networkidle")
                
                # Wait for login form
                await page.wait_for_selector('input[type="email"]', timeout=10000)
                
                # Fill login credentials
                await page.fill('input[type="email"]', self.username)
                await page.fill('input[type="password"]', self.password)
                
                # Click login button
                await page.click('button[type="submit"]')
                
                # Wait for navigation after login
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(2)
                
                # Navigate to VM list
                vm_list_url = f"{self.xo_url}/v5/#/home?p=1&s=power_state%3Arunning+&t=VM"
                logger.info(f"Navigating to VM list: {vm_list_url}")
                await page.goto(vm_list_url, wait_until="networkidle")
                await asyncio.sleep(3)
                
                # Screenshot 1: VM List
                vm_list_path = self.screenshot_dir / f"{task_id}_{model_short_name}_xo_list.png"
                await page.screenshot(path=str(vm_list_path), full_page=True)
                screenshots["xen_orchestra_vm_list"] = str(vm_list_path.relative_to("/app/golden_dataset"))
                logger.info(f"Captured VM list screenshot: {vm_list_path}")
                
                # Screenshot 2: VM Details (click first VM)
                try:
                    vm_elements = await page.query_selector_all('.vm-item, [data-testid="vm-row"], tr.vm')
                    if vm_elements:
                        await vm_elements[0].click()
                        await asyncio.sleep(2)
                        
                        vm_details_path = self.screenshot_dir / f"{task_id}_{model_short_name}_vm_details.png"
                        await page.screenshot(path=str(vm_details_path), full_page=True)
                        screenshots["vm_details"] = str(vm_details_path.relative_to("/app/golden_dataset"))
                        logger.info(f"Captured VM details screenshot: {vm_details_path}")
                except Exception as e:
                    logger.warning(f"Could not capture VM details screenshot: {e}")
                
                # Screenshot 3: Resource Usage (navigate to pool/host view)
                try:
                    await page.goto(f"{self.xo_url}/v5/#/hosts", wait_until="networkidle")
                    await asyncio.sleep(2)
                    
                    resources_path = self.screenshot_dir / f"{task_id}_{model_short_name}_resources.png"
                    await page.screenshot(path=str(resources_path), full_page=True)
                    screenshots["resource_usage"] = str(resources_path.relative_to("/app/golden_dataset"))
                    logger.info(f"Captured resources screenshot: {resources_path}")
                except Exception as e:
                    logger.warning(f"Could not capture resources screenshot: {e}")
                
                await browser.close()
            
            return screenshots
            
        except Exception as e:
            logger.error(f"Screenshot capture failed: {str(e)}")
            return self._generate_placeholder_screenshots(task_id, model_short_name)
    
    def _generate_placeholder_screenshots(self, task_id: str, model_short_name: str) -> Dict[str, str]:
        """Generate placeholder screenshot paths when capture fails
        
        Args:
            task_id: Task identifier
            model_short_name: Model short name
            
        Returns:
            Dict with placeholder paths
        """
        screenshots = {
            "xen_orchestra_vm_list": f"screenshots/{task_id}_{model_short_name}_xo_list.png",
            "vm_details": f"screenshots/{task_id}_{model_short_name}_vm_details.png",
            "resource_usage": f"screenshots/{task_id}_{model_short_name}_resources.png"
        }
        
        # Create empty placeholder files
        for key, path in screenshots.items():
            full_path = Path("/app/golden_dataset") / path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            if not full_path.exists():
                full_path.write_text(f"Placeholder for {key}")
        
        return screenshots
    
    async def get_vm_details_from_xo(self) -> List[Dict]:
        """Get VM details from Xen Orchestra API
        
        Returns:
            List of VM details dicts
        """
        # This would use the XO API to get VM details
        # For now, return placeholder
        return []
