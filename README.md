## Vocalis.io: Your Adaptive Explainable AI Pronunciation Training Companion

<br />

Vocalis is an adaptive, explainable AI-driven pronunciation training companion designed specifically for South Asian English speakers. Unlike traditional Computer-Assisted Pronunciation Training (CAPT) that provide opaque scores or simple "correct/incorrect" feedback, Vocalis leverages [`wav2vec2-large-960h`](https://huggingface.co/facebook/wav2vec2-large-960h) acoustic model on the [`Svarah`](https://huggingface.co/datasets/ai4bharat/Svarah) dataset to perform frame-level phoneme alignment directly from mono 16KHz speech waveforms. The aligned phoneme sequences are analyzed by a custom weighted scoring engine that models pronunciation deviations as assigned errors. These phonological error vectors are then transformed into human-interpretable articulatory explanations by a Groq-hosted [`Llama-4-Scout-17B-16E-Instruct.`](https://huggingface.co/meta-llama/Llama-4-Scout-17B-16E-Instruct)

<hr>

### Getting Started

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

3. Copy The Backend `.env.example` File And Create An `.env` File Based On The Example File

    ```bash
    cp backend/.env.example backend/.env
    ```

4. Edit The Newly Created Backend `.env` File And Enter Your Configuration Values

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

<hr>

### LICENSE

Vocalis.io Is Distributed Under The [MIT LICENSE](https://opensource.org/license/mit). See `LICENSE` For More Information.