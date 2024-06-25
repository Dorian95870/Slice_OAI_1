from models.slice_model import Slice
from utils.api_utils import send_request_to_nsmf

def create_slice(data):
    slice = Slice(**data)
    # Ajoutez la logique métier ici si nécessaire
    response = send_request_to_nsmf(slice)
    return response
