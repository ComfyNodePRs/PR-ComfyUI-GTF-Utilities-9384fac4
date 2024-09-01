import torch
from ..gtf_impl import utils as U
from ..gtf_impl import filters as FT


# BASE CLASSES

class FilterBase:
    @staticmethod
    def INPUT_TYPES():
        return {"required": {'gtf': ('GTF', {})}}

    RETURN_TYPES = ('GTF', )
    RETURN_NAMES = ('gtf', )
    CATEGORY = 'gtf/filter'
    FUNCTION = "f"


class FilterRadiusBase(FilterBase):
    @staticmethod
    def INPUT_TYPES():
        return {"required": {
            "gtf": ("GTF", {}),
            "radius": ("INT", {"min": 0, "default": 1}),
        }}


# NODES

class Invert(FilterBase):
    @staticmethod
    def f(gtf: torch.Tensor) -> tuple[torch.Tensor]:
        inverted = U.invert(gtf)
        return (inverted, )


class SumNormalize(FilterBase):
    @staticmethod
    def f(gtf: torch.Tensor) -> tuple[torch.Tensor]:
        normalized = U.sum_normalize(gtf, (2, 3))
        return (normalized, )


class RangeNormalize(FilterBase):
    @staticmethod
    def f(gtf: torch.Tensor) -> tuple[torch.Tensor]:
        normalized = U.range_normalize(gtf, (2, 3))
        return (normalized, )


class PatchRangeNormalize(FilterRadiusBase):
    @staticmethod
    def f(gtf: torch.Tensor, radius: int) -> tuple[torch.Tensor]:
        normalized = FT.patch_range_normalize(gtf, radius)
        return (normalized, )


class BinaryThreshold(FilterBase):
    @staticmethod
    def INPUT_TYPES():
        return {"required": {
            'gtf': ('GTF', {}),
            "gtf_threshold": ("GTF", {}),
        }}

    @staticmethod
    def f(gtf: torch.Tensor, gtf_threshold: torch.Tensor) -> tuple[torch.Tensor]:
        thresholded = (gtf >= gtf_threshold).to(torch.float)
        return (thresholded, )


class OtsusMethod(FilterBase):
    @staticmethod
    def INPUT_TYPES():
        return {"required": {
            'gtf': ('GTF', {}),
            'bins': ("INT", {"min": 1, "default": 256}),
        }}

    @staticmethod
    def f(gtf: torch.Tensor, bins: int) -> tuple[torch.Tensor]:
        thresholds = FT.otsus_method(gtf, bins)
        return (thresholds, )


class HysteresisThreshold(FilterBase):
    @staticmethod
    def INPUT_TYPES():
        return {"required": {
            'gtf_weak': ('GTF', {}),
            'gtf_strong': ('GTF', {}),
        }}

    @staticmethod
    def f(gtf_weak: torch.Tensor, gtf_strong: torch.Tensor) -> tuple[torch.Tensor]:
        thresholded = FT.hysteresis_threshold(gtf_weak, gtf_strong)
        return (thresholded, )


class Quantize(FilterBase):
    @staticmethod
    def INPUT_TYPES():
        return {"required": {
            'gtf': ('GTF', ),
            "steps": ("INT", {"default": 256, "min": 2, "max": 1_000_000}),
            "mode": ([*FT.F_MAP.keys()], ),
        }}

    @staticmethod
    def f(gtf: torch.Tensor, steps: int, mode: str) -> tuple[torch.Tensor]:
        quantized = FT.quantize(gtf, steps, mode)
        return (quantized, )


class Convolve(FilterBase):
    @staticmethod
    def INPUT_TYPES():
        return {"required": {
            "gtf": ("GTF", {}),
            "gtf_kernel": ("GTF", {}),
        }}

    @staticmethod
    def f(gtf: torch.Tensor, gtf_kernel: torch.Tensor) -> tuple[torch.Tensor]:
        convolved = FT.convolve_2d(gtf, gtf_kernel)
        return (convolved, )


class GradientNMSMask(FilterBase):
    @staticmethod
    def INPUT_TYPES():
        return {"required": {
            "gtf_r": ("GTF", {}),
            "gtf_theta": ("GTF", {}),
        }}

    @staticmethod
    def f(gtf_r: torch.Tensor, gtf_theta: torch.Tensor) -> tuple[torch.Tensor]:
        mask = FT.gradient_suppression_mask(gtf_r, gtf_theta)
        return (mask, )


class MorphologicalFilter(FilterBase):
    @staticmethod
    def INPUT_TYPES():
        return {"required": {
            "gtf": ("GTF", {}),
            "operation": (["dilate", "erode", "open", "close"], {}),
            "radius": ("INT", {"default": 3, "min": 1})
        }}

    @staticmethod
    def f(gtf: torch.Tensor, operation: str, radius: int) -> tuple[torch.Tensor]:
        if radius == 0:
            return (gtf, )
        match operation:
            case "dilate":
                filtered = FT.dilate(gtf, radius)
            case "erode":
                filtered = FT.erode(gtf, radius)
            case "open":
                filtered = FT.open(gtf, radius)
            case "close":
                filtered = FT.close(gtf, radius)
        return (filtered, )


class MinFilter(FilterRadiusBase):
    @staticmethod
    def f(gtf: torch.Tensor, radius: int) -> tuple[torch.Tensor]:
        filtered = FT.patch_min(gtf, radius)
        return (filtered, )


class MaxFilter(FilterRadiusBase):
    @staticmethod
    def f(gtf: torch.Tensor, radius: int) -> tuple[torch.Tensor]:
        filtered = FT.patch_max(gtf, radius)
        return (filtered, )


class MedianFilter(FilterRadiusBase):
    @staticmethod
    def f(gtf: torch.Tensor, radius: int) -> tuple[torch.Tensor]:
        filtered = FT.patch_median(gtf, radius)
        return (filtered, )


NODE_CLASS_MAPPINGS = {
    "GTF | Filter - Convolve":         Convolve,
    "GTF | Filter - Gradient NMS Mask": GradientNMSMask,
    "GTF | Filter - Hysteresis Threshold": HysteresisThreshold,
    "GTF | Filter - Sum Normalize":    SumNormalize,
    "GTF | Filter - Range Normalize":  RangeNormalize,
    "GTF | Filter - Invert":           Invert,
    "GTF | Filter - Binary Threshold": BinaryThreshold,
    "GTF | Filter - Quantize":         Quantize,
    "GTF | Filter - Morphological":    MorphologicalFilter,
    "GTF | Helper - Otsu's Method":    OtsusMethod,
    "GTF | Filter - Patch Range Normalize": PatchRangeNormalize,
    "GTF | Filter - Patch Min": MinFilter,
    "GTF | Filter - Patch Max": MaxFilter,
    "GTF | Filter - Patch Median": MedianFilter,
}

__all__ = ["NODE_CLASS_MAPPINGS"]
