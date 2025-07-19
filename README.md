# Design and Implementation of an API

# Gateway for Microservices on Kubernetes

My project is a **microservices** architecture that uses an API Gateway. It has been developed in
**Kubernetes** , using **Minikube**. Minikube offers a single Kubernetes cluster, composed of a single
node (minikube). On this node I installed and configured the entire architecture of my service,
which, in a real case scenario, should be deployed on a much higher number of nodes.

At the application level there is an **e-commerce service** which is divided into five microservices:

- Authentication microservice;
- Authorization microservice;
- Products microservice;
- Orders microservice;
- Database microservice.

These microservices (except for the Database microservice) are simple web servers configured
using **Python Flask**.

All clients’ requests are received by the **API Gateway** , which forwards the requests to the correct
microservice. It uses the authentication microservice to authenticate the requests that need
authentication and the authorization microservice to authorize the requests that need authorization.
If a request that needs both authentication and authorization will be validated by both the
corresponding microservices, it will be forwarded to the correct microservice. This procedure is
executed transparently to the client. The adopted API Gateway is configured with **Traefik**.

The **Authentication microservice** is publicly available to the users (or clients) and is used for
login, registration and authentication of all the requests. This means that the API Gateway routes all
the requests it receives (at the least the ones that require authentication) to this microservice, in
order to validate (i.e. authenticate) the requests. The other microservices don’t have to implement
authentication (i.e. checking cookies) to know the identity of the users, they can simply read the “ **X-
User-ID** ” header that the authentication microservice has attached to all the authenticated requests.
If the authentication microservice can’t authenticate a request (invalid, expired or absent JWT), an
error (HTTP status code: 40 1 ) is returned to the API gateway and this error is then forwarded to the
client. All requests except the ones for _/authentication/login_ and _/authentication/registration_
endpoints require authentication. The exposed endpoints are:

- **_/authentication/login_** : allows a user to login;
- **_/authentication/logout_** : allows a user to logout (its cookie will be blacklisted);
- **_/authentication/registration_** : allows a user to registrate to the service;
- **_/authentication/whoami_** : allows to a user to get its username;
- **_/validate_** : allows the API gateway to authenticate requests (this endpoint is not publicly
    available).

The **Authorization microservice** is **not** publicly available, but it is used by the API gateway to
authorize some requests. If the authorization microservice does not authorize a request (returns
HTTP status code 40 1 to the gateway), an error is then forwarded to the client. In this application
there is a single endpoint which requires authorization ( _/products/admin_ ). The only interesting


endpoint of this microservice is **_/validate_** , which is used by the API gateway to authorize certain
requests.

The **Products microservice** is publicly available and contains the following endpoints:

- **_/products_** : returns all available products;
- **_/products/admin_** : returns a product that only the _admin_ can see (this endpoint requires
    authorization);
- **_/products/{id}/buy_** : allows to buy a product (whose id is specified in the path).

The **Order microservice** is publicly available and contains the following endpoints:

- **_/orders_** : returns all the orders of a user;
- **_/microservice/orders/add_** : allows to add an order (this endpoint is not publicly reachable
    and is accessed only by the Products Microservice).

The **Database microservice** is **not** publicly available and handles a distributed SQL database. Only
the other microservices use this hidden microservice. This microservice in based on **CockroachDB**
distributed DBMS, which manages the SQL database and automatically guarantees all the non-
functional properties a database should have in a distributed environment (fault tolerance, high
availability, security, scaling, sharding, consistency and so on).

This e-commerce application allows a user to:

- Login ( _/authentication/login_ )
- Registrate ( _/authentication/registration_ )
- Know its username ( _/authentication/whoami_ )
- Get the available products ( _/products_ )
- Buy a product ( _/products/{id}/buy_ )
- Check its orders ( _/orders_ )
- Retrieve a special product if the user is the _admin_ ( _/products/admin_ )

The general architecture can be represented like this:
![General architecture](https://i.postimg.cc/xdhhQyJ1/General-Architecture-Cloud.png)

For more information about this project, check the report I've written for oral presentation.
