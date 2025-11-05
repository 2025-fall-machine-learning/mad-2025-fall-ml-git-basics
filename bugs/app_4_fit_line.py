import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def fit_best_line(x, y):
    """Return slope and intercept of the best fit line for y ~ m*x + b."""
    # Ensure numpy float arrays
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.size == 0 or y.size == 0:
        raise ValueError("x and y must be non-empty arrays")
    if x.size != y.size:
        raise ValueError("x and y must have the same length")

    # Compute means
    x_mean = float(np.mean(x))
    y_mean = float(np.mean(y))

    # Sum of squares.
    Sxx=0
    Sxy=0
    for xi, yi in zip(x, y):
        # print (f"xi: {xi}, yi: {yi}")  # Debugging output
        dx = xi - x_mean
        dy = yi - y_mean
        Sxx += dx * dx
        Sxy += dy * dx
        # print(f"xi: {xi}, yi: {yi} dx: {dx}, dy: {dy}, Sxx: {Sxx}, Sxy: {Sxy}")  # Debugging output
    if Sxx == 0:
        raise ValueError("Cannot compute slope: all x values are identical")

    # Least squares estimates
    m =  Sxy / Sxx
    b = y_mean - (m * x_mean)
    return m, b


def main():
    """ Plot 12,000 points with R² ≈ 0.75."""

    # Read data from CSV file
    csv_filename = 'data_points.csv'
    df = pd.read_csv(csv_filename)
    x = df['x'].values
    y = df['y'].values
    print(f"Data loaded from {csv_filename}")

    # Compute best fit line
    m, b = fit_best_line(x, y)
    x_line = np.linspace(x.min(), x.max(), 500)
    y_line = m * x_line + b
    print(f" {m}, {b}")

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.scatter(x, y, alpha=0.3, s=5, color='blue', edgecolors='none')
    plt.plot(x_line, y_line, color='red', linewidth=2, label=f'Best fit: y = {m:.2f}x + {b:.2f}')
    plt.legend()
    
    # Labels and title
    plt.xlabel('X Values', fontsize=12)
    plt.ylabel('Y Values', fontsize=12)
    plt.title('Scatter Plot of 12,000 Points (Target R² ≈ 0.75)', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    
    # Show the plot
    plt.tight_layout()
    plt.show()
    
    # Print some statistics
    print(f"Number of points: {len(x)}")
    print(f"X range: [{x.min():.2f}, {x.max():.2f}]")
    print(f"Y range: [{y.min():.2f}, {y.max():.2f}]")
    print(f"Best fit line: y = {m:.3f}x + {b:.3f}")


if __name__ == "__main__":
    main()
