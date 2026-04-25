from fastapi import APIRouter

router = APIRouter()


# When i get a GET request for /health. send back status : ok
@router.get("/health")
def health_check():
    return {"status": "ok"}
