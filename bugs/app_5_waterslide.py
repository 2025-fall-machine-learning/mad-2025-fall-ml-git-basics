import numpy as np
from typing import Sequence, Callable, Optional
from App5Plot import App5Plot


def simulate_waterslide_landings(num_bags: int,
                                 variance_x: float,
                                 variance_y: float,
                                 pool_center: tuple[float, float] = (0.0, 0.0)):
    """
    Simulate sandbag landings after coming down a waterslide.

    Args:
        num_bags: Number of sandbags to drop.
        variance_x: Variance of x-landing positions.
        variance_y: Variance of y-landing positions.
        pool_center: Mean landing location (x, y).

    Returns:
        (x_positions, y_positions): Two numpy arrays of length num_bags.
    """
    std_x = float(np.sqrt(variance_x))
    std_y = float(np.sqrt(variance_y))
    mean_x, mean_y = pool_center

    x_positions = np.random.normal(loc=mean_x, scale=std_x, size=num_bags)
    y_positions = np.random.normal(loc=mean_y, scale=std_y, size=num_bags)
    return x_positions, y_positions


def compute_in_pool_fraction(x_positions: np.ndarray,
                             y_positions: np.ndarray,
                             pool_radius: float) -> float:
    """Return the fraction of landings inside the pool radius."""
    if x_positions.size == 0:
        return 0.0
    distances = np.sqrt(x_positions**2 + y_positions**2)
    return float(np.mean(distances <= pool_radius))


def optimize_mean_and_variance(num_bags: int,
                               pool_radius: float,
                               init_mean: tuple[float, float],
                               init_variance: float,
                               mean_steps: Sequence[float] = (1.0, 0.5, 0.25),
                               var_steps: Sequence[float] = (1.0, 0.5, 0.25),
                               max_iters_per_scale: int = 50,
                               var_bounds: tuple[float, float] = (0.05, 25.0),
                               on_improve: Optional[Callable[[tuple[float, float], float, np.ndarray, np.ndarray, float, int], None]] = None,
                               replicates: int = 3,
                               epsilon: float = 1e-3,
                               target_radius: Optional[float] = None,
                               target_mean_tolerance: Optional[float] = None,
                               ) -> tuple[tuple[float, float], float, np.ndarray, np.ndarray, float]:
    """
    Hill-climb the (mean_x, mean_y) and symmetric variance.
    
    When target_radius is set: minimize variance while keeping all bags within that radius.
    When target_mean_tolerance is set: also require the actual mean to be within tolerance of (0,0).
    Otherwise: maximize fraction of landings inside the pool.

    Returns: (best_mean, best_variance, best_x, best_y, best_fraction)
    """
    mean = np.array(init_mean, dtype=float)
    variance = float(init_variance)
    var_min, var_max = var_bounds

    def goals_met_for_samples(xs: np.ndarray, ys: np.ndarray) -> bool:
        if target_radius is None and target_mean_tolerance is None:
            return False  # No strict goal; handled by fraction objective
        distances = np.sqrt(xs**2 + ys**2)
        within_radius = True
        if target_radius is not None:
            within_radius = bool(np.all(distances <= float(target_radius)))
        mean_ok = True
        if target_mean_tolerance is not None:
            mx = float(np.mean(xs))
            my = float(np.mean(ys))
            mean_dist = float(np.sqrt(mx*mx + my*my))
            mean_ok = mean_dist <= float(target_mean_tolerance)
        return within_radius and mean_ok

    def score_samples(xs: np.ndarray, ys: np.ndarray, v: float) -> float:
        # Higher is better
        if target_radius is None and target_mean_tolerance is None:
            return compute_in_pool_fraction(xs, ys, pool_radius)
        distances = np.sqrt(xs**2 + ys**2)
        max_dist = float(np.max(distances)) if distances.size else 0.0
        # Penalties for violating constraints
        penalty = 0.0
        if target_radius is not None:
            if np.any(distances > float(target_radius)):
                penalty -= 1000.0 + (max_dist - float(target_radius))
        if target_mean_tolerance is not None:
            mx = float(np.mean(xs))
            my = float(np.mean(ys))
            mean_dist = float(np.sqrt(mx*mx + my*my))
            if mean_dist > float(target_mean_tolerance):
                penalty -= 200.0 + (mean_dist - float(target_mean_tolerance))
        # If constraints satisfied, prefer lower variance. Return a large
        # positive score that prefers lower variance so that higher-is-better
        # holds consistently. When constraints are violated, return a
        # large negative penalty.
        if penalty == 0.0:
            return 1000.0 - float(v)
        return penalty

    def estimate_objective(m: np.ndarray, v: float, reps: int) -> tuple[float, np.ndarray, np.ndarray, float]:
        scores = []
        xs_keep: np.ndarray | None = None
        ys_keep: np.ndarray | None = None
        frac_keep: float = 0.0
        for _ in range(reps):
            xs, ys = simulate_waterslide_landings(num_bags, v, v, pool_center=tuple(m))
            s = score_samples(xs, ys, v)
            scores.append(s)
            # Track a representative sample (prefer goal-satisfying)
            if xs_keep is None:
                xs_keep, ys_keep = xs, ys
                frac_keep = compute_in_pool_fraction(xs, ys, pool_radius)
            else:
                # Prefer satisfying goals; else higher fraction
                if (target_radius is not None) or (target_mean_tolerance is not None):
                    if goals_met_for_samples(xs, ys) and not goals_met_for_samples(xs_keep, ys_keep):
                        xs_keep, ys_keep = xs, ys
                        frac_keep = compute_in_pool_fraction(xs, ys, pool_radius)
                    elif (not goals_met_for_samples(xs, ys) and not goals_met_for_samples(xs_keep, ys_keep)
                          and compute_in_pool_fraction(xs, ys, pool_radius) > frac_keep):
                        xs_keep, ys_keep = xs, ys
                        frac_keep = compute_in_pool_fraction(xs, ys, pool_radius)
                else:
                    f = compute_in_pool_fraction(xs, ys, pool_radius)
                    if f > frac_keep:
                        xs_keep, ys_keep = xs, ys
                        frac_keep = f
        return float(np.mean(scores)), xs_keep if xs_keep is not None else np.array([]), ys_keep if ys_keep is not None else np.array([]), frac_keep

    best_mean = mean.copy()
    best_variance = variance
    best_x = np.array([])
    best_y = np.array([])
    best_frac = 0.0

    # Initial baseline
    base_score, base_x, base_y, base_frac = estimate_objective(mean, variance, replicates)
    best_x, best_y, best_frac = base_x, base_y, base_frac

    for scale_idx in range(max(len(mean_steps), len(var_steps))):
        mstep = mean_steps[scale_idx] if scale_idx < len(mean_steps) else mean_steps[-1] * 0.5 ** (scale_idx - len(mean_steps) + 1)
        vstep = var_steps[scale_idx] if scale_idx < len(var_steps) else var_steps[-1] * 0.5 ** (scale_idx - len(var_steps) + 1)

        for _ in range(max_iters_per_scale):
            candidates: list[tuple[np.ndarray, float, float, np.ndarray, np.ndarray, float]] = []

            # Mean moves (cardinal and diagonals)
            dirs = [
                np.array([ mstep,  0.0]), np.array([-mstep,  0.0]),
                np.array([ 0.0 ,  mstep]), np.array([ 0.0 , -mstep]),
                np.array([ mstep,  mstep]), np.array([ mstep, -mstep]),
                np.array([-mstep,  mstep]), np.array([-mstep, -mstep]),
                np.array([ 0.0 ,  0.0])  # no-op
            ]
            for d in dirs:
                m2 = mean + d
                score, xs, ys, frac = estimate_objective(m2, variance, replicates)
                candidates.append((m2, variance, score, xs, ys, frac))

            # Variance moves
            for dv in (-vstep, vstep):
                v2 = float(np.clip(variance + dv, var_min, var_max))
                score, xs, ys, frac = estimate_objective(mean, v2, replicates)
                candidates.append((mean.copy(), v2, score, xs, ys, frac))

            # Choose best (candidates sorted by score, high->low)
            candidates.sort(key=lambda t: t[2], reverse=True)
            best_m2, best_v2, best_score2, xs2, ys2, frac2 = candidates[0]

            # Improvement threshold: accept only if the candidate score is
            # better than the baseline by at least epsilon. The previous
            # comparison was inverted and accepted worse solutions.
            if best_score2 > base_score + float(epsilon):
                # Accept move (improvement)
                mean = best_m2
                variance = best_v2
                base_score = best_score2
                best_x, best_y, best_frac = xs2, ys2, frac2
                best_mean = mean.copy()
                best_variance = variance
                if on_improve is not None:
                    on_improve(tuple(mean), variance, best_x, best_y, best_frac, scale_idx)
            else:
                # No improvement at this scale
                break

    # Final best sample if empty
    if best_x.size == 0 or best_y.size == 0:
        _, best_x, best_y, best_frac = estimate_objective(best_mean, best_variance, replicates)

    # Extra refinement: keep going until goals are met or we hit limits
    if target_radius is not None or target_mean_tolerance is not None:
        extra_scale = max(len(mean_steps), len(var_steps))
        extra_iters = 0
        max_extra_iters = 200
        curr_vstep = var_steps[-1] if len(var_steps) > 0 else 0.25
        # Put the while-loop inside the same block so variables like
        # `extra_iters` and `curr_vstep` are defined when used. Previously
        # the while was dedented which caused a NameError/logic bug.
        while extra_iters < max_extra_iters:
            # Check goals on a fresh sample using current best params
            xs_chk, ys_chk = simulate_waterslide_landings(num_bags, best_variance, best_variance, pool_center=tuple(best_mean))
            if goals_met_for_samples(xs_chk, ys_chk):
                best_x, best_y = xs_chk, ys_chk
                best_frac = compute_in_pool_fraction(xs_chk, ys_chk, pool_radius)
                break

            # Try decreasing variance aggressively
            v2 = float(np.clip(best_variance - curr_vstep, var_min, var_max))
            # If cannot decrease further, reduce step and continue
            if abs(v2 - best_variance) < 1e-9:
                curr_vstep *= 0.5
                if curr_vstep < 1e-3:
                    # Also try tiny mean tweaks
                    for d in [np.array([1e-2, 0.0]), np.array([-1e-2, 0.0]), np.array([0.0, 1e-2]), np.array([0.0, -1e-2])]:
                        m2 = np.array(best_mean) + d
                        xs2, ys2 = simulate_waterslide_landings(num_bags, best_variance, best_variance, pool_center=tuple(m2))
                        if goals_met_for_samples(xs2, ys2):
                            best_mean = m2
                            best_x, best_y = xs2, ys2
                            best_frac = compute_in_pool_fraction(xs2, ys2, pool_radius)
                            if on_improve is not None:
                                on_improve(tuple(best_mean), best_variance, best_x, best_y, best_frac, extra_scale + extra_iters)
                            break
                    break
                extra_iters += 1
                continue

            # Unconditionally reduce variance while goals unmet to force convergence
            best_variance = v2
            xs2, ys2 = simulate_waterslide_landings(num_bags, best_variance, best_variance, pool_center=tuple(best_mean))
            best_x, best_y = xs2, ys2
            best_frac = compute_in_pool_fraction(xs2, ys2, pool_radius)
            if on_improve is not None:
                on_improve(tuple(best_mean), best_variance, best_x, best_y, best_frac, extra_scale + extra_iters)
            extra_iters += 1

    return (tuple(best_mean), float(best_variance), best_x, best_y, float(best_frac))


def main() -> None:
    np.random.seed(42)
    num_bags = 200
    pool_radius = 5.0  # meters

    # Initial settings: worst-case variance and off-target mean
    init_variance = 7.5
    init_mean = (2.85, -2.85)

    # Optimizer parameters
    pause_seconds = 0.3  # Comfortable viewing speed
    mean_steps = (1.0, 0.5, 0.25)
    var_steps = (1.0, 0.5, 0.25)
    target_radius = 2.0  # Goal: all bags within 2m of center
    target_mean_tolerance = 0.5  # Goal: actual mean within 0.5m of center

    # Create plotter
    plotter = App5Plot(pool_radius=pool_radius,
                      target_radius=target_radius,
                      target_mean_tolerance=target_mean_tolerance,
                      interactive=True)
    fig, ax1, ax2 = plotter.create_figure()

    def on_improve(mean: tuple[float, float], variance: float, x: np.ndarray, y: np.ndarray, frac: float, scale_idx: int) -> None:
        std_curr = float(np.sqrt(variance))
        # Compute current step sizes
        if scale_idx < len(mean_steps):
            mstep = mean_steps[scale_idx]
            vstep = var_steps[scale_idx]
        else:
            # Extra refinement beyond predefined steps
            mstep = mean_steps[-1] * 0.5 ** (scale_idx - len(mean_steps) + 1)
            vstep = var_steps[-1] * 0.5 ** (scale_idx - len(var_steps) + 1)
        
        plotter.draw(
            x, y, std_curr, std_curr,
            title_prefix="",
            annot_mean=mean,
            annot_variance=variance,
            annot_frac=frac,
            annot_scale_idx=scale_idx,
            annot_total_scales=len(mean_steps),
            annot_mstep=mstep,
            annot_vstep=vstep,
            pause_seconds=pause_seconds
        )

    best_mean, best_variance, best_x, best_y, best_frac = optimize_mean_and_variance(
        num_bags=num_bags,
        pool_radius=pool_radius,
        init_mean=init_mean,
        init_variance=init_variance,
        mean_steps=mean_steps,
        var_steps=var_steps,
        max_iters_per_scale=50,
        var_bounds=(0.05, 25.0),
        on_improve=on_improve,
        replicates=3,
        epsilon=5e-3,
        target_radius=target_radius,  # Continue until all bags within target radius
        target_mean_tolerance=target_mean_tolerance,  # And mean within tolerance
    )

    std_final = float(np.sqrt(best_variance))
    print(f"Optimized mean: ({best_mean[0]:.2f}, {best_mean[1]:.2f}) | variance: {best_variance:.3f} | in-pool: {best_frac*100:.1f}%")
    
    # Check final state
    distances_final = np.sqrt(best_x**2 + best_y**2)
    max_dist_final = float(np.max(distances_final))
    all_within_target = bool(np.all(distances_final <= target_radius))
    actual_mean_x_final = float(np.mean(best_x))
    actual_mean_y_final = float(np.mean(best_y))
    actual_mean_dist_final = float(np.sqrt(actual_mean_x_final**2 + actual_mean_y_final**2))
    mean_within_tol = bool(actual_mean_dist_final <= target_mean_tolerance)
    print(f"Max distance: {max_dist_final:.2f}m | Target radius: {target_radius}m | All within target: {all_within_target}")
    print(f"Mean distance: {actual_mean_dist_final:.3f}m | Mean tolerance: {target_mean_tolerance}m | Mean within tolerance: {mean_within_tol}")

    # Final render
    final_scale_idx = len(mean_steps) - 1
    plotter.draw(
        best_x, best_y, std_final, std_final,
        title_prefix="",
        annot_mean=best_mean,
        annot_variance=best_variance,
        annot_frac=best_frac,
        annot_scale_idx=final_scale_idx,
        annot_total_scales=len(mean_steps),
        annot_mstep=mean_steps[-1],
        annot_vstep=var_steps[-1],
        pause_seconds=0.0
    )
    
    plotter.show()


if __name__ == "__main__":
    main()