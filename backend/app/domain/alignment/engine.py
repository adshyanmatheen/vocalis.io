import logging

from torchao.quantization import (
    Int8DynamicActivationInt8WeightConfig,
    quantize_,
)
from transformers import AutoModelForCTC, AutoProcessor

from app.core.config import settings
from app.domain.alignment.exceptions import (
    ModelInitializationError,
    QuantizationError,
)
from app.domain.alignment.models import AlignmentModelBundle
from app.domain.alignment.registry import (
    _alignment_model_registry,
)

logger = logging.getLogger(__name__)


def load_alignment_model_bundle(
    *, local_files_only: bool = False
) -> AlignmentModelBundle:

    global _alignment_model_registry

    if _alignment_model_registry is not None:
        return _alignment_model_registry

    try:
        processor = AutoProcessor.from_pretrained(
            settings.app.huggingface_model_id,
            cache_dir=settings.app.huggingface_cache_dir,
            local_files_only=local_files_only,
        )

        model = AutoModelForCTC.from_pretrained(
            settings.app.huggingface_model_id,
            cache_dir=settings.app.huggingface_cache_dir,
            local_files_only=local_files_only,
        )

    except Exception as error:
        logger.exception("Failed to initialize alignment models")
        raise ModelInitializationError(
            "The Alignment Models Could Not Be Initialized Safely."
        ) from error

    inference_device = settings.app.device

    quantization_backend = None

    quantization_precision = None

    if (
        settings.app.alignment_quantization_backend == "torchao"
        and inference_device == "cpu"
    ):
        try:
            quantize_(
                model,
                Int8DynamicActivationInt8WeightConfig(),
            )

            quantization_backend = "torchao"

            quantization_precision = "int8"

        except Exception as error:
            logger.exception(
                "Torchao quantization failed during alignment initialization"
            )
            raise QuantizationError(
                "Torchao Quantization Failed During Alignment Initialization."
            ) from error

    model.to(inference_device)

    model.eval()

    tokenizer = processor.tokenizer

    blank_token_id = tokenizer.pad_token_id

    if blank_token_id is None:
        raise ModelInitializationError(
            "The Alignment Tokenizer Does Not Define A Valid CTC Blank Token."
        )

    _alignment_model_registry = AlignmentModelBundle(
        processor=processor,
        model=model,
        blank_token_id=blank_token_id,
        vocabulary=tokenizer.get_vocab(),
        inference_device=inference_device,
        quantization_backend=quantization_backend,
        quantization_precision=quantization_precision,
    )

    return _alignment_model_registry
