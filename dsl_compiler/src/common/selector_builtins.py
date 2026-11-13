"""Native selector-combinator functions and their positional argument arities."""

# All return dynamic Bundles except count_signals, which outputs one named Signal.
SELECTOR_BUILTINS = {
    "select_max": (1, 1),
    "select_min": (1, 1),
    "select_index": (2, 3),
    "count_signals": (1, 2),
    "random_input": (1, 2),
    "stack_size": (1, 1),
    "rocket_capacity": (1, 1),
    "quality_filter": (2, 3),
    "quality_transfer": (2, 3),
    "quality_transfer_signal": (2, 3),
}
