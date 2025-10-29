"""
Plotting class for waterslide sandbag landing visualization.
Encapsulates all matplotlib visualization logic for the waterslide optimizer.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from typing import Optional, Tuple
from matplotlib.figure import Figure
from matplotlib.axes import Axes


class App5Plot:
    """Manages all plotting for the waterslide sandbag landing analysis."""
    
    def __init__(self, pool_radius: float, 
                 target_radius: Optional[float] = None,
                 target_mean_tolerance: Optional[float] = None,
                 interactive: bool = True):
        """
        Initialize the plotter.
        
        Args:
            pool_radius: Radius of the pool (safe zone).
            target_radius: Optional target radius for all bags.
            target_mean_tolerance: Optional tolerance for mean distance from center.
            interactive: If True, use interactive mode for live updates.
        """
        self.pool_radius = pool_radius
        self.target_radius = target_radius
        self.target_mean_tolerance = target_mean_tolerance
        self.interactive = interactive
        
        self.fig: Optional[Figure] = None
        self.ax1: Optional[Axes] = None
        self.ax2: Optional[Axes] = None
    
    def create_figure(self) -> Tuple[Figure, Axes, Axes]:
        """
        Create and return the figure with two subplots.
        
        Returns:
            (fig, ax1, ax2): Figure and two axes objects.
        """
        if self.interactive:
            plt.ion()
        
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(18, 8))
        return self.fig, self.ax1, self.ax2
    
    def draw(self, 
             x_positions: np.ndarray,
             y_positions: np.ndarray,
             std_x: float,
             std_y: float,
             title_prefix: str = "",
             annot_mean: Optional[Tuple[float, float]] = None,
             annot_variance: Optional[float] = None,
             annot_frac: Optional[float] = None,
             annot_scale_idx: Optional[int] = None,
             annot_total_scales: Optional[int] = None,
             annot_mstep: Optional[float] = None,
             annot_vstep: Optional[float] = None,
             pause_seconds: float = 0.0) -> None:
        """
        Draw or update the complete visualization.
        
        Args:
            x_positions: X coordinates of sandbag landings.
            y_positions: Y coordinates of sandbag landings.
            std_x: Standard deviation in x direction.
            std_y: Standard deviation in y direction.
            title_prefix: Prefix for the main title.
            annot_mean: Current optimizer mean (for annotation).
            annot_variance: Current variance (for annotation).
            annot_frac: Current in-pool fraction (for annotation).
            annot_scale_idx: Current scale index (for annotation).
            annot_total_scales: Total number of scales (for annotation).
            annot_mstep: Current mean step size (for annotation).
            annot_vstep: Current variance step size (for annotation).
            pause_seconds: Seconds to pause after drawing (for animation).
        """
        if self.ax1 is None or self.ax2 is None:
            raise RuntimeError("Figure not created. Call create_figure() first.")
        
        # Clear axes for redraw
        self.ax1.clear()
        self.ax2.clear()
        
        # Draw both panels
        self._draw_overhead_view(x_positions, y_positions, std_x, std_y, 
                                annot_mean, annot_variance, annot_frac,
                                annot_scale_idx, annot_total_scales, 
                                annot_mstep, annot_vstep)
        self._draw_histogram(x_positions, std_x)
        
        # Set main title
        self.fig.suptitle(f"{title_prefix}Waterslide Sandbag Landing Analysis", 
                         fontsize=14, fontweight='bold')
        self.fig.tight_layout(rect=[0, 0, 1, 0.95])
        
        # Update canvas
        if self.interactive:
            self.fig.canvas.draw_idle()
            if pause_seconds > 0:
                plt.pause(pause_seconds)
    
    def _draw_overhead_view(self,
                           x_positions: np.ndarray,
                           y_positions: np.ndarray,
                           std_x: float,
                           std_y: float,
                           annot_mean: Optional[Tuple[float, float]],
                           annot_variance: Optional[float],
                           annot_frac: Optional[float],
                           annot_scale_idx: Optional[int],
                           annot_total_scales: Optional[int],
                           annot_mstep: Optional[float],
                           annot_vstep: Optional[float]) -> None:
        """Draw the overhead view (left panel) with pool, bags, and annotations."""
        self.ax1.set_title("Overhead View: Landing Positions", fontsize=12, fontweight='bold')
        self.ax1.set_aspect('equal')
        
        # Calculate statistics
        distances = np.sqrt(x_positions**2 + y_positions**2)
        in_pool = distances <= self.pool_radius
        out_of_pool = ~in_pool
        
        num_in_pool = int(np.sum(in_pool))
        num_out = int(np.sum(out_of_pool))
        percent_in_pool = (num_in_pool / len(x_positions)) * 100 if len(x_positions) > 0 else 0.0
        
        # Determine plot limits
        plot_limit = max(self.pool_radius * 1.5, 
                        np.max(np.abs([x_positions, y_positions])) * 1.1 if x_positions.size else self.pool_radius)
        
        # Draw background zones
        self._draw_zones(plot_limit)
        
        # Draw target circles
        self._draw_target_circles(std_x, std_y)
        
        # Plot sandbags
        self._draw_sandbags(x_positions, y_positions, in_pool, out_of_pool, 
                           num_in_pool, num_out, percent_in_pool)
        
        # Draw target center marker
        self.ax1.plot(0, 0, 'y*', markersize=35, markeredgecolor='black',
                     markeredgewidth=2, label='Target Center (Mean)', zorder=10)
        
        # Set axis properties
        self.ax1.set_xlim(-plot_limit, plot_limit)
        self.ax1.set_ylim(-plot_limit, plot_limit)
        self.ax1.set_xlabel('Distance from Center (meters)', fontsize=12, fontweight='bold')
        self.ax1.set_ylabel('Distance from Center (meters)', fontsize=12, fontweight='bold')
        self.ax1.legend(loc='upper right', fontsize=10, framealpha=0.95)
        self.ax1.grid(True, alpha=0.3)
        
        # Add statistics text box
        self._add_statistics_box(len(x_positions), num_in_pool, num_out, 
                                percent_in_pool, distances)
        
        # Add optimizer annotation if provided
        if annot_mean is not None and annot_variance is not None and annot_frac is not None:
            self._add_optimizer_annotation(x_positions, y_positions, annot_mean, 
                                          annot_variance, annot_frac, annot_scale_idx,
                                          annot_total_scales, annot_mstep, annot_vstep)
    
    def _draw_zones(self, plot_limit: float) -> None:
        """Draw the concrete danger zone and pool safe zone."""
        theta = np.linspace(0, 2*np.pi, 100)
        
        # Outer concrete zone
        outer_x = plot_limit * np.cos(theta)
        outer_y = plot_limit * np.sin(theta)
        self.ax1.fill(outer_x, outer_y, color='gray', alpha=0.2, label='Concrete (Danger Zone)')
        
        # Pool safe zone
        pool_x = self.pool_radius * np.cos(theta)
        pool_y = self.pool_radius * np.sin(theta)
        self.ax1.fill(pool_x, pool_y, color='white', alpha=1)
        
        pool = Circle((0, 0), self.pool_radius, fill=True,
                     facecolor='lightblue', edgecolor='blue',
                     linewidth=4, alpha=0.3, label='Pool (Safe Zone)')
        self.ax1.add_patch(pool)
    
    def _draw_target_circles(self, std_x: float, std_y: float) -> None:
        """Draw target radius, mean tolerance, and sigma circles."""
        # Target radius circle
        if self.target_radius is not None:
            target_circle = Circle((0, 0), self.target_radius,
                                  fill=False, edgecolor='red', linewidth=3,
                                  linestyle='-', alpha=0.8, 
                                  label=f'Target Radius ({self.target_radius}m)')
            self.ax1.add_patch(target_circle)
        
        # Mean tolerance circle
        if self.target_mean_tolerance is not None:
            mean_tolerance_circle = Circle((0, 0), self.target_mean_tolerance,
                                          fill=False, edgecolor='orange', linewidth=2,
                                          linestyle=':', alpha=0.7, 
                                          label=f'Mean Tolerance ({self.target_mean_tolerance}m)')
            self.ax1.add_patch(mean_tolerance_circle)
        
        # Standard deviation circles
        avg_std = np.mean([std_x, std_y])
        for i in range(1, 4):
            std_circle = Circle((0, 0), i * avg_std,
                               fill=False, edgecolor='green', linewidth=2,
                               linestyle='--', alpha=0.5)
            self.ax1.add_patch(std_circle)
            if i == 1:
                self.ax1.text(0, i * avg_std + 0.3, f'{i}σ', fontsize=10, ha='center',
                            color='green', fontweight='bold')
    
    def _draw_sandbags(self, 
                      x_positions: np.ndarray,
                      y_positions: np.ndarray,
                      in_pool: np.ndarray,
                      out_of_pool: np.ndarray,
                      num_in_pool: int,
                      num_out: int,
                      percent_in_pool: float) -> None:
        """Draw sandbag scatter points (green circles for in-pool, red X for out)."""
        if np.any(in_pool):
            self.ax1.scatter(x_positions[in_pool], y_positions[in_pool],
                           c='green', s=80, alpha=0.7, edgecolors='darkgreen',
                           linewidth=1.5, label=f'In Pool: {num_in_pool} ({percent_in_pool:.1f}%)',
                           zorder=5)
        
        if np.any(out_of_pool):
            self.ax1.scatter(x_positions[out_of_pool], y_positions[out_of_pool],
                           c='red', s=100, marker='X', alpha=0.9,
                           edgecolors='darkred', linewidth=2,
                           label=f'On Concrete: {num_out} ({100-percent_in_pool:.1f}%)',
                           zorder=5)
    
    def _add_statistics_box(self, 
                           total: int, 
                           num_in_pool: int, 
                           num_out: int,
                           percent_in_pool: float,
                           distances: np.ndarray) -> None:
        """Add statistics text box to the overhead view."""
        textstr = f'Total Bags: {total}\n'
        textstr += f'In Pool: {num_in_pool} ({percent_in_pool:.1f}%)\n'
        textstr += f'On Concrete: {num_out} ({100-percent_in_pool:.1f}%)\n'
        textstr += f'Mean Distance: {np.mean(distances):.2f}m\n'
        textstr += f'Max Distance: {np.max(distances):.2f}m'
        
        self.ax1.text(0.02, 0.02, textstr, transform=self.ax1.transAxes,
                     fontsize=11, verticalalignment='bottom',
                     bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
    
    def _add_optimizer_annotation(self,
                                 x_positions: np.ndarray,
                                 y_positions: np.ndarray,
                                 annot_mean: Tuple[float, float],
                                 annot_variance: float,
                                 annot_frac: float,
                                 annot_scale_idx: Optional[int],
                                 annot_total_scales: Optional[int],
                                 annot_mstep: Optional[float],
                                 annot_vstep: Optional[float]) -> None:
        """Add optimizer status annotation box."""
        lines = ["Optimization"]
        
        # Scale info
        if annot_scale_idx is not None and annot_total_scales is not None:
            if annot_scale_idx < annot_total_scales:
                lines.append(f"Scale: {annot_scale_idx + 1}/{annot_total_scales}")
            else:
                lines.append(f"Scale: {annot_scale_idx + 1} (extra refinement)")
        
        # Optimizer parameters
        lines.append(f"Mean: ({annot_mean[0]:.2f}, {annot_mean[1]:.2f})")
        lines.append(f"Variance: {annot_variance:.3f} (σ={np.sqrt(annot_variance):.2f})")
        lines.append(f"In-pool: {annot_frac * 100:.1f}%")
        
        if annot_mstep is not None and annot_vstep is not None:
            lines.append(f"Step (mean, var): ({annot_mstep:.3f}, {annot_vstep:.3f})")
        
        # Goal status
        distances = np.sqrt(x_positions**2 + y_positions**2)
        max_dist = float(np.max(distances))
        actual_mean_x = float(np.mean(x_positions))
        actual_mean_y = float(np.mean(y_positions))
        actual_mean_dist = float(np.sqrt(actual_mean_x**2 + actual_mean_y**2))
        
        goals_met = True
        
        if self.target_radius is not None:
            all_within_target = np.all(distances <= self.target_radius)
            lines.append(f"Max dist: {max_dist:.2f}m vs target={self.target_radius}m")
            if all_within_target:
                lines.append(f"✓ All within {self.target_radius}m!")
            else:
                goals_met = False
        
        if self.target_mean_tolerance is not None:
            mean_within_tol = actual_mean_dist <= self.target_mean_tolerance
            lines.append(f"Mean dist: {actual_mean_dist:.3f}m vs tol={self.target_mean_tolerance}m")
            if mean_within_tol:
                lines.append(f"✓ Mean within {self.target_mean_tolerance}m!")
            else:
                goals_met = False
        
        if self.target_radius is None and self.target_mean_tolerance is None:
            lines.append(f"Max dist: {max_dist:.2f}m")
            lines.append(f"Mean dist: {actual_mean_dist:.3f}m")
            goals_met = False
        
        overlay = "\n".join(lines)
        self.ax1.text(0.02, 0.98, overlay, transform=self.ax1.transAxes,
                     fontsize=10, va='top', ha='left',
                     bbox=dict(boxstyle='round', 
                              facecolor='lightgreen' if goals_met else 'white',
                              edgecolor='gray', alpha=0.9))
    
    def _draw_histogram(self, x_positions: np.ndarray, std_x: float) -> None:
        """Draw the histogram (right panel) showing distribution of x positions."""
        self.ax2.set_title('Distribution of Landing Positions\n(Centered at Target Mean = 0)', 
                          fontsize=14, fontweight='bold')
        
        bins = 40
        self.ax2.hist(x_positions, bins=bins, color='steelblue', edgecolor='black', alpha=0.7)
        
        # Reference lines
        self.ax2.axvline(0, color='green', linestyle='-', linewidth=3, label='Target Mean (0m)')
        self.ax2.axvline(-self.pool_radius, color='red', linestyle='--', linewidth=2,
                        label=f'Pool Edges (±{self.pool_radius}m)', alpha=0.7)
        self.ax2.axvline(self.pool_radius, color='red', linestyle='--', linewidth=2, alpha=0.7)
        
        # Sigma lines
        self.ax2.axvline(-std_x, color='orange', linestyle=':', linewidth=2,
                        label=f'±1σ (±{std_x:.2f}m)', alpha=0.7)
        self.ax2.axvline(std_x, color='orange', linestyle=':', linewidth=2, alpha=0.7)
        self.ax2.axvline(-2*std_x, color='purple', linestyle=':', linewidth=2,
                        label=f'±2σ (±{2*std_x:.2f}m)', alpha=0.7)
        self.ax2.axvline(2*std_x, color='purple', linestyle=':', linewidth=2, alpha=0.7)
        
        # Safe zone shading
        self.ax2.axvspan(-self.pool_radius, self.pool_radius, alpha=0.1, color='blue', 
                        label='Safe Zone (Inside Pool)')
        
        # Labels and legend
        self.ax2.set_xlabel('Distance from Target (meters)\n← Left | Center (0) | Right →', 
                           fontsize=12, fontweight='bold')
        self.ax2.set_ylabel('Number of Sandbags', fontsize=12, fontweight='bold')
        self.ax2.legend(fontsize=9, loc='upper right')
        self.ax2.grid(axis='y', alpha=0.3)
        
        # Statistics box
        stats_text = f'Mean: {np.mean(x_positions):.2f}m\n'
        stats_text += f'Std Dev: {np.std(x_positions):.2f}m\n'
        stats_text += f'Range: [{np.min(x_positions):.2f}, {np.max(x_positions):.2f}]m'
        
        self.ax2.text(0.02, 0.98, stats_text, transform=self.ax2.transAxes,
                     fontsize=10, verticalalignment='top',
                     bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    def show(self, block: bool = True) -> None:
        """Display the figure."""
        if self.interactive:
            plt.ioff()
        plt.show(block=block)
