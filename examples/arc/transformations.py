"""ARC adapter: shared grid primitives."""
from epistemic_sdk.algorithms.grid_transforms import (
    anti_transpose as anti_transpose,
)
from epistemic_sdk.algorithms.grid_transforms import (
    crop as crop,
)
from epistemic_sdk.algorithms.grid_transforms import (
    flip_horizontal as flip_horizontal,
)
from epistemic_sdk.algorithms.grid_transforms import (
    flip_vertical as flip_vertical,
)
from epistemic_sdk.algorithms.grid_transforms import (
    pad_square as pad_square,
)
from epistemic_sdk.algorithms.grid_transforms import (
    recolor as recolor,
)
from epistemic_sdk.algorithms.grid_transforms import (
    rotate_90 as rotate_90,
)
from epistemic_sdk.algorithms.grid_transforms import (
    rotate_180 as rotate_180,
)
from epistemic_sdk.algorithms.grid_transforms import (
    rotate_270 as rotate_270,
)
from epistemic_sdk.algorithms.grid_transforms import (
    transpose as transpose,
)
from epistemic_sdk.algorithms.grid_transforms import (
    upscale as upscale,
)

from .loader import Example


def discover_recolor(examples: tuple[Example, ...]) -> dict[int, int]:
    mapping: dict[int, int] = {}
    for example in examples:
        if (
            example.input.height != example.output.height
            or example.input.width != example.output.width
        ):
            raise ValueError("grid dimensions differ; recolor does not apply")
        for row in range(example.input.height):
            for column in range(example.input.width):
                source = example.input[row, column]
                target = example.output[row, column]
                if source == target:
                    continue
                if source in mapping and mapping[source] != target:
                    raise ValueError(f"inconsistent recolor for color {source}")
                mapping[source] = target
    return mapping
