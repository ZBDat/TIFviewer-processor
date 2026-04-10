from processors.histogram_eq import apply as _hist_eq
from processors.local_contrast_norm import apply as _lcn

PROCESSORS = {
    "histogram_equalization": _hist_eq,
    "local_contrast_normalization": _lcn,
}

__all__ = ["PROCESSORS"]
