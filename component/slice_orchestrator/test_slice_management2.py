
import uuid
from slice_orchestrator import SliceOrchestrator
from csmf import CSMF
from nsmf import NSMF
from nssmf import CoreNSSMF

def main():
    # Initialisation des composants
    so = SliceOrchestrator()
    csmf = CSMF("config/network_slice_templates/gst_template2.json")
    nsmf = NSMF()
    nssmf = CoreNSSMF()
    
    print("All components initialized")

    # Configuration des composants
    so.set_components(csmf, nsmf, nssmf)
    csmf.set_slice_orchestrator(so)
    
    print("Components configured")

    # Exemple de demande de service
    service_request = {
        "service_type": "eMBB",
        "latency": {"value": 10, "unit": "ms"},
        "throughput": {"value": 100, "unit": "Mbps"}
    }

    try:
        # Créer un service (slice)
        slice_id = csmf.process_communication_service_request(service_request)
        print(f"Service created with slice ID: {slice_id}")

        # Obtenir le statut du service
        status = so.get_slice_status(slice_id)
        print(f"Service status: {status}")

        # Modifier le service
        modification = {"latency": {"value": 5, "unit": "ms"}}
        csmf.update_communication_service(slice_id, modification)
        
        # Mettre à jour le statut du slice
        so.update_slice_status(slice_id, "MODIFIED")
        
        # Obtenir le nouveau statut
        new_status = so.get_slice_status(slice_id)
        print(f"Service modified. New status: {new_status}")

        # Terminer le service
        csmf.terminate_communication_service(slice_id)
        print("Service terminated")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()

