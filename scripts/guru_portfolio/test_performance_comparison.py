#!/usr/bin/env python3
"""
Test script for portfolio performance comparison feature
"""

import subprocess
import sys
import os

def test_performance_comparison():
    """Test the performance comparison feature with a well-known fund"""
    
    print("🧪 Testing Portfolio Performance Comparison Feature")
    print("="*60)
    
    # Test cases with different companies
    test_cases = [
        {
            "company": "Berkshire Hathaway Inc",
            "quarter": "Q3 2024",
            "lookback": 4,
            "description": "Warren Buffett's Berkshire Hathaway"
        },
        {
            "company": "ARK Invest",
            "quarter": "Q3 2024", 
            "lookback": 8,
            "description": "Cathie Wood's ARK Invest (8 quarters lookback)"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📊 Test Case {i}: {test['description']}")
        print("-"*50)
        
        # Prepare command
        cmd = [
            sys.executable,
            "main.py",
            test["company"],
            test["quarter"],
            "--compare-sp500",
            "--lookback-quarters", str(test["lookback"]),
            "--output-dir", f"test_output_{i}",
            "--save-html"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        
        try:
            # Run the command
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Test passed!")
                print("\nOutput files created:")
                output_dir = f"test_output_{i}"
                if os.path.exists(output_dir):
                    for file in sorted(os.listdir(output_dir)):
                        print(f"  - {file}")
            else:
                print("❌ Test failed!")
                print(f"Error: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Exception occurred: {e}")
    
    print("\n" + "="*60)
    print("🎉 Performance comparison feature testing completed!")
    print("\nTo view the results, check the test_output_* directories")
    print("The performance_comparison.png files show the portfolio vs S&P 500 comparison")

if __name__ == "__main__":
    # First, ensure dependencies are installed
    print("📦 Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], 
                   capture_output=True)
    
    # Run the tests
    test_performance_comparison() 