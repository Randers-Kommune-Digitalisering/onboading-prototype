from __future__ import annotations

from typing import Any, Dict


def serialize_ressource(ressource: Any) -> Dict[str, Any]:
    """Serialize a Ressource model to the JSON shape used by the API.

    Includes file metadata when the ressource represents an uploaded file.
    """

    is_file = bool(getattr(ressource, 'isFile', False))

    item: Dict[str, Any] = {
        'RessourceID': getattr(ressource, 'RessourceID', None),
        'name': getattr(ressource, 'name', None),
        'url': getattr(ressource, 'url', None),
        'isFile': is_file,
    }

    file_obj = getattr(ressource, 'file', None) if is_file else None
    if is_file and file_obj is not None:
        item.update({
            'filename': getattr(file_obj, 'filename', None),
            'content_type': getattr(file_obj, 'content_type', None),
            'size_bytes': getattr(file_obj, 'size_bytes', None),
        })

    return item
