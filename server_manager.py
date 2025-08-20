"""
FastChat Server Management System
Handles starting, stopping, and monitoring FastChat servers with port conflict resolution
"""

import os
import subprocess
import time
import socket
import psutil
import signal
import requests
from typing import Dict, List, Optional, Tuple
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ServerManager:
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.base_ports = {
            'controller': 21001,
            'openai_api': 8000,
            'model_worker_base': 21002
        }
        self.running_ports: List[int] = []
        
    def find_free_port(self, start_port: int = 8000, max_attempts: int = 100) -> int:
        """Find a free port starting from start_port"""
        for port in range(start_port, start_port + max_attempts):
            if self.is_port_free(port):
                return port
        raise RuntimeError(f"Could not find a free port starting from {start_port}")
    
    def is_port_free(self, port: int) -> bool:
        """Check if a port is free"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                return result != 0
        except Exception:
            return False
    
    def kill_processes_on_port(self, port: int):
        """Kill any processes running on the specified port"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    for conn in proc.info['connections'] or []:
                        if conn.laddr.port == port:
                            logger.info(f"Killing process {proc.info['pid']} ({proc.info['name']}) using port {port}")
                            proc.kill()
                            proc.wait(timeout=5)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            logger.warning(f"Error killing processes on port {port}: {e}")
    
    def cleanup_existing_servers(self):
        """Clean up any existing FastChat servers"""
        logger.info("Cleaning up existing FastChat servers...")
        
        # Kill processes by name patterns
        patterns = ['controller', 'model_worker', 'openai_api_server']
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if any(pattern in cmdline for pattern in patterns) and 'fastchat' in cmdline:
                    logger.info(f"Killing FastChat process: {proc.info['pid']}")
                    proc.kill()
                    proc.wait(timeout=5)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # Clean up ports
        for port in [21001, 8000] + list(range(21002, 21010)):
            if not self.is_port_free(port):
                self.kill_processes_on_port(port)
        
        time.sleep(2)  # Give processes time to cleanup
    
    def start_controller(self) -> int:
        """Start the FastChat controller"""
        port = self.find_free_port(self.base_ports['controller'])
        logger.info(f"Starting controller on port {port}")
        
        cmd = [
            'python', '-m', 'fastchat.serve.controller',
            '--host', 'localhost',
            '--port', str(port)
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        self.processes['controller'] = process
        self.running_ports.append(port)
        
        # Wait for controller to start
        if self.wait_for_service(f"http://localhost:{port}/list_models", timeout=30):
            logger.info(f"Controller started successfully on port {port}")
            return port
        else:
            raise RuntimeError("Controller failed to start")
    
    def start_model_worker(self, model_name: str = "lmsys/vicuna-7b-v1.5", worker_id: Optional[str] = None) -> int:
        """Start a model worker"""
        if worker_id is None:
            worker_id = f"worker_{len([k for k in self.processes.keys() if k.startswith('worker')])}"
        
        port = self.find_free_port(self.base_ports['model_worker_base'])
        controller_port = None
        
        # Find controller port
        for p in self.running_ports:
            if self.is_service_running(f"http://localhost:{p}/list_models"):
                controller_port = p
                break
        
        if not controller_port:
            raise RuntimeError("Controller not running")
        
        logger.info(f"Starting model worker '{worker_id}' with model '{model_name}' on port {port}")
        
        cmd = [
            'python', '-m', 'fastchat.serve.model_worker',
            '--model-path', model_name,
            '--controller', f'http://localhost:{controller_port}',
            '--worker-address', f'http://localhost:{port}',
            '--host', 'localhost',
            '--port', str(port)
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        self.processes[worker_id] = process
        self.running_ports.append(port)
        
        # Wait for worker to register
        time.sleep(10)  # Give worker time to download model and register
        
        if self.check_worker_registered(controller_port, model_name):
            logger.info(f"Model worker '{worker_id}' started successfully on port {port}")
            return port
        else:
            logger.warning(f"Model worker '{worker_id}' may not have registered properly")
            return port
    
    def start_openai_api_server(self) -> int:
        """Start the OpenAI-compatible API server"""
        port = self.find_free_port(self.base_ports['openai_api'])
        controller_port = None
        
        # Find controller port
        for p in self.running_ports:
            if self.is_service_running(f"http://localhost:{p}/list_models"):
                controller_port = p
                break
        
        if not controller_port:
            raise RuntimeError("Controller not running")
        
        logger.info(f"Starting OpenAI API server on port {port}")
        
        cmd = [
            'python', '-m', 'fastchat.serve.openai_api_server',
            '--controller-address', f'http://localhost:{controller_port}',
            '--host', 'localhost',
            '--port', str(port)
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        self.processes['openai_api'] = process
        self.running_ports.append(port)
        
        # Wait for API server to start
        if self.wait_for_service(f"http://localhost:{port}/v1/models", timeout=30):
            logger.info(f"OpenAI API server started successfully on port {port}")
            return port
        else:
            raise RuntimeError("OpenAI API server failed to start")
    
    def wait_for_service(self, url: str, timeout: int = 30) -> bool:
        """Wait for a service to become available"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        return False
    
    def is_service_running(self, url: str) -> bool:
        """Check if a service is running"""
        try:
            response = requests.get(url, timeout=2)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def check_worker_registered(self, controller_port: int, model_name: str) -> bool:
        """Check if a worker is registered with the controller"""
        try:
            response = requests.post(f"http://localhost:{controller_port}/list_models", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return any(model_name in model for model in models)
        except requests.exceptions.RequestException:
            pass
        return False
    
    def get_api_server_port(self) -> Optional[int]:
        """Get the port of the running OpenAI API server"""
        for port in self.running_ports:
            if self.is_service_running(f"http://localhost:{port}/v1/models"):
                return port
        return None
    
    def stop_all_servers(self):
        """Stop all running servers"""
        logger.info("Stopping all servers...")
        
        for name, process in self.processes.items():
            try:
                logger.info(f"Stopping {name}...")
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning(f"Force killing {name}...")
                process.kill()
                process.wait()
            except Exception as e:
                logger.error(f"Error stopping {name}: {e}")
        
        self.processes.clear()
        self.running_ports.clear()
    
    def get_status(self) -> Dict:
        """Get status of all servers"""
        status = {
            'controller': None,
            'openai_api': None,
            'workers': []
        }
        
        for port in self.running_ports:
            if self.is_service_running(f"http://localhost:{port}/list_models"):
                if port < 10000:  # Likely API server
                    status['openai_api'] = port
                else:  # Likely controller
                    status['controller'] = port
        
        return status
    
    def start_full_stack(self, model_name: str = "lmsys/vicuna-7b-v1.5") -> Dict[str, int]:
        """Start the complete FastChat stack"""
        try:
            # Clean up existing servers
            self.cleanup_existing_servers()
            
            # Start controller
            controller_port = self.start_controller()
            
            # Start model worker
            worker_port = self.start_model_worker(model_name)
            
            # Start OpenAI API server
            api_port = self.start_openai_api_server()
            
            return {
                'controller': controller_port,
                'worker': worker_port,
                'api': api_port
            }
            
        except Exception as e:
            logger.error(f"Failed to start full stack: {e}")
            self.stop_all_servers()
            raise

if __name__ == "__main__":
    # Test the server manager
    manager = ServerManager()
    try:
        ports = manager.start_full_stack()
        print(f"FastChat stack started successfully: {ports}")
        print("Press Ctrl+C to stop...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping servers...")
        manager.stop_all_servers()
        print("Servers stopped.")