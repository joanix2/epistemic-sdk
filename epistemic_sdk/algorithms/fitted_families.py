"""Registry of task-fitted learners, grouped by the taxonomy family that owns them.

Learners estimate parameters from training pairs only (see ``fitting``). Each is
also offered after cropping to the foreground bounding box, under the same family
with a ``_cropped`` suffix. Family order is a search prior, not a proven optimum.
"""
from . import grid_transforms as transforms
from .extraction_learners import fit_color_summary, fit_crop, fit_window
from .fitting import Learner, after
from .layout_learners import (
    fit_block_assembly,
    fit_block_reduction,
    fit_cell_expansion,
    fit_fractal,
    fit_partition_combination,
)
from .local_rule import fit_local_rule

_BASE_LEARNERS: dict[str, dict[str, Learner]] = {
    "tiling": {"task_tiling": fit_block_assembly, "task_fractal": fit_fractal,
               "task_expansion": fit_cell_expansion},
    "partition": {"task_partition": fit_partition_combination,
                  "task_reduction": fit_block_reduction},
    "extraction": {"task_crop": fit_crop, "task_summary": fit_color_summary,
                   "task_window": fit_window},
    "local_rule": {"task_local_rule": fit_local_rule},
}

FITTED_FAMILIES: dict[str, dict[str, Learner]] = {
    family: {
        **learners,
        **{name + "_cropped": after(transforms.crop, learner)
           for name, learner in learners.items()},
    } for family, learners in _BASE_LEARNERS.items()
}
