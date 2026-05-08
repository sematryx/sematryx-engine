from sematryx_engine.solvers.scipy_solvers import solve_with_scipy


def sphere(x: list[float]) -> float:
    return sum(v * v for v in x)


def test_scipy_extended_local_methods_execute() -> None:
    bounds = [(-2.0, 2.0), (-2.0, 2.0)]
    for strategy in [
        "scipy_local_powell",
        "scipy_local_tnc",
        "scipy_local_slsqp",
        "scipy_local_cobyla",
        "scipy_local_nelder_mead",
        "scipy_local_cg",
        "scipy_shgo",
    ]:
        result = solve_with_scipy(
            strategy=strategy,
            objective_function=sphere,
            bounds=bounds,
            max_evaluations=120,
        )
        assert getattr(result, "x") is not None
        assert float(result.fun) >= 0.0
