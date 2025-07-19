import requests
import warnings
from urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter("ignore", InsecureRequestWarning)


endpoints = {
    "registration": "https://localhost/authentication/registration", 
    "login": "https://localhost/authentication/login",
    "whoami": "https://localhost/authentication/whoami",   
    "products": "https://localhost/products", 
    "buy_products": "https://localhost/products",  
    "orders": "https://localhost/orders",
    "logout": "https://localhost/authentication/logout",
   "admin": "https://localhost/products/admin"
}

microservices={
    "authentication": "https://localhost/authentication/fail",
    "authorization": "https://localhost/authentication/fail",
    "products": "https://localhost/products/fail",
    "orders": "https://localhost/orders/fail",

}


session = requests.Session()

def send_request(url, data=None, method="GET"):
    """
    Funzione per inviare la richiesta HTTP al server con gestione dei cookie.
    :param endpoint_name: nome dell'endpoint (es. "endpoint1")
    :param data: i dati da inviare nel corpo della richiesta (opzionale)
    :return: risposta dal server
    """

    try:
        # Se ci sono dati da inviare, faremo una richiesta POST
        if method=="POST":
            response = session.post(url, json=data, verify=False, allow_redirects=False)
        elif method=="DELETE":
            response=session.delete(url, verify=False, allow_redirects=False)
        else:
            response = session.get(url, verify=False, allow_redirects=False)

        response.raise_for_status()  # Solleva un'eccezione per risposte HTTP non valide

        print("Headers: ", dict(response.headers))

        # Estrai i cookie dalla risposta, se presenti
        cookies = response.cookies.get_dict()

        # Se c'è un JWT, salvalo nella sessione
        jwt_token = cookies.get("jwt")
        if jwt_token:
            session.cookies.set("jwt", jwt_token)  # Salva il JWT nella sessione
            print("New cookie: "+str(jwt_token))

        try:
            response_data = response.json()  # Se è JSON, la funzione restituirà il JSON
            return response_data
        except ValueError:  # Se non è un JSON valido, restituire il contenuto come testo
            return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error in the request: {e}")
        return None

def main():

    while True:
        print("\nSelect an endpoint (type 'exit' to close the program):")
        for endpoint in endpoints:
            print(f" - {endpoint}")

        print(f" - fail")

        endpoint = input("Endpoint: ").strip().lower()
        
        if endpoint == "exit":
            break
        
        if endpoint in endpoints:
            url = endpoints.get(endpoint)
            data=None

            if endpoint=="registration" or endpoint=="login":
                username = input("Username: ")
                password = input("Password: ")
                data={"username": username, "password": password}
                method="POST"
            elif endpoint=="buy_products":
                productID=input("Product ID: ")
                quantity = input("Quantity: ")
                data={"quantity": quantity}
                url+=f"/{productID}/buy"
                method="POST"
            elif endpoint=="logout":
                method="DELETE"
            else:
                method="GET"


            response = send_request(url, data, method)
            
            if response:
                print("Server response:", response)

        elif endpoint=="fail":
            print("\nSelect a microservice to fail (type 'exit' to close the program):")
            for microservice in microservices:
                print(f" - {microservice}")
        
            microservice = input("Microservice: ").strip().lower()
        
            if microservice == "exit":
                break
            if microservice in microservices:
                url = microservices.get(microservice)
                    
                response = send_request(url)
                
                print("Server response:", response)
                
            else:
                print("Invalid microservice!")
        else:
            print("Invalid endpoint!")

if __name__ == "__main__":
    main()
