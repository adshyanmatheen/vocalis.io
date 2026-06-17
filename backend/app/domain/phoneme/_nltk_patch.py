from __future__ import annotations

import logging
from urllib.request import url2pathname

logger = logging.getLogger(__name__)


def install() -> None:
    import nltk.data
    import nltk.pathsec

    _original_reject = nltk.data._reject_unsafe_no_protocol

    def _patched_reject(resource_url: str) -> None:
        _original_reject(resource_url)
        decoded = url2pathname(resource_url)
        if decoded != resource_url:
            _original_reject(decoded)

    nltk.data._reject_unsafe_no_protocol = _patched_reject

    _original_find = nltk.data.find

    def _patched_find(
        resource_name: str, paths: list[str] | None = None
    ) -> nltk.data.PathPointer:
        decoded = url2pathname(resource_name)
        if decoded != resource_name and nltk.data._UNSAFE_NO_PROTOCOL_RE.search(decoded):
            raise ValueError(
                f"Unsafe resource path (detected after URL decoding): {resource_name!r}"
            )
        return _original_find(resource_name, paths)

    nltk.data.find = _patched_find

    nltk.pathsec.ENFORCE = True

    logger.info(
        "NLTK security patches applied: URL-decode-before-check fix + ENFORCE=True"
    )

