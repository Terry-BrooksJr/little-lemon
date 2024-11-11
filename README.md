# Little Lemon API

Welcome to the Little Lemon API, a RESTful API designed for managing a restaurant's operations.

This project is developed as a final assignment for Meta's APIs course on Coursera by Terry Brooks. You can find the course on [Coursera](https://www.coursera.org/learn/apis/home/info) and the project source code on [GitHub](https://github.com/Terry-BrooksJr/little-lemon).

> **Note:** This project is open-source for learning purposes, but please respect Coursera’s academic honesty policy. Refer to the [Coursera Honor Code](https://www.coursera.support/s/article/209818863-Coursera-Honor-Code?) for guidance.

## Table of Contents

- [Little Lemon API](#little-lemon-api)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
    - [Features](#features)
  - [Getting Started](#getting-started)
    - [Testing/Touring the Mock API](#testingtouring-the-mock-api)
      - [_Which ever Method Selected, The Getting Started Steps are the Same_:](#which-ever-method-selected-the-getting-started-steps-are-the-same)
  - [API Documentation](#api-documentation)
  - [Authentication](#authentication)
      - [Example Header](#example-header)
  - [Rate and Usage Limits](#rate-and-usage-limits)
  - [Happy Coding!](#happy-coding)

## Overview

The Little Lemon API offers a collection of endpoints to manage user accounts, menu items, carts, and orders within a restaurant management context. It supports user registration, token-based authentication, and various managerial functions.

### Features

- **User Management:** Register users, authenticate, and manage user roles.
- **Inventory Management:** CRUD operations on menu items.
- **Cart Management:** Manage items within a user's cart.
- **Order Management:** Handle order lifecycle from creation to deletion.

## Getting Started

### Testing/Touring the Mock API

To explore the API without setting up a local environment, you can use the tour the API via:

- #### [Postman](https://www.postman.com/blackberry-py-dev/workspace/little-lemon-meta-apis-final-terry-brooks-jr)
- Fully documented [Postman](https://www.postman.com/) Workspace, that has helpful request automnation scripting.
- #### [DRF Browseable API UI](https://api.little-lemon.xyz)
- The native browser based API interface provided by [Django Rest Framework](https://www.django-rest-framework.org/).
- #### [Swagger UI](https://api.little-lemon.xyz/api/swagger)
- Browser Based API interface using the [Swagger UI](https://swagger.io/)
- #### BYOC Bring Your Own Client
- Any HTTP Client your heart desires using the `https://api.little-lemon.xyz` and the documentation found via [Postman](https://www.postman.com/blackberry-py-dev/workspace/little-lemon-meta-apis-final-terry-brooks-jr) or e[ReDoc](https://api.little-lemon.xyz/api/docs)

#### _Which ever Method Selected, The Getting Started Steps are the Same_:

1. **Register as a User:** Start by creating an account using the `Create New User` endpoint.
2. **Generate a Token:** Use the `Create Token` endpoint to generate an access token.
3. **Explore Managerial Permissions:** To access manager-specific features, use the `manager_token` in the request header.

## API Documentation

The API follows the OpenAPI 3.0 standard. Here are the main route categories:

- **User Management:** Endpoints for user creation, token generation, and role management.
- **Token Management:** Generate and invalidate tokens for secure access.
- **Inventory Management:** Manage restaurant menu items.
- **Cart Management:** Add, remove, and view items in a user’s cart.
- **Order Management:** Create, update, and delete orders.

For detailed information, refer to the full documentation on [Postman](https://www.postman.com/blackberry-py-dev/workspace/little-lemon-meta-apis-final-terry-brooks-jr) or [ReDoc](https://api.little-lemon.xyz/api/docs)

## Authentication

The Little Lemon API uses **Bearer Token** authentication. To authenticate:

1. Generate a token with the `Create Token` endpoint.
2. Include the token in each request's header as `Authorization: Token <token>`.
3. If a token is invalid or expired, the API will return a 401 Unauthorized error.

#### Example Header

```http
Authorization: Token <your_token_here>
```

## Rate and Usage Limits

This API is intended for educational purposes. Rate limits are as follows:
•	Authenticated Requests: Max 12 requests per minute.
•	Unauthenticated Requests: Max 4 requests per minute.
•	User Creations: Max 10 new users per day.

Exceeding these limits will result in a 429 Too Many Requests response.

Contact

For additional help:
•	[Submit a GitHub Issue](https://github.com/Terry-BrooksJr/little-lemon/issues)
•	Email: [API@little-lemon.xyz](mailto:api.little-lemon.xyz)

## Happy Coding!

