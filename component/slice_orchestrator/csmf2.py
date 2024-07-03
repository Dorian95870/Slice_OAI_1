import json
import os
import logging
from typing import Dict, Any

class CSMF:
    # Définition des types de tranches valides
    valid_slice_types = ["eMBB", "URLLC", "mMTC"]

    def __init__(self, template_path):
        # Initialisation du CSMF avec le chemin du template
        self.template_path = template_path
        self.slice_orchestrator = None
        logging.debug(f"CSMF initialized with template path: {template_path}")

    def set_slice_orchestrator(self, so):
        # Configuration de l'orchestrateur de tranches
        self.slice_orchestrator = so
        logging.debug("Slice orchestrator set in CSMF")

    def process_communication_service_request(self, service_request):
        # Traitement d'une demande de service de communication
        logging.debug(f"CSMF received service request: {json.dumps(service_request, indent=2)}")
        
        # Vérification de la présence du type de tranche dans la demande
        if "slice_type" not in service_request:
            logging.error("Slice type is missing in the service request")
            raise ValueError("Slice type must be specified")
        
        # Vérification de la validité du type de tranche
        if service_request["slice_type"] not in self.valid_slice_types:
            logging.error(f"Invalid slice type: {service_request['slice_type']}")
            raise ValueError(f"Invalid slice type. Must be one of {', '.join(self.valid_slice_types)}")
        
        # Traduction de la demande
        translated_request = self._translate_request(service_request)
        logging.debug(f"Translated request: {json.dumps(translated_request, indent=2)}")
        
        # Vérification de la présence de l'orchestrateur de tranches
        if self.slice_orchestrator is None:
            logging.error("Slice orchestrator is not set")
            raise RuntimeError("Slice orchestrator is not set")
        
        # Création de la tranche
        slice_id = self.slice_orchestrator.create_slice(translated_request)
        logging.info(f"Slice created with ID: {slice_id}")
        return slice_id

    def update_communication_service(self, slice_id, modification):
        # Mise à jour d'un service de communication existant
        logging.debug(f"Updating communication service for slice ID {slice_id}")
        logging.debug(f"Modification request: {json.dumps(modification, indent=2)}")
        
        # Traduction de la demande de modification
        translated_mod = self._translate_modification(modification)
        logging.debug(f"Translated modification: {json.dumps(translated_mod, indent=2)}")
        
        # Application de la modification
        self.slice_orchestrator.modify_slice(slice_id, translated_mod)
        logging.info(f"Slice {slice_id} updated successfully")

    def terminate_communication_service(self, slice_id):
        # Terminaison d'un service de communication
        logging.debug(f"Terminating communication service for slice ID {slice_id}")
        self.slice_orchestrator.delete_slice(slice_id)
        logging.info(f"Slice {slice_id} terminated successfully")

    def get_communication_service_status(self, slice_id):
        # Récupération du statut d'un service de communication
        logging.debug(f"Getting status for slice ID {slice_id}")
        status = self.slice_orchestrator.get_slice_status(slice_id)
        logging.debug(f"Status for slice {slice_id}: {json.dumps(status, indent=2)}")
        return status

    def _translate_request(self, service_request):
        # Méthode interne pour traduire une demande de service
        logging.debug("Translating service request")
        return service_request

    def _translate_modification(self, modification):
        # Méthode interne pour traduire une demande de modification
        logging.debug("Translating modification request")
        return modification