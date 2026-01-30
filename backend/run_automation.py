#!/usr/bin/env python3
"""CLI runner for golden dataset automation"""
import os
import sys
import logging
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from automation.orchestrator import GoldenDatasetOrchestrator
from automation.task_definitions import TASK_ORDER

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/golden_dataset/logs/automation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Golden Dataset Generator for LLM Terraform Testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tasks for all models
  python run_automation.py --all
  
  # Run specific tasks
  python run_automation.py --tasks c1_2 c1_3
  
  # Run for specific model only
  python run_automation.py --models deepseek_r1 --all
  
  # Run specific tasks for specific model
  python run_automation.py --models google_gemini_3_pro --tasks c1_2 c2_2
  
  # Custom iteration limit
  python run_automation.py --all --max-iterations 10
        """
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all tasks in order'
    )
    
    parser.add_argument(
        '--tasks',
        nargs='+',
        choices=TASK_ORDER,
        help='Specific task IDs to run (e.g., c1_2 c1_3)'
    )
    
    parser.add_argument(
        '--models',
        nargs='+',
        choices=['deepseek_r1', 'google_gemini_3_pro'],
        help='Specific models to test (default: both)'
    )
    
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=20,
        help='Maximum retry iterations per task (default: 20)'
    )
    
    parser.add_argument(
        '--base-dir',
        type=str,
        default='/app/golden_dataset',
        help='Base directory for output (default: /app/golden_dataset)'
    )
    
    parser.add_argument(
        '--api-key',
        type=str,
        help='OpenRouter API key (overrides environment variable)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.all and not args.tasks:
        parser.error("Must specify either --all or --tasks")
    
    # Load environment variables
    load_dotenv(Path(__file__).parent / '.env')
    
    # Check for API key
    api_key = args.api_key or os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        logger.error("OpenRouter API key is required!")
        logger.error("Set OPENROUTER_API_KEY environment variable or use --api-key argument")
        sys.exit(1)
    
    # Print banner
    print("\n" + "="*80)
    print("  Golden Dataset Generator for LLM Terraform Testing")
    print("="*80)
    print(f"  Base Directory: {args.base_dir}")
    print(f"  Max Iterations: {args.max_iterations}")
    print(f"  Models: {args.models or 'all'}")
    print(f"  Tasks: {args.tasks or 'all'}")
    print("="*80 + "\n")
    
    # Create orchestrator
    orchestrator = GoldenDatasetOrchestrator(
        base_dir=Path(args.base_dir),
        max_iterations=args.max_iterations,
        openrouter_api_key=api_key
    )
    
    # Determine tasks to run
    tasks_to_run = args.tasks if args.tasks else TASK_ORDER
    
    # Run tasks
    try:
        results = orchestrator.run_all_tasks(
            models=args.models,
            tasks=tasks_to_run
        )
        
        # Check if all succeeded
        all_success = all(
            task_result.get('success', False)
            for model_results in results.values()
            for task_result in model_results.values()
        )
        
        if all_success:
            logger.info("\n✅ All tasks completed successfully!")
            sys.exit(0)
        else:
            logger.warning("\n⚠️ Some tasks failed. Check logs for details.")
            sys.exit(1)
    
    except KeyboardInterrupt:
        logger.warning("\n⚠️ Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
