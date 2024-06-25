import uuid
from typing import Dict, Any, List

class NSSMF:
    def __init__(self):
        # Initialisation si nécessaire
        pass

    def create_subnet_slices(self, network_slice: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Implémentation simple pour le test
        return [{"subnet_slice_id": str(uuid.uuid4())}]

    def modify_subnet_slices(self, slice_id: str, translated_mod: Dict[str, Any]) -> None:
        # Logique de modification de sous-slices
        pass

    def delete_subnet_slices(self, slice_id: str) -> None:
        # Logique de suppression de sous-slices
        pass