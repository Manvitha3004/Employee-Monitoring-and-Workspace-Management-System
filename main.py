"""
Main Application Entry Point
Employee Monitoring and Workspace Management System
"""

import sys
import os
import logging
import argparse

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.controller import SystemController
from src.api_server import APIServer


def setup_logging(log_level='INFO'):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/system.log'),
            logging.StreamHandler()
        ]
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Employee Monitoring System')
    parser.add_argument('--config', default='config.yaml', help='Path to configuration file')
    parser.add_argument('--log-level', default='INFO', help='Logging level')
    parser.add_argument('--no-autostart', action='store_true', help='Do not auto-start monitoring')
    
    args = parser.parse_args()
    
    # Create necessary directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("=" * 60)
        logger.info("Employee Monitoring and Workspace Management System")
        logger.info("=" * 60)
        
        # Initialize system controller
        controller = SystemController(args.config)
        
        # Auto-start if not disabled
        if not args.no_autostart:
            controller.start()
        
        # Initialize and run API server
        api_server = APIServer(controller, controller.config)
        
        logger.info("System ready. Access the web interface at:")
        logger.info(f"http://{api_server.host}:{api_server.port}")
        
        # Run server (blocking)
        api_server.run()
        
    except KeyboardInterrupt:
        logger.info("\nShutting down...")
        controller.stop()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
