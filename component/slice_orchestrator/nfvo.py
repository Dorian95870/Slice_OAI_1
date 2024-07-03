import random
import uuid
from typing import Dict, Any, List
import logging
from threading import Lock

class NFVO:
    def __init__(self):
        # Initialisation des structures de données et configuration du logging
        self.network_slices = {}
        self.vnf_instances = {}
        self.ip_pool = [f"192.168.0.{i}" for i in range(1, 255)]
        self.ip_lock = Lock()  # Pour la gestion de la concurrence
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def instantiate_vnfs(self, calculated_resources: Dict[str, Any]) -> Dict[str, Any]:
        # Instanciation des VNFs pour une nouvelle slice réseau
        slice_id = str(uuid.uuid4())
        vnf_instances = {}

        for component, resources in calculated_resources.items():
            if not self._validate_resources(resources):
                raise ValueError(f"Invalid resources for component {component}")
            
            instance_id = str(uuid.uuid4())
            ip_address = self._allocate_ip()
            
            vnf_instances[component] = {
                'instance_id': instance_id,
                'ip_address': ip_address,
                'status': 'running',
                'resources': resources
            }

        self.network_slices[slice_id] = {
            'status': 'active',
            'vnf_instances': vnf_instances
        }

        self.logger.info(f"Deployed network slice {slice_id}")
        return {
            'slice_id': slice_id,
            'vnf_instances': vnf_instances
        }

    def update_network_slice(self, slice_id: str, new_resources: Dict[str, Any]) -> Dict[str, Any]:
        # Mise à jour des ressources d'une slice réseau existante
        if slice_id not in self.network_slices:
            raise ValueError(f"Network slice {slice_id} not found")

        for component, resources in new_resources.items():
            if not self._validate_resources(resources):
                raise ValueError(f"Invalid resources for component {component}")
            
            if component in self.network_slices[slice_id]['vnf_instances']:
                self.network_slices[slice_id]['vnf_instances'][component]['resources'] = resources
            else:
                # Ajout d'un nouveau composant à la slice existante
                instance_id = str(uuid.uuid4())
                try:
                    ip_address = self._allocate_ip()
                except Exception as e:
                    self.logger.error(f"Failed to allocate IP: {str(e)}")
                    raise
                self.network_slices[slice_id]['vnf_instances'][component] = {
                    'instance_id': instance_id,
                    'ip_address': ip_address,
                    'status': 'running',
                    'resources': resources
                }

        self.logger.info(f"Updated network slice {slice_id}")
        return self.network_slices[slice_id]['vnf_instances']

    def delete_network_slice(self, slice_id: str) -> bool:
        # Suppression d'une slice réseau
        if slice_id not in self.network_slices:
            return False

        for instance in self.network_slices[slice_id]['vnf_instances'].values():
            self._deallocate_ip(instance['ip_address'])

        del self.network_slices[slice_id]
        self.logger.info(f"Deleted network slice {slice_id}")
        return True

    def get_slice_status(self, slice_id: str) -> str:
        # Récupération du statut d'une slice réseau
        if slice_id not in self.network_slices:
            raise ValueError(f"Network slice {slice_id} not found")
        return self.network_slices[slice_id]['status']

    def list_network_slices(self) -> List[str]:
        # Liste des IDs de toutes les slices réseau
        return list(self.network_slices.keys())

    def scale_vnf_instance(self, slice_id: str, component: str, scale_type: str, scale_amount: int) -> None:
        # Mise à l'échelle d'une instance VNF
        if slice_id not in self.network_slices:
            raise ValueError(f"Network slice {slice_id} not found")
        
        if component not in self.network_slices[slice_id]['vnf_instances']:
            raise ValueError(f"Component {component} not found in slice {slice_id}")
        
        vnf_instance = self.network_slices[slice_id]['vnf_instances'][component]
        
        if scale_type == 'up':
            vnf_instance['resources']['cpu'] += scale_amount
            vnf_instance['resources']['memory'] += scale_amount * 1024  # 1GB per unit
        elif scale_type == 'down':
            vnf_instance['resources']['cpu'] = max(1, vnf_instance['resources']['cpu'] - scale_amount)
            vnf_instance['resources']['memory'] = max(1024, vnf_instance['resources']['memory'] - scale_amount * 1024)
        else:
            raise ValueError("Invalid scale type. Use 'up' or 'down'")

        self.logger.info(f"Scaled {scale_type} VNF instance {component} in slice {slice_id}")

    def get_vnf_metrics(self, slice_id: str, component: str) -> Dict[str, Any]:
        # Récupération des métriques d'une instance VNF
        if slice_id not in self.network_slices:
            raise ValueError(f"Network slice {slice_id} not found")
        
        if component not in self.network_slices[slice_id]['vnf_instances']:
            raise ValueError(f"Component {component} not found in slice {slice_id}")
        
        vnf_instance = self.network_slices[slice_id]['vnf_instances'][component]
        
        # Simulation de la collecte de métriques
        return {
            'cpu_usage': random.uniform(0, 100),
            'memory_usage': random.uniform(0, vnf_instance['resources']['memory']),
            'network_in': random.uniform(0, 1000),
            'network_out': random.uniform(0, 1000)
        }

    def _allocate_ip(self) -> str:
        # Allocation d'une adresse IP depuis le pool
        with self.ip_lock:
            if not self.ip_pool:
                raise Exception("IP pool exhausted")
            return self.ip_pool.pop(random.randint(0, len(self.ip_pool) - 1))

    def _deallocate_ip(self, ip: str) -> None:
        # Libération d'une adresse IP
        with self.ip_lock:
            if ip not in self.ip_pool:
                self.ip_pool.append(ip)

    def _validate_resources(self, resources: Dict[str, Any]) -> bool:
        # Validation des ressources demandées
        required_keys = ['cpu', 'memory', 'storage']
        if not all(key in resources for key in required_keys):
            return False
        
        if resources['cpu'] < 1 or resources['memory'] < 1024 or resources['storage'] < 1:
            return False
        
        return True

    def save_state(self, filename: str) -> None:
        # Sauvegarde de l'état du NFVO dans un fichier
        import json
        with open(filename, 'w') as f:
            json.dump({
                'network_slices': self.network_slices,
                'ip_pool': self.ip_pool
            }, f)
        self.logger.info(f"Saved NFVO state to {filename}")

    def load_state(self, filename: str) -> None:
        # Chargement de l'état du NFVO depuis un fichier
        import json
        with open(filename, 'r') as f:
            data = json.load(f)
            self.network_slices = data['network_slices']
            self.ip_pool = data['ip_pool']
        self.logger.info(f"Loaded NFVO state from {filename}")