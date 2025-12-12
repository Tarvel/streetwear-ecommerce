# Wimer - Streetwear Ecommerce Platform

Wimer is a modern streetwear ecommerce platform built with Django. It features a drop-based product release system, comprehensive order management, and secure payment integration.

## Features

- **Product Drops & Collections**: Organize products into "Drops" for limited-time releases.
- **Product Variants**: Support for multiple sizes and colours for each product.
- **Shopping Cart**: Fully functional shopping cart with session persistence.
- **Checkout & Orders**: Secure checkout process with order tracking.
- **Payment Integration**: Integrated with **Paystack** for secure online payments.
- **User Authentication**:
  - Email/Password login and registration.
  - **Google OAuth** integration for one-click sign-in.
- **User Accounts**: Profile management and order history.
- **Gallery & Events**: Sections to showcase brand visuals and upcoming events.
- **Contact Form**: Integrated contact form for customer inquiries.

## Tech Stack

- **Backend**: Django 5.2.4
- **Database**: SQLite (Default)
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: django-allauth
- **Payment**: Paystack API
- **Image Processing**: Pillow

## Prerequisites

- Python 3.10+
- pip (Python package manager)

## Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd wimer
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**

    Create a `.env` file in the root directory (same level as `manage.py`) and add the following variables:

    ```env
    SECRET_KEY=your_django_secret_key
    DEBUG=True
    PAYSTACK_SECRET_KEY=your_paystack_secret_key
    ```

    _Note: For Google OAuth, you will need to configure the Social Application in the Django Admin panel after running migrations._

5.  **Apply database migrations:**

    ```bash
    python manage.py migrate
    ```

6.  **Create a superuser:**

    ```bash
    python manage.py createsuperuser
    ```

7.  **Run the development server:**

    ```bash
    python manage.py runserver
    ```

    Access the application at `http://127.0.0.1:8000/`.

## Configuration

### Google OAuth Setup

1.  Go to the Django Admin (`http://127.0.0.1:8000/admin/`).
2.  Navigate to **Social Accounts** > **Social Applications**.
3.  Add a new Social Application:
    - **Provider**: Google
    - **Name**: Google
    - **Client ID**: Your Google Client ID
    - **Secret Key**: Your Google Client Secret
    - **Sites**: Select `example.com` (or your configured site).
4.  Ensure `django.contrib.sites` is configured correctly (default Site ID is 1).

## Usage

- **Admin Panel**: Use the superuser credentials to access `/admin` to manage products, drops, orders, and users.
- **Storefront**: Browse products, add to cart, and proceed to checkout.
- **User Dashboard**: Users can view their past orders and manage their profile.
