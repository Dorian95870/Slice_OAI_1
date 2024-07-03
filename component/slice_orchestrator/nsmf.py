import uuid
import logging
from typing import Dict, Any

class NSMF:
    def __init__(self):
        # Initialisation des dictionnaires pour stocker les slices et les NSSMF
        self.slices = {}
        self.nssmfs = {}  # Pour le moment, nous n'avons que le Core NSSMF
        logging.debug("NSMF initialized")
    
    def register_nssmf(self, domain: str, nssmf: Any):
        # Enregistrement d'un NSSMF pour un domaine spécifique
        self.nssmfs[domain] = nssmf
        logging.debug(f"NSSMF registered for domain: {domain}")

    def create_slice_instance(self, slice_request: Dict[str, Any]) -> str:
        # Création d'une nouvelle instance de slice
        logging.debug(f"Received slice creation request: {slice_request}")
        
        # Validation de base
        if 'slice_type' not in slice_request:
            logging.error("Missing slice_type in slice request")
            raise ValueError("Missing slice_type in slice request")

        # Génération d'un ID unique pour la nouvelle slice
        slice_id = str(uuid.uuid4())
        self.slices[slice_id] = {
            'status': 'creating',
            'request': slice_request,
            'sub_slices': {}
        }

        try:
            # Pour l'instant, nous ne gérons que le Core
            if 'core' in self.nssmfs:
                logging.debug(f"Sending sub-slice creation request to CoreNSSMF with config: {slice_request}")
                core_sub_slice_id = self.nssmfs['core'].create_sub_slice(slice_request)
                self.slices[slice_id]['sub_slices']['core'] = core_sub_slice_id
            else:
                logging.warning("No Core NSSMF registered")

            self.slices[slice_id]['status'] = 'active'
            logging.info(f"Slice instance created successfully with ID: {slice_id}")
            return slice_id
        except Exception as e:
            logging.error(f"Error creating slice instance: {str(e)}")
            del self.slices[slice_id]
            raise

    def generate_nsi_config(self, slice_id: str, service_request: Dict[str, Any]) -> Dict[str, Any]:
        # Génération de la configuration NSI pour une slice donnée
        if slice_id not in self.slices:
            raise ValueError(f"Slice instance {slice_id} not found")

        slice_instance = self.slices[slice_id]
        nsi_config = {
            "nsi_id": slice_id,
            "slice_type": service_request["slice_type"],
            "slice_differentiator": service_request["slice_differentiator"],
            "qos": service_request["qos"],
            "resources": service_request["resources"],
            "sub_slices": {}
        }

        # Récupération des configurations des sous-slices
        for domain, sub_slice_id in slice_instance['sub_slices'].items():
            if domain in self.nssmfs:
                sub_slice_config = self.nssmfs[domain].get_sub_slice_config(sub_slice_id)
                nsi_config["sub_slices"][domain] = sub_slice_config

        return nsi_config

    def get_slice_instance(self, slice_id: str) -> Dict[str, Any]:
        # Récupération des informations d'une instance de slice
        if slice_id not in self.slices:
            logging.error(f"Slice instance {slice_id} not found")
            raise ValueError(f"Slice instance {slice_id} not found")
        return self.slices[slice_id]

    def update_slice_instance(self, slice_id: str, update_request: Dict[str, Any]) -> None:
        # Mise à jour d'une instance de slice existante
        if slice_id not in self.slices:
            logging.error(f"Slice instance {slice_id} not found for update")
            raise ValueError(f"Slice instance {slice_id} not found")
        
        logging.debug(f"Updating slice instance {slice_id} with request: {update_request}")
        
        # Mise à jour des sous-slices
        if 'core' in update_request and 'core' in self.nssmfs:
            core_sub_slice_id = self.slices[slice_id]['sub_slices'].get('core')
            if core_sub_slice_id:
                self.nssmfs['core'].update_sub_slice(core_sub_slice_id, update_request['core'])

        # Mise à jour de la requête principale
        self.slices[slice_id]['request'].update(update_request)
        logging.info(f"Slice instance {slice_id} updated successfully")

    def terminate_slice_instance(self, slice_id: str) -> None:
        # Terminaison d'une instance de slice
        if slice_id not in self.slices:
            logging.error(f"Slice instance {slice_id} not found for termination")
            raise ValueError(f"Slice instance {slice_id} not found")
        
        logging.debug(f"Terminating slice instance {slice_id}")
        
        # Terminer les sous-slices
        for domain, sub_slice_id in self.slices[slice_id]['sub_slices'].items():
            if domain in self.nssmfs:
                self.nssmfs[domain].terminate_sub_slice(sub_slice_id)

        # Supprimer l'instance de slice
        del self.slices[slice_id]
        logging.info(f"Slice instance {slice_id} terminated successfully")

    def list_slice_instances(self) -> list[str]:
        # Liste des IDs de toutes les instances de slice
        return list(self.slices.keys())

    def get_slice_details(self, slice_id: str) -> Dict[str, Any]:
        # Récupération des détails d'une instance de slice spécifique
        if slice_id not in self.slices:
            logging.error(f"Slice instance {slice_id} not found")
            raise ValueError(f"Slice instance {slice_id} not found")
        return self.slices[slice_id]