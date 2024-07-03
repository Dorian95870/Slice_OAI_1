import unittest
from slice_orchestrator2 import SliceOrchestrator
from csmf2 import CSMF
from nsmf import NSMF
from nssmf import CoreNSSMF

class TestSliceManagement(unittest.TestCase):
    def setUp(self):
        self.so = SliceOrchestrator()
        self.csmf = CSMF("config/network_slice_templates/gst_template2.json")
        self.nsmf = NSMF()
        self.nssmf = CoreNSSMF()
        
        self.so.set_components(self.csmf, self.nsmf, self.nssmf)
        self.csmf.set_slice_orchestrator(self.so)

    def test_slice_lifecycle(self):
        # Créer un service
        service_request = {
            "service_type": "eMBB",
            "latency": {"value": 10, "unit": "ms"},
            "throughput": {"value": 100, "unit": "Mbps"},
            "core": {
                "upf_capacity": 1000
            }
        }
        slice_id = self.csmf.process_communication_service_request(service_request)
        self.assertIsNotNone(slice_id)

        # Vérifier le statut
        status = self.csmf.get_communication_service_status(slice_id)
        self.assertEqual(status, "active")

        # Modifier le service
        modification = {
            "latency": {"value": 5, "unit": "ms"},
            "core": {
                "upf_capacity": 1500
            }
        }
        self.csmf.update_communication_service(slice_id, modification)
        
        # Vérifier que la modification a été appliquée
        slice_info = self.nsmf.get_slice_instance(slice_id)
        self.assertEqual(slice_info['request']['latency']['value'], 5)
        self.assertEqual(slice_info['request']['core']['upf_capacity'], 1500)

        # Terminer le service
        self.csmf.terminate_communication_service(slice_id)
        
        # Vérifier que le service n'existe plus
        with self.assertRaises(ValueError):
            self.nsmf.get_slice_instance(slice_id)

if __name__ == '__main__':
    unittest.main()
