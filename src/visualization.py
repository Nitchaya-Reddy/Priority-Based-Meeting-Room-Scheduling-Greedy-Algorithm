"""
Visualization Module for Experimental Results

Generates graphs showing the relationship between input size and running time
to validate the theoretical time complexity analysis of O(n log n) for the
greedy activity selection algorithm.

"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


class ResultVisualizer:
    """Creates visualizations for experimental results."""
    
    def __init__(self, results_file: str = "../data/experimental_results.json"):
        """Load experimental results from JSON file."""
        with open(results_file, 'r') as f:
            self.results = json.load(f)
    
    def plot_running_time_comparison(self, save_path: str = "../results/plots/running_time.png"):
        """Plot running time vs input size."""
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Extract data
        sizes = self.results['sizes']
        times = self.results['times']
        
        # Plot actual running times
        ax.plot(sizes, times, 'o-', label='Actual Running Time', 
                linewidth=2.5, markersize=8, color='#2ecc71')
        
        # Plot theoretical O(n log n) curve for comparison
        sizes_np = np.array(sizes)
        if len(sizes) > 1 and times[0] > 0:
            # Scale theoretical curve to match first data point
            theoretical_nlogn = sizes_np * np.log2(sizes_np)
            scaling_factor = times[0] / theoretical_nlogn[0] if theoretical_nlogn[0] > 0 else 1
            theoretical_scaled = theoretical_nlogn * scaling_factor
            
            ax.plot(sizes, theoretical_scaled, '--', label='Theoretical O(n log n)', 
                    linewidth=2, color='#95a5a6')
        
        ax.set_xlabel('Input Size (n)', fontsize=13, fontweight='bold')
        ax.set_ylabel('Running Time (seconds)', fontsize=13, fontweight='bold')
        ax.set_title('Running Time Analysis: O(n log n) Complexity', 
                    fontsize=15, fontweight='bold', pad=20)
        ax.legend(fontsize=12, loc='upper left')
        ax.grid(True, alpha=0.3)
        
        # Format y-axis to avoid scientific notation overlap
        ax.ticklabel_format(style='plain', axis='y')
        
        plt.tight_layout(pad=2.0)
        self._ensure_dir(save_path)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved: {save_path}")
    
    def plot_complexity_verification(self, save_path: str = "../results/plots/complexity_ratio.png"):
        """Plot the ratio of time to theoretical O(n log n) to verify complexity."""
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Extract data
        sizes = np.array(self.results['sizes'])
        times = np.array(self.results['times'])
        
        # Filter out small sizes to avoid log issues
        valid_indices = sizes > 1
        sizes_valid = sizes[valid_indices]
        times_valid = times[valid_indices]
        
        # Calculate ratio: time / (n log n)
        ratio = times_valid / (sizes_valid * np.log2(sizes_valid))
        
        # Convert to scientific notation for cleaner display
        mean_ratio = np.mean(ratio)
        std_dev = np.std(ratio)
        
        ax.plot(sizes_valid, ratio, 'o-', linewidth=2.5, markersize=8, color='#3498db')
        ax.axhline(y=mean_ratio, color='#e74c3c', linestyle='--', 
                   linewidth=2, label=f'Mean = {mean_ratio:.2e}')
        
        # Add confidence interval
        ax.fill_between(sizes_valid, 
                        mean_ratio - std_dev, 
                        mean_ratio + std_dev, 
                        alpha=0.2, color='#e74c3c',
                        label=f'±1 Std Dev = {std_dev:.2e}')
        
        ax.set_xlabel('Input Size (n)', fontsize=13, fontweight='bold')
        ax.set_ylabel('Time / (n log n)', fontsize=13, fontweight='bold')
        ax.set_title('Complexity Verification: Constant Ratio Confirms O(n log n)', 
                    fontsize=15, fontweight='bold', pad=20)
        ax.legend(fontsize=11, loc='upper right')
        ax.grid(True, alpha=0.3)
        
        # Use scientific notation for y-axis
        ax.ticklabel_format(style='scientific', axis='y', scilimits=(0,0))
        
        plt.tight_layout(pad=2.0)
        self._ensure_dir(save_path)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved: {save_path}")
    
    def plot_all(self):
        """Generate all visualization plots."""
        print("=" * 80)
        print("GENERATING VISUALIZATIONS")
        print("=" * 80)
        print()
        
        self.plot_running_time_comparison()
        self.plot_complexity_verification()
        
        print()
        print("=" * 80)
        print("All visualizations generated successfully!")
        print("Check the '../results/plots/' directory for output files.")
        print("=" * 80)
    
    @staticmethod
    def _ensure_dir(filepath: str):
        """Ensure directory exists for the given filepath."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    # Check if results file exists
    results_file = "../data/experimental_results.json"
    
    if not Path(results_file).exists():
        print(f"Error: Results file '{results_file}' not found!")
        print("Please run 'experimental_analysis.py' first to generate results.")
    else:
        visualizer = ResultVisualizer(results_file)
        visualizer.plot_all()
