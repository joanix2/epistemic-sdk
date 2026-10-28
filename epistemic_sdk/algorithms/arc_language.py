"""Shared taxonomy of grid languages, including explicit object representations.

Seed operators are engineering priors, not discovered scientific knowledge.
Tasks specialize versioned families; learned definitions can later enrich the
same families. The taxonomy says which operations are available, not which
empirical rule must hold for an unseen task.
"""
from collections import Counter
from collections.abc import Callable
from functools import partial
from typing import Any

from epistemic_sdk import Operator, Sort

from . import grid_transforms as transforms
from .grid_objects import (
    Grid,
    complete_bbox_reflection,
    complete_reflection,
    components,
    crop_bbox,
    fill_holes,
    object_crop,
    remove_small_objects,
    select_object,
    separator_cells,
    split_regions,
)
from .language_taxonomy import LanguageRef, LanguageTaxonomy, OperatorBinding


def _majority_components(grid: Grid, connectivity: int, monochrome: bool):
    counts = Counter(value for row in grid.cells for value in row)
    background = min(counts, key=lambda value: (-counts[value], value)) if counts else 0
    return components(grid, background, connectivity, monochrome)


def build_arc_taxonomy() -> tuple[LanguageTaxonomy, dict[str, LanguageRef]]:
    """Create a reproducible seed; registration order is also a search prior."""
    taxonomy = LanguageTaxonomy()
    root = taxonomy.define_node("grid", sorts=(Sort("Grid"),))
    orientation: dict[str, Callable[..., Any]] = {
        "flip_horizontal": transforms.flip_horizontal,
        "flip_vertical": transforms.flip_vertical,
        "rotate_90": transforms.rotate_90,
        "rotate_180": transforms.rotate_180,
        "rotate_270": transforms.rotate_270,
        "transpose": transforms.transpose,
        "anti_transpose": transforms.anti_transpose,
    }
    parts: dict[str, Callable[..., Any]] = {
        f"keep_{part}": partial(transforms.half, part=part) for part in (
            "top", "bottom", "left", "right",
            "top_left", "top_right", "bottom_left", "bottom_right")
    }
    parts.update({f"window_{anchor}": partial(transforms.window, anchor=anchor)
                  for anchor in ("start", "end")})
    resizing: dict[str, Callable[..., Any]] = {
        "crop": transforms.crop,
        "upscale_2": partial(transforms.upscale, factor=2),
        "upscale_3": partial(transforms.upscale, factor=3),
        "pad_square": transforms.pad_square,
        **{f"dedupe_{axis}": partial(transforms.dedupe, axis=axis)
           for axis in ("rows", "columns", "both")},
    }

    def bind(functions: dict[str, Callable[..., Any]]) -> tuple[OperatorBinding, ...]:
        return tuple(OperatorBinding(Operator(name, ("Grid",), "Grid"), function)
                     for name, function in functions.items())

    orientation_ref = taxonomy.define_node("orientation", parents=(root,),
                                           operators=bind(orientation))
    parts_ref = taxonomy.define_node("parts", parents=(root,), operators=bind(parts))
    global_ref = taxonomy.define_node("geometry", parents=(orientation_ref, parts_ref),
                                      operators=bind(resizing))
    object_bindings = []
    for connectivity in (4, 8):
        for monochrome in (False, True):
            name = f"components_{connectivity}_{'color' if monochrome else 'foreground'}"
            object_bindings.append(OperatorBinding(
                Operator(name, ("Grid",), "Objects"),
                partial(components, connectivity=connectivity, monochrome=monochrome),
            ))
            object_bindings.append(OperatorBinding(
                Operator(name + "_majority", ("Grid",), "Objects"),
                partial(_majority_components, connectivity=connectivity, monochrome=monochrome),
            ))
    objects_ref = taxonomy.define_node(
        "objects", parents=(root,), sorts=(Sort("Objects"), Sort("Object")),
        operators=(*object_bindings, OperatorBinding(
            Operator("separator_regions", ("Grid",), "Objects"),
            lambda grid: tuple(region for row in separator_cells(grid) for region in row),
        ), *(OperatorBinding(
            Operator(f"split_{rows}x{columns}", ("Grid",), "Objects"),
            partial(split_regions, rows=rows, columns=columns),
        ) for rows, columns in ((1, 2), (2, 1), (1, 3), (3, 1), (2, 2)))),
    )
    selection = tuple(OperatorBinding(
        Operator("select_" + criterion, ("Objects",), "Object"),
        partial(select_object, criterion=criterion),
    ) for criterion in (
        "largest", "smallest", "most_colors", "least_colors", "widest", "tallest",
        "largest_bbox", "smallest_bbox", "unique_shape", "unique_color",
        "densest", "sparsest", "unique_content",
    ))
    selection_ref = taxonomy.define_node("object_selection", parents=(objects_ref,), operators=(
        *selection,
        OperatorBinding(Operator("object_crop", ("Object",), "Grid"), object_crop),
        OperatorBinding(Operator("crop_bbox", ("Grid", "Object"), "Grid"), crop_bbox),
    ))
    symmetry_ref = taxonomy.define_node("symmetry", parents=(root,), operators=(
        *(OperatorBinding(Operator("complete_" + axis, ("Grid",), "Grid"),
                          partial(complete_reflection, axis=axis))
          for axis in ("vertical", "horizontal", "both", "main_diagonal", "anti_diagonal",
                       "rotation", "full")),
        *(OperatorBinding(Operator("complete_bbox_" + axis, ("Grid",), "Grid"),
                          partial(complete_bbox_reflection, axis=axis))
          for axis in ("vertical", "horizontal", "both", "main_diagonal", "anti_diagonal",
                       "rotation", "full")),
    ))
    topology_ref = taxonomy.define_node("topology", parents=(root,), operators=(
        *(OperatorBinding(Operator(f"fill_holes_{color}", ("Grid",), "Grid"),
                          partial(fill_holes, color=color)) for color in range(1, 10)),
        *(OperatorBinding(Operator(f"remove_noise_{size}", ("Grid",), "Grid"),
                          partial(remove_small_objects, max_size=size)) for size in (1, 2, 3)),
        *(OperatorBinding(Operator(f"{name}_{connectivity}", ("Grid",), "Grid"),
                          partial(function, connectivity=connectivity))
          for name, function in (("dilate", transforms.dilate), ("erode", transforms.erode))
          for connectivity in (4, 8)),
    ))
    dynamics_ref = taxonomy.define_node("dynamics", parents=(root,), operators=tuple(
        OperatorBinding(Operator(f"{name}_{side}", ("Grid",), "Grid"),
                        partial(function, direction=side))
        for name, function in (("gravity", transforms.gravity), ("shift", transforms.shift))
        for side in ("up", "down", "left", "right")
    ))
    composed_ref = taxonomy.define_node(
        "object_geometry", parents=(global_ref, selection_ref),
    )
    logic_ref = taxonomy.define_node("logic", parents=(orientation_ref, parts_ref), operators=(
        *(OperatorBinding(Operator(name, ("Grid", "Grid"), "Grid"), function)
          for name, function in (("and", transforms.logical_and), ("or", transforms.logical_or),
                                 ("xor", transforms.logical_xor))),
        OperatorBinding(Operator("not", ("Grid",), "Grid"), transforms.logical_not),
    ))
    layout_ref = taxonomy.define_node("layout", parents=(orientation_ref, parts_ref), operators=(
        OperatorBinding(Operator("hconcat", ("Grid", "Grid"), "Grid"), transforms.hconcat),
        OperatorBinding(Operator("vconcat", ("Grid", "Grid"), "Grid"), transforms.vconcat),
    ))
    return taxonomy, {
        "geometry": global_ref,
        "object_selection": selection_ref,
        "symmetry": symmetry_ref,
        "topology": topology_ref,
        "dynamics": dynamics_ref,
        "object_geometry": composed_ref,
        "logic": logic_ref,
        "layout": layout_ref,
    }
