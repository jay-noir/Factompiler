"""End-to-end tests for Factorio 2.0 selector combinators."""

import pytest

from dsl_compiler.src.common.diagnostics import ProgramDiagnostics
from dsl_compiler.src.emission.emitter import BlueprintEmitter
from dsl_compiler.src.layout.planner import LayoutPlanner
from dsl_compiler.src.lowering.lowerer import ASTLowerer
from dsl_compiler.src.parsing.parser import DSLParser
from dsl_compiler.src.semantic.analyzer import SemanticAnalyzer


def compile_selector(source):
    diagnostics = ProgramDiagnostics()
    ast = DSLParser().parse(source, "<selector-test>")
    semantic = SemanticAnalyzer(diagnostics)
    semantic.visit(ast)
    assert diagnostics.error_count() == 0, "semantic diagnostics"
    lowerer = ASTLowerer(semantic, diagnostics)
    operations = lowerer.lower_program(ast)
    assert diagnostics.error_count() == 0, "lowering diagnostics"
    layout = LayoutPlanner(
        lowerer.ir_builder.signal_type_map,
        diagnostics,
        signal_refs=lowerer.signal_refs,
        referenced_signal_names=lowerer.referenced_signal_names,
    ).plan_layout(operations)
    blueprint = BlueprintEmitter(diagnostics, lowerer.ir_builder.signal_type_map).emit_from_plan(
        layout
    )
    assert diagnostics.error_count() == 0, "layout or emission diagnostics"
    return blueprint.to_dict()["blueprint"]


ITEMS = 'Bundle items = { ("iron-plate", 5), ("copper-plate", 10) };'


@pytest.mark.parametrize(
    ("declaration", "operation", "expected"),
    [
        ('Bundle result = select_max(items);', "select", {}),
        ('Bundle result = select_min(items);', "select", {"select_max": False}),
        (
            'Bundle result = select_index(items, 2, 0);',
            "select",
            {"index_constant": 2, "select_max": False},
        ),
        ('Signal result = count_signals(items, "signal-C");', "count", {}),
        (
            'Bundle result = random_input(items, 60);',
            "random",
            {"random_update_interval": 60},
        ),
        ('Bundle result = stack_size(items);', "stack-size", {}),
        ('Bundle result = rocket_capacity(items);', "rocket-capacity", {}),
        ('Bundle result = quality_filter(items, "rare", ">=");', "quality-filter", {}),
        ('Bundle result = quality_transfer(items, "rare");', "quality-transfer", {}),
        (
            'Bundle result = quality_transfer_signal(items, "signal-Q");',
            "quality-transfer",
            {"select_quality_from_signal": True},
        ),
    ],
)
def test_native_selector_builtin(declaration, operation, expected):
    blueprint = compile_selector(ITEMS + "\n" + declaration)
    selectors = [
        entity for entity in blueprint["entities"] if entity["name"] == "selector-combinator"
    ]
    assert len(selectors) == 1
    behavior = selectors[0]["control_behavior"]
    assert behavior["operation"] == operation
    for key, value in expected.items():
        assert behavior[key] == value
    # A selector with input signals must be wired to the source network.
    connected = [
        wire for wire in blueprint.get("wires", []) if selectors[0]["entity_number"] in wire[::2]
    ]
    assert connected


def test_dynamic_index_signal_is_connected_and_configured():
    blueprint = compile_selector(
        ITEMS
        + '\nSignal index = ("signal-I", 2);'
        + "\nBundle result = select_index(items, index);"
    )
    selector = next(e for e in blueprint["entities"] if e["name"] == "selector-combinator")
    assert selector["control_behavior"]["index_signal"]["name"] == "signal-I"
    assert blueprint.get("wires")


def test_manual_selector_uses_minimal_select_control_behavior():
    blueprint = compile_selector(
        'Entity select_1 = place("selector-combinator", 0, 0, {'
        'operation: "select", direction: 4});'
    )
    selector = next(e for e in blueprint["entities"] if e["name"] == "selector-combinator")
    assert selector["control_behavior"]["operation"] == "select"
    assert selector["direction"] == 4


def test_manual_selector_count_mode_serializes_output_signal():
    blueprint = compile_selector(
        'Entity counter = place("selector-combinator", 0, 0, {'
        'operation: "count", count_signal: "signal-C"});'
    )
    selector = next(e for e in blueprint["entities"] if e["name"] == "selector-combinator")
    assert selector["control_behavior"]["operation"] == "count"
    assert selector["control_behavior"]["count_signal"]["name"] == "signal-C"


@pytest.mark.parametrize(
    "source",
    [
        'Signal chosen = select_min(items)["iron-plate"];',
        'Bundle lowest = select_min(items);\nSignal chosen = lowest["iron-plate"];',
        'Signal recipe = ("iron-plate", 1);\n'
        'Bundle lowest = select_min(items);\nSignal chosen = lowest[recipe.type];',
        'Bundle lowest = select_min(items);\n'
        'Bundle doubled = lowest * 2;\nSignal chosen = doubled["iron-plate"];',
        'Bundle lowest = select_min(items);\n'
        'Bundle filtered = (lowest > 0) : lowest;\n'
        'Signal chosen = filtered["iron-plate"];',
        'Bundle lowest = select_min(items);\n'
        'Bundle combined = { lowest, ("signal-A", 1) };\n'
        'Signal chosen = combined["iron-plate"];',
    ],
)
def test_dynamic_selector_output_can_be_indexed_by_known_signal(source):
    blueprint = compile_selector(ITEMS + "\n" + source + "\nSignal used = chosen + 1;")
    assert any(e["name"] == "selector-combinator" for e in blueprint["entities"])
    assert any(e["name"] == "arithmetic-combinator" for e in blueprint["entities"])


def test_static_bundle_still_rejects_missing_signal():
    diagnostics = ProgramDiagnostics()
    ast = DSLParser().parse(
        'Bundle fixed = { ("iron-plate", 5) };'
        'Signal missing = fixed["copper-plate"];',
        "<static-bundle-test>",
    )
    SemanticAnalyzer(diagnostics).visit(ast)
    assert diagnostics.error_count() > 0
