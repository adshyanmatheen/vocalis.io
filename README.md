## Vocalis.io: Your Adaptive Explainable AI-Driven Pronunciation Training Companion

<br />

### Getting Started

<br />

The Following Instructions Are To Clone And Configure An Instance Of Vocalis.io Within Your Local Environment.

#### The Pre-Requisites Before Cloning And Configuring Vocalis.io

This Technology Is Required For Configuring An Instance Of Vocalis.io Within Your Local Environment.


1. Install The Docker Containerization Platform

    ```bash
    curl -fsSL https://get.docker.com | sh
    ```


#### The Instructions For Cloning And Configuring Vocalis.io

These Instructions Are Required For Configuring An Instance Of Vocalis.io Within Your Local Environment.

1. Clone The GitHub Repository Using The GitHub CLI

    ```bash
    gh repo clone adshyanmatheen/vocalis.io 
    ```

2. Navigate To The Cloned Repository

    ```bash
    cd vocalis.io
    ```

3. Copy The `.env.example` File And Create An `.env` File Based On The Example File

    ```bash
    cp .env.example .env
    ```

4. Edit The Newly Created `.env` File And Enter Your Configuration Values

    ```ini
    DATABASE_URL="Enter Your Database URL Here"
    JWT_SECRET_KEY="Enter Your JWT Secret Key Here"
    SENTRY_DSN="Enter Your Sentry DSN Key Here"
    GROQ_API_KEY="Enter Your Groq API Key Here"
    HUGGINGFACE_TOKEN="Enter Your Hugging Face Token Here"
    ```

5. Build And Start The Virtual Containerized Instance Of Vocalis.io Using Docker Compose

    ```bash
    docker compose up --build
    ```

### LICENSE

Vocalis.io Is Distributed Under The [MIT LICENSE](https://opensource.org/license/mit). See `LICENSE` For More Information.