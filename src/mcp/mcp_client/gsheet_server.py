from jsonrpcserver import method, serve
from src.tools.get_data_ggSheet import get_information_from_url

@method
def get_sheet_data(url: str) -> dict:
    data = get_information_from_url(url)
    return {"data": data}

if __name__ == "__main__":
    serve()
