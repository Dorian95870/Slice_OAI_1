import uuid
from typing import Dict, List, Any
from enum import Enum

class SliceStatus(Enum):
    CREATING = 1
    ACTIVE = 2
    MODIFYING = 3
    DELETING = 4
    ERROR = 5

class SliceOrchestrator:
    def __init__(self):
        self.slices: Dict[str, Dict[str, Any]] = {}
        self.csmf = None
        self.nsmf = None
        self.nssmf = None

    def set_components(self, csmf, nsmf, nssmf):
        """Configure les composants nécessaires pour l'orchestration."""
        self.csmf = csmf
        self.nsmf = nsmf
        self.nssmf = nssmf

    def create_slice(self, slice_request: Dict[str, Any]) -> str:
        """Orchestre la création d'une nouvelle slice."""
        if not all([self.csmf, self.nsmf, self.nssmf]):
            raise RuntimeError("All components (CSMF, NSMF, NSSMF) must be set before creating a slice")

        slice_id = str(uuid.uuid4())
        self.slices[slice_id] = {
            "status": SliceStatus.CREATING,
            "request": slice_request,
            "config": {}
        }

        try:
            # Utiliser translate_request au lieu de translate_request
            translated_request = self.csmf.translate_request(slice_request)

            # Le reste du code reste inchangé
            network_slice = self.nsmf.create_network_slice(translated_request)
            subnet_slices = self.nssmf.create_subnet_slices(network_slice)

            # Mise à jour de la configuration de la slice
            self.slices[slice_id]["config"] = {
                "network_slice": network_slice,
                "subnet_slices": subnet_slices
            }
            self.slices[slice_id]["status"] = SliceStatus.ACTIVE

            return slice_id
        except Exception as e:
            self.slices[slice_id]["status"] = SliceStatus.ERROR
            self.slices[slice_id]["error"] = str(e)
            raise

    def modify_slice(self, slice_id: str, modification: Dict[str, Any]) -> None:
        """Orchestre la modification d'une slice existante."""
        if slice_id not in self.slices:
            raise ValueError(f"Slice {slice_id} not found")

        self.slices[slice_id]["status"] = SliceStatus.MODIFYING

        try:
            # Coordonner avec CSMF pour traduire la modification
            translated_mod = self.csmf.translate_modification(modification)

            # Coordonner avec NSMF pour modifier le réseau
            self.nsmf.modify_network_slice(slice_id, translated_mod)

            # Coordonner avec NSSMF pour modifier les sous-slices
            self.nssmf.modify_subnet_slices(slice_id, translated_mod)

            # Mise à jour de la configuration de la slice
            self.slices[slice_id]["config"].update(translated_mod)
            self.slices[slice_id]["status"] = SliceStatus.ACTIVE
        except Exception as e:
            self.slices[slice_id]["status"] = SliceStatus.ERROR
            self.slices[slice_id]["error"] = str(e)
            raise

    def delete_slice(self, slice_id: str) -> None:
        """Orchestre la suppression d'une slice."""
        if slice_id not in self.slices:
            raise ValueError(f"Slice {slice_id} not found")

        self.slices[slice_id]["status"] = SliceStatus.DELETING

        try:
            # Coordonner avec NSSMF pour supprimer les sous-slices
            self.nssmf.delete_subnet_slices(slice_id)

            # Coordonner avec NSMF pour supprimer le réseau
            self.nsmf.delete_network_slice(slice_id)

            # Supprimer la slice de la liste
            del self.slices[slice_id]
        except Exception as e:
            self.slices[slice_id]["status"] = SliceStatus.ERROR
            self.slices[slice_id]["error"] = str(e)
            raise

    def get_slice_status(self, slice_id: str) -> SliceStatus:
        """Récupère le statut d'une slice."""
        if slice_id not in self.slices:
            raise ValueError(f"Slice {slice_id} not found")
        return self.slices[slice_id]["status"]

    def list_slices(self) -> List[str]:
        """Liste tous les IDs des slices gérées."""
        return list(self.slices.keys())

    def monitor_slices(self) -> Dict[str, SliceStatus]:
        """Surveille l'état de toutes les slices."""
        return {slice_id: self.get_slice_status(slice_id) for slice_id in self.slices}

# Exemple d'utilisation
if __name__ == "__main__":
    so = SliceOrchestrator()
    
    # Ici, vous devriez initialiser et configurer CSMF, NSMF, NSSMF
    # so.set_components(csmf, nsmf, nssmf)
    
    # Exemple de création de slice
    slice_request = {
        "name": "Example Slice",
        "type": "eMBB",
        "performance_req": {
            "latency": 10,
            "throughput": 100
        }
    }
    
    try:
        slice_id = so.create_slice(slice_request)
        print(f"Slice created with ID: {slice_id}")
        
        # Exemple de modification de slice
        so.modify_slice(slice_id, {"performance_req": {"latency": 5}})
        
        # Exemple de surveillance
        print(f"Slice status: {so.get_slice_status(slice_id)}")
        
        # Exemple de suppression de slice
        so.delete_slice(slice_id)
        print("Slice deleted")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
