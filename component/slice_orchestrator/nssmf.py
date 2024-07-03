import uuid  
import math  
import logging  
from nfvo import NFVO  
from typing import Dict, Any, List  

class CoreNSSMF:
    def __init__(self):
        # Initialisation de la classe
        self.sub_slices = {}  # Dictionnaire pour stocker les sous-slices
        self.nfvo = NFVO()  # Instanciation de l'objet NFVO
        logging.basicConfig(level=logging.DEBUG)  # Configuration de la journalisation

    def create_sub_slice(self, config: Dict[str, Any]) -> str:
        # Méthode pour créer un nouveau sous-slice
        logging.debug(f"Received sub-slice creation request with config: {config}")
        try:
            # Vérification de la configuration
            if not config:
                logging.error("Received empty configuration")
                raise ValueError("Empty configuration")

            if not self.validate_config(config):
                logging.error("Configuration validation failed")
                raise ValueError("Invalid configuration")

            # Génération d'un ID unique pour le sous-slice
            sub_slice_id = str(uuid.uuid4())
            # Calcul des ressources nécessaires
            calculated_resources = self._calculate_resources(config)
            logging.debug(f"Calculated resources: {calculated_resources}")

            # Instantiation des VNFs via le NFVO
            nfvo_response = self.nfvo.instantiate_vnfs(calculated_resources)
            logging.info(f"NFVO deployed network slice with response: {nfvo_response}")
            
            # Stockage des informations du sous-slice
            self.sub_slices[sub_slice_id] = {
                'status': 'active',
                'config': config,
                'calculated_resources': calculated_resources,
                'nfvo_slice_id': nfvo_response['slice_id'],
                'vnf_instances': nfvo_response['vnf_instances']
            }
            logging.info(f"Sub-slice created successfully with ID: {sub_slice_id}")
            return sub_slice_id
        except Exception as e:
            logging.error(f"Error creating sub-slice: {str(e)}")
            raise

    def generate_vcn_config(self, slice_id, service_request):
        # Génération de la configuration VCN (Virtual Core Network)
        vcn_config = {
            "slice_id": slice_id,
            "core_network": {
                "amf": {"instance_count": 1},
                "smf": {"instance_count": 1},
                "upf": {"instance_count": 2},
            },
            "qos_parameters": service_request.get("qos", {})
        }
        return vcn_config
    
    def update_sub_slice(self, sub_slice_id: str, new_config: Dict[str, Any]) -> None:
        # Mise à jour d'un sous-slice existant
        if sub_slice_id not in self.sub_slices:
            raise ValueError(f"Sub-slice {sub_slice_id} not found")
        
        if not self.validate_config(new_config):
            raise ValueError("Invalid configuration")

        # Mise à jour de la configuration et recalcul des ressources
        self.sub_slices[sub_slice_id]['config'].update(new_config)
        calculated_resources = self._calculate_resources(self.sub_slices[sub_slice_id]['config'])
        nfvo_slice_id = self.sub_slices[sub_slice_id]['nfvo_slice_id']
        
        # Mise à jour du slice réseau via le NFVO
        self.nfvo.update_network_slice(nfvo_slice_id, calculated_resources)
        self.sub_slices[sub_slice_id]['calculated_resources'] = calculated_resources

    def terminate_sub_slice(self, sub_slice_id: str) -> None:
        # Terminaison d'un sous-slice
        if sub_slice_id not in self.sub_slices:
            raise ValueError(f"Sub-slice {sub_slice_id} not found")
        
        nfvo_slice_id = self.sub_slices[sub_slice_id]['nfvo_slice_id']
        self.nfvo.delete_network_slice(nfvo_slice_id)
        del self.sub_slices[sub_slice_id]

    def get_sub_slice_details(self, sub_slice_id: str) -> Dict[str, Any]:
        # Récupération des détails d'un sous-slice
        if sub_slice_id not in self.sub_slices:
            raise ValueError(f"Sub-slice {sub_slice_id} not found")
        return self.sub_slices[sub_slice_id]

    def list_sub_slices(self) -> List[str]:
        # Liste de tous les sous-slices
        return list(self.sub_slices.keys())

    def get_sub_slice_status(self, sub_slice_id: str) -> str:
        # Récupération du statut d'un sous-slice
        if sub_slice_id not in self.sub_slices:
            raise ValueError(f"Sub-slice {sub_slice_id} not found")
        return self.sub_slices[sub_slice_id]['status']

    def get_sub_slice_config(self, sub_slice_id: str) -> Dict[str, Any]:
        # Récupération de la configuration d'un sous-slice
        if sub_slice_id not in self.sub_slices:
            raise ValueError(f"Sub-slice {sub_slice_id} not found")
        return self.sub_slices[sub_slice_id]['config']

    def scale_sub_slice(self, sub_slice_id: str, scale_type: str, scale_amount: int) -> None:
        # Mise à l'échelle d'un sous-slice
        if sub_slice_id not in self.sub_slices:
            raise ValueError(f"Sub-slice {sub_slice_id} not found")
        
        current_config = self.sub_slices[sub_slice_id]['config']
        if scale_type == 'up':
            current_config['resources']['cpu'] += scale_amount
            current_config['resources']['memory'] += scale_amount * 1024  # 1GB par unité
        elif scale_type == 'down':
            current_config['resources']['cpu'] = max(1, current_config['resources']['cpu'] - scale_amount)
            current_config['resources']['memory'] = max(1024, current_config['resources']['memory'] - scale_amount * 1024)
        else:
            raise ValueError("Invalid scale type. Use 'up' or 'down'")

        self.update_sub_slice(sub_slice_id, current_config)

    def _calculate_resources(self, config: Dict[str, Any]) -> Dict[str, Any]:
        # Calcul des ressources pour chaque composant du sous-slice
        slice_type = config['slice_type']
        qos = config['qos']
        requested_resources = config['resources']

        calculated_resources = {}
        for component in ['AMF', 'NRF', 'SMF', 'UPF']:
            calculated_resources[component] = self._calculate_component_resources(
                component, slice_type, qos, requested_resources
            )

        return calculated_resources

    def _calculate_component_resources(self, component, slice_type, qos, requested_resources):
        # Calcul des ressources pour un composant spécifique
        # Définition des seuils minimaux pour chaque composant
        min_resources = {
            'AMF': {'cpu': 2, 'memory': 2048, 'storage': 10},
            'NRF': {'cpu': 1, 'memory': 1024, 'storage': 5},
            'SMF': {'cpu': 2, 'memory': 2048, 'storage': 8},
            'UPF': {'cpu': 4, 'memory': 4096, 'storage': 20}
        }

        # Facteurs d'ajustement basés sur le type de slice
        slice_factors = {
            'eMBB': {'cpu': 1.0, 'memory': 1.2, 'storage': 1.0},
            'URLLC': {'cpu': 1.5, 'memory': 1.3, 'storage': 1.1},
            'mMTC': {'cpu': 0.8, 'memory': 0.9, 'storage': 1.2}
        }

        if slice_type not in slice_factors:
            raise ValueError(f"Unknown slice type: {slice_type}")

        factors = slice_factors[slice_type]

        # Calcul des ressources ajustées
        cpu = max(min_resources[component]['cpu'], 
                  math.ceil(requested_resources['cpu']['value'] * factors['cpu']))
        memory = max(min_resources[component]['memory'], 
                     math.ceil(requested_resources['memory']['value'] * factors['memory']))
        storage = max(min_resources[component]['storage'], 
                      math.ceil(requested_resources['storage']['value'] * factors['storage']))

        # Ajustements supplémentaires basés sur QoS
        cpu += math.ceil(qos['throughput']['value'] / 100)
        memory += math.ceil(qos['throughput']['value'] * 5)

        return {'cpu': cpu, 'memory': memory, 'storage': storage}
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        # Validation de la configuration du sous-slice
        logging.debug(f"Validating configuration: {config}")
        required_keys = ['slice_type', 'qos', 'resources']
        for key in required_keys:
            if key not in config:
                logging.error(f"Missing required key: {key}")
                return False
        
        valid_slice_types = ['URLLC', 'eMBB', 'mMTC']
        if config['slice_type'] not in valid_slice_types:
            logging.error(f"Invalid slice_type: {config['slice_type']}")
            return False
        
        if 'cpu' not in config['resources'] or 'memory' not in config['resources']:
            logging.error("Missing 'cpu' or 'memory' in resources")
            return False
        
        if not isinstance(config['resources']['cpu'].get('value'), (int, float)) or config['resources']['cpu']['value'] <= 0:
            logging.error("Invalid CPU value")
            return False
        if not isinstance(config['resources']['memory'].get('value'), (int, float)) or config['resources']['memory']['value'] <= 0:
            logging.error("Invalid memory value")
            return False

        # Vérification que le QoS contient une valeur de débit (throughput)
        if 'throughput' not in config['qos'] or not isinstance(config['qos']['throughput'].get('value'), (int, float)):
            logging.error("Missing or invalid 'throughput' in QoS")
            return False

        logging.debug("Configuration validation passed")
        return True

