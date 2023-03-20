# eShopOnTesting - Automation Bootcamp Final Project

Pytesting in Python the infamous eShopOnContainers - Ordering microservice ~

## Introduction
Each student should write a set of automation test cases in Python.
The test cases will be based on collection of micro services that will function as a “Unit Under Test” – “EshopOnline” website.
Every student will be assigned one or more micro services to implement automation tests for.

## Unit under test description
The UUT for the project is called “EshopOnline”. It’s an online shop website which includes client applications, backend micro services, API Gateways, DBs and an Event bus to communicate between the micro services.
The whole system is launched as a docker containers on your local machine.
Each micro service is running independently as listed in the diagram below:

<img src="https://github.com/dotnet-architecture/eShopOnContainers/raw/dev/img/eShopOnContainers-architecture.png" alt="Eshop containers architecture">

## List of services:
* Basket API – Handles shopping basket
* Catalog API – Handles the store catalog
* Identity API – Handles shop customers
* Payment API – Handles customer payments
* Ordering API – Handles orders after purchases
* Event bus – Handles communications between services
* Web status – Shows the status of each service
* Web/mobile clients – Used for system review / manual testing
