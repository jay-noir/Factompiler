# Missing Features and Roadmap

This document outlines features that are planned but not yet implemented in Facto.

---

## Selector Combinators (Implemented)

Factorio 2.0 selector combinators are supported with native Facto functions
and explicitly placed entities. See [Entity documentation](05_entities.md#selector-combinators)
for all seven modes and their configuration.

```facto
Bundle resources = { ("iron-plate", 100), ("copper-plate", 80) };
Bundle highest = select_max(resources);
Bundle third_lowest = select_index(resources, 2, 0);
Signal count = count_signals(resources, "signal-C");
Bundle stacks = stack_size(resources);
```

Selector functions emit native `selector-combinator` entities with circuit
inputs and outputs, not simulated arithmetic or decider networks. Selector
outputs whose signal type depends on runtime input are Bundles.

---

## Entity Arrays

Currently, entities must be placed individually:

```facto
Entity lamp1 = place("small-lamp", 0, 0);
Entity lamp2 = place("small-lamp", 1, 0);
Entity lamp3 = place("small-lamp", 2, 0);
```

A future feature would allow **entity arrays** for dynamic placement using for-loops:

```facto
# Proposed syntax - NOT YET IMPLEMENTED
Entity[10] lamps;
for i in 0..10 {
    lamps[i] = place("small-lamp", i, 0);
    lamps[i].enable = counter.read() > i;
}
```

This would enable:
- Creating rows/grids of entities with a single loop
- Dynamic indexing and configuration
- More concise blueprints for repetitive structures

---

## Web-Based Compiler Platform

A web-based version of the Facto compiler is planned, which would allow:

- **In-browser compilation**: Write and compile Facto code without installing anything
- **Blueprint preview**: Visual preview of the generated circuit layout
- **Interactive examples**: Try sample programs directly in the browser
- **Sharing**: Generate shareable links to Facto programs

This will lower the barrier to entry for new users and enable quick experimentation without local setup.

---

## Other Planned Features

Additional features under consideration:

- **Display panel support**: Control display panels for in-game text output
- **Interrupt signals**: Support for interrupt-based control flow
- **Blueprint books**: Generate blueprint books containing multiple related circuits
- **Import from blueprint**: Reverse-compile existing blueprints to Facto code for modification
