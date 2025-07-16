#!/usr/bin/env python3
"""
Startup script to initialize pre-generation of sample videos
"""

import time
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def wait_for_server(url="http://127.0.0.1:8080", max_retries=30):
    """
    Wait for the Flask server to be ready
    """
    for i in range(max_retries):
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                logger.info("Server is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        logger.info(f"Waiting for server... ({i+1}/{max_retries})")
        time.sleep(2)
    
    logger.error("Server did not start within expected time")
    return False

def start_pre_generation():
    """
    Start pre-generation of sample videos
    """
    try:
        # Start pre-generation of sample videos
        response = requests.post("http://127.0.0.1:8080/pre-generate/samples")
        if response.status_code == 200:
            logger.info("Pre-generation started successfully!")
            
            # Monitor progress
            while True:
                status_response = requests.get("http://127.0.0.1:8080/pre-generate/status")
                if status_response.status_code == 200:
                    status = status_response.json()
                    logger.info(f"Pre-generation status: {status['queue_length']} items in queue, running: {status['is_running']}")
                    
                    if status['queue_length'] == 0 and not status['is_running']:
                        logger.info("Pre-generation completed!")
                        break
                
                time.sleep(10)  # Check every 10 seconds
        else:
            logger.error(f"Failed to start pre-generation: {response.text}")
            
    except Exception as e:
        logger.error(f"Error starting pre-generation: {e}")

if __name__ == "__main__":
    logger.info("Starting pre-generation initialization...")
    
    if wait_for_server():
        start_pre_generation()
    else:
        logger.error("Could not connect to server")
