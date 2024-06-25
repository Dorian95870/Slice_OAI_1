import json
import os
from typing import Dict, Any

class CSMF:
    def __init__(self, gst_template_path: str):
        self.gst_template_path = gst_template_path
        self.gst_template = self._load_gst_template()
        self.slice_orchestrator = None

    def set_slice_orchestrator(self, so):
        """Configure le Slice Orchestrator."""
        self.slice_orchestrator = so

    def _load_gst_template(self) -> Dict[str, Any]:
        """Charge le template GST depuis un fichier JSON."""
        if not os.path.exists(self.gst_template_path):
            raise FileNotFoundError(f"GST template file not found: {self.gst_template_path}")
        
        with open(self.gst_template_path, 'r') as file:
            return json.load(file)

    def process_communication_service_request(self, service_request: Dict[str, Any]) -> str:
        """Traite une demande de service de communication et la transmet au SO."""
        if self.slice_orchestrator is None:
            raise RuntimeError("Slice Orchestrator not set")

        # Valider et traduire la demande de service en configuration de slice
        slice_config = self._translate_service_to_slice_config(service_request)

        # Transmettre la configuration de slice au SO pour création
        slice_id = self.slice_orchestrator.create_slice(slice_config)
        return slice_id

    def translate_request(self, service_request: Dict[str, Any]) -> Dict[str, Any]:
        """Traduit une demande de service en configuration de slice."""
        return self._translate_service_to_slice_config(service_request)
    
    def translate_modification(self, modification: Dict[str, Any]) -> Dict[str, Any]:
        """Traduit une demande de modification de service en configuration de slice."""
        # Pour l'instant, nous allons simplement retourner la modification telle quelle
        # Dans une implémentation réelle, vous devriez traduire la modification en configuration de slice
        return modification

    def _translate_service_to_slice_config(self, service_request: Dict[str, Any]) -> Dict[str, Any]:
        """Traduit une demande de service en configuration de slice basée sur le GST."""
        slice_config = {}
        for attr, template_value in self.gst_template['gst']['attributes'].items():
            if attr in service_request:
                # Valider que la valeur demandée est conforme au template
                if self._validate_attribute(attr, service_request[attr], template_value):
                    slice_config[attr] = service_request[attr]
                else:
                    raise ValueError(f"Invalid value for attribute {attr}")
            else:
                # Utiliser la valeur par défaut du template si non spécifiée dans la demande
                slice_config[attr] = template_value.get('default', None)
        return slice_config

    def _validate_attribute(self, attr: str, value: Any, template: Dict[str, Any]) -> bool:
        """Valide un attribut par rapport à sa définition dans le template."""
        # Implémentez ici la logique de validation spécifique
        # Par exemple, vérifier les types, les plages de valeurs, etc.
        return True  # Placeholder, à implémenter selon les besoins spécifiques

    def update_communication_service(self, slice_id: str, update_request: Dict[str, Any]) -> None:
        """Met à jour un service de communication existant."""
        if self.slice_orchestrator is None:
            raise RuntimeError("Slice Orchestrator not set")

        # Traduire la demande de mise à jour
        update_config = self._translate_service_to_slice_config(update_request)

        # Demander au SO de modifier la slice
        self.slice_orchestrator.modify_slice(slice_id, update_config)

    def terminate_communication_service(self, slice_id: str) -> None:
        """Termine un service de communication."""
        if self.slice_orchestrator is None:
            raise RuntimeError("Slice Orchestrator not set")

        # Demander au SO de supprimer la slice
        self.slice_orchestrator.delete_slice(slice_id)

    def get_communication_service_status(self, slice_id: str) -> Dict[str, Any]:
        """Récupère le statut d'un service de communication."""
        if self.slice_orchestrator is None:
            raise RuntimeError("Slice Orchestrator not set")

        # Obtenir le statut de la slice auprès du SO
        return self.slice_orchestrator.get_slice_status(slice_id)

# Exemple d'utilisation
if __name__ == "__main__":
    from slice_orchestrator import SliceOrchestrator

    csmf = CSMF("config/network_slice_templates/gst_template2.json")
    so = SliceOrchestrator()
    csmf.set_slice_orchestrator(so)

    # Exemple de demande de service
    service_request = {
        "service_type": "eMBB",
        "latency": {"value": 10, "unit": "ms"},
        "throughput": {"value": 100, "unit": "Mbps"}
    }

    try:
        slice_id = csmf.process_communication_service_request(service_request)
        print(f"Service created with slice ID: {slice_id}")

        # Exemple de mise à jour
        update_request = {
            "latency": {"value": 5, "unit": "ms"}
        }
        csmf.update_communication_service(slice_id, update_request)
        print("Service updated")

        # Obtenir le statut
        status = csmf.get_communication_service_status(slice_id)
        print(f"Service status: {status}")

        # Terminer le service
        csmf.terminate_communication_service(slice_id)
        print("Service terminated")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

