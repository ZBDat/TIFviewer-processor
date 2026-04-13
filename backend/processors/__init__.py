from dataclasses import dataclass
from typing import Callable, Literal

import numpy as np
from pydantic import BaseModel

from processors.add_operation import Params as AddOperationParams
from processors.add_operation import apply as add_operation_apply
from processors.divide_operation import Params as DivideOperationParams
from processors.divide_operation import apply as divide_operation_apply
from processors.guided_filter import Params as GuidedFilterParams
from processors.guided_filter import apply as guided_filter_apply
from processors.histogram_eq import Params as HistogramEqParams
from processors.histogram_eq import apply as histogram_equalization_apply
from processors.homomorphic_filter import Params as HomomorphicFilterParams
from processors.homomorphic_filter import apply as homomorphic_filter_apply
from processors.gamma_correction import Params as GammaCorrectionParams
from processors.gamma_correction import apply as gamma_correction_apply
from processors.gaussian_blur import Params as GaussianBlurParams
from processors.gaussian_blur import apply as gaussian_blur_apply
from processors.anisotropic_diffusion import Params as AnisotropicDiffusionParams
from processors.anisotropic_diffusion import apply as anisotropic_diffusion_apply
from processors.local_contrast_norm import Params as LocalContrastNormParams
from processors.local_contrast_norm import apply as local_contrast_normalization_apply
from processors.log_correction import Params as LogCorrectionParams
from processors.log_correction import apply as log_correction_apply
from processors.median_blur import Params as MedianBlurParams
from processors.median_blur import apply as median_blur_apply
from processors.rescale_intensity import Params as RescaleIntensityParams
from processors.rescale_intensity import apply as rescale_intensity_apply
from processors.sigmoid_correction import Params as SigmoidCorrectionParams
from processors.sigmoid_correction import apply as sigmoid_correction_apply
from processors.subtract_operation import Params as SubtractOperationParams
from processors.subtract_operation import apply as subtract_operation_apply
from processors.tophat import Params as TopHatParams
from processors.tophat import apply as tophat_apply
from processors.white_tophat import Params as WhiteTopHatParams
from processors.white_tophat import apply as white_tophat_apply
from processors.wls_filter import Params as WlsFilterParams
from processors.wls_filter import apply as wls_filter_apply


@dataclass(frozen=True)
class ProcessorSpec:
    apply: Callable[..., np.ndarray]
    params_model: type[BaseModel]
    kind: Literal["unary", "binary"] = "unary"


PROCESSOR_SPECS: dict[str, ProcessorSpec] = {
    "histogram_equalization": ProcessorSpec(
        apply=histogram_equalization_apply,
        params_model=HistogramEqParams,
    ),
    "local_contrast_normalization": ProcessorSpec(
        apply=local_contrast_normalization_apply,
        params_model=LocalContrastNormParams,
    ),
    "gamma_correction": ProcessorSpec(
        apply=gamma_correction_apply,
        params_model=GammaCorrectionParams,
    ),
    "log_correction": ProcessorSpec(
        apply=log_correction_apply,
        params_model=LogCorrectionParams,
    ),
    "sigmoid_correction": ProcessorSpec(
        apply=sigmoid_correction_apply,
        params_model=SigmoidCorrectionParams,
    ),
    "tophat": ProcessorSpec(
        apply=tophat_apply,
        params_model=TopHatParams,
    ),
    "white_tophat": ProcessorSpec(
        apply=white_tophat_apply,
        params_model=WhiteTopHatParams,
    ),
    "gaussian_blur": ProcessorSpec(
        apply=gaussian_blur_apply,
        params_model=GaussianBlurParams,
    ),
    "median_blur": ProcessorSpec(
        apply=median_blur_apply,
        params_model=MedianBlurParams,
    ),
    "homomorphic_filter": ProcessorSpec(
        apply=homomorphic_filter_apply,
        params_model=HomomorphicFilterParams,
    ),
    "wls_filter": ProcessorSpec(
        apply=wls_filter_apply,
        params_model=WlsFilterParams,
    ),
    "anisotropic_diffusion": ProcessorSpec(
        apply=anisotropic_diffusion_apply,
        params_model=AnisotropicDiffusionParams,
    ),
    "guided_filter": ProcessorSpec(
        apply=guided_filter_apply,
        params_model=GuidedFilterParams,
    ),
    "rescale_intensity": ProcessorSpec(
        apply=rescale_intensity_apply,
        params_model=RescaleIntensityParams,
    ),
    "add_operation": ProcessorSpec(
        apply=add_operation_apply,
        params_model=AddOperationParams,
        kind="binary",
    ),
    "subtract_operation": ProcessorSpec(
        apply=subtract_operation_apply,
        params_model=SubtractOperationParams,
        kind="binary",
    ),
    "divide_operation": ProcessorSpec(
        apply=divide_operation_apply,
        params_model=DivideOperationParams,
        kind="binary",
    ),
}

# Backward-compatible callable map
PROCESSORS: dict[str, Callable[..., np.ndarray]] = {
    name: spec.apply for name, spec in PROCESSOR_SPECS.items()
}


def get_processor_params_model(name: str) -> type[BaseModel] | None:
    spec = PROCESSOR_SPECS.get(name)
    return spec.params_model if spec else None


def get_processor(name: str) -> Callable[..., np.ndarray] | None:
    spec = PROCESSOR_SPECS.get(name)
    return spec.apply if spec else None


def list_processor_names() -> list[str]:
    return list(PROCESSOR_SPECS.keys())


__all__ = [
    "PROCESSORS",
    "PROCESSOR_SPECS",
    "ProcessorSpec",
    "get_processor",
    "get_processor_params_model",
    "list_processor_names",
]
