import uuid
from typing import Dict, List, Any
from enum import Enum
import logging

class ResourceValidator:
    def __init__(self, available_resources):
        # Initialise le validateur avec les ressources disponibles
        self.available_resources = available_resources

    def validate(self, requested_resources):
        # Valide les ressources demandées par rapport aux ressources disponibles
        errors = []
        for resource, details in requested_resources.items():
            if resource in self.available_resources:
                if details['value'] > self.available_resources[resource]:
                    # Ajoute une erreur si la demande dépasse la disponibilité
                    errors.append(f"Requested {resource} ({details['value']} {details['unit']}) exceeds available {resource} ({self.available_resources[resource]} {details['unit']})")
            else:
                # Ajoute une erreur si le type de ressource est inconnu
                errors.append(f"Unknown resource type: {resource}")
        return errors

class SliceOrchestrator:
    def __init__(self):
        # Initialise l'orchestrateur de tranches
        self.nsmf = None
        self.csmf = None
        # Crée un validateur de ressources avec des valeurs d'exemple
        self.resource_validator = ResourceValidator({
            'cpu': 100,  # exemple: 100 vCPUs disponibles
            'memory': 256000,  # exemple: 256 GB disponibles
            'storage': 10000,  # exemple: 10 TB disponibles
            'bandwidth': 10000  # exemple: 10 Gbps disponibles
        })

    def set_components(self, csmf, nsmf, nssmf):
        # Configure les composants CSMF, NSMF et NSSMF
        self.csmf = csmf
        self.nsmf = nsmf
        self.nsmf.register_nssmf('core', nssmf)

    def create_slice(self, translated_request: Dict[str, Any]) -> str:
        # Crée une nouvelle tranche réseau
        # Valide d'abord les ressources demandées
        validation_errors = self.resource_validator.validate(translated_request['resources'])
        if validation_errors:
            raise ValueError(f"Resource validation failed: {', '.join(validation_errors)}")

        # Si la validation passe, procède à la création de la tranche
        nsi_config = self.generate_nsi_config(translated_request)
        return self.nsmf.create_slice_instance(nsi_config)

    def generate_nsi_config(self, translated_request: Dict[str, Any]) -> Dict[str, Any]:
        # Génère la configuration pour une nouvelle instance de tranche réseau
        slice_id = str(uuid.uuid4())
        nsi_config = {
            "slice_id": slice_id,
            "slice_type": translated_request["slice_type"],
            "slice_differentiator": translated_request["slice_differentiator"],
            "qos": translated_request["qos"],
            "resources": translated_request["resources"],
            "sub_slices": {}
        }

        # Génère la configuration des sous-tranches pour chaque domaine
        for domain, nssmf in self.nsmf.nssmfs.items():
            logging.debug(f"Creating sub-slice for domain: {domain}")
            sub_slice_id = nssmf.create_sub_slice(translated_request)
            logging.debug(f"Created sub-slice with ID: {sub_slice_id}")
            if sub_slice_id is None:
                logging.error(f"Failed to create sub-slice for domain: {domain}")
                continue
            sub_slice_config = nssmf.get_sub_slice_config(sub_slice_id)
            logging.debug(f"Retrieved sub-slice config: {sub_slice_config}")
            if sub_slice_config is None:
                logging.error(f"Failed to retrieve config for sub-slice: {sub_slice_id}")
                continue
            nsi_config["sub_slices"][domain] = sub_slice_config

        return nsi_config

    def delete_slice(self, slice_id: str) -> bool:
        # Supprime une instance de tranche réseau
        return self.nsmf.delete_slice_instance(slice_id)

    def modify_slice(self, slice_id: str, modifications: Dict[str, Any]) -> bool:
        # Modifie une instance de tranche réseau existante
        # Valide d'abord les modifications de ressources
        if 'resources' in modifications:
            validation_errors = self.resource_validator.validate(modifications['resources'])
            if validation_errors:
                raise ValueError(f"Resource modification validation failed: {', '.join(validation_errors)}")

        return self.nsmf.modify_slice_instance(slice_id, modifications)

    def get_slice_info(self, slice_id: str) -> Dict[str, Any]:
        # Récupère les informations sur une instance de tranche réseau
        return self.nsmf.get_slice_instance_info(slice_id)

    def list_slices(self) -> List[str]:
        # Liste toutes les instances de tranches réseau
        return self.nsmf.list_slice_instances()

    def monitor_slice(self, slice_id: str) -> Dict[str, Any]:
        # Surveille une instance de tranche réseau
        return self.nsmf.monitor_slice_instance(slice_id)

    def scale_slice(self, slice_id: str, scaling_info: Dict[str, Any]) -> bool:
        # Redimensionne une instance de tranche réseau
        # Valide d'abord les modifications de ressources pour le scaling
        if 'resources' in scaling_info:
            validation_errors = self.resource_validator.validate(scaling_info['resources'])
            if validation_errors:
                raise ValueError(f"Scaling resource validation failed: {', '.join(validation_errors)}")

        return self.nsmf.scale_slice_instance(slice_id, scaling_info)