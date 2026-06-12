## Vocalis.io: Your Adaptive Explainable AI Pronunciation Training Companion

<img src="assets/Vocalis.io.gif" width="100%" alt="Vocalis.io">

<p align="center">
  <img src="https://shieldcn.dev/github/ci/vercel/next.js.svg?variant=outline&mode=light&size=xs&animate=glow" alt="GitHub CI" />
  &nbsp;
  <img src="https://shieldcn.dev/badge/made%20with-%E2%9D%A4-red.svg?variant=outline&size=xs&mode=light" alt="Made with Love" />
</p>

Vocalis is an adaptive, explainable AI-driven pronunciation training companion designed specifically for South Asian English speakers. Unlike traditional Computer-Assisted Pronunciation Training (CAPT) that provide opaque scores or simple "correct/incorrect" feedback, Vocalis leverages [`wav2vec2-large-960h`](https://huggingface.co/facebook/wav2vec2-large-960h) acoustic model finetuned on the [`Svarah`](https://huggingface.co/datasets/ai4bharat/Svarah) dataset to perform frame-level phoneme alignment directly from mono 16KHz speech waveforms. The aligned phoneme sequences are analyzed by a custom weighted scoring engine that models pronunciation deviations as assigned errors. These phonological error vectors are then transformed into human-interpretable articulatory explanations by a Groq-hosted [`Llama-4-Scout-17B-16E-Instruct.`](https://huggingface.co/meta-llama/Llama-4-Scout-17B-16E-Instruct)

During the benchmarking process, the finetuned [`wav2vec2-large-960h`](https://huggingface.co/facebook/wav2vec2-large-960h) acoustic model trained on the [`Svarah`](https://huggingface.co/datasets/ai4bharat/Svarah) dataset was benchmarked against three models: a pretrained baseline [`wav2vec2-base-960h`](https://huggingface.co/facebook/wav2vec2-base-960h), a multilingual [`mms-1b-all`](https://huggingface.co/facebook/mms-1b-all), and a [`distil-large-v3`](https://huggingface.co/distil-whisper/distil-large-v3) model. The results are displayed below.

<br />

<div align="center"> 

<table width="100%" border="1" cellpadding="6" rules="all">
  <thead>
    <tr bgcolor="#595959">
      <th width="28%">Model</th>
      <th width="18%">WER</th>
      <th width="18%">CER</th>
      <th width="12%">Precision</th>
      <th width="12%">Recall</th>
      <th width="12%">F1 Score</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Standard Wav2Vec2</td>
      <td>0.5247</td>
      <td>0.2567</td>
      <td>0.5607</td>
      <td>0.5844</td>
      <td>0.5723</td>
    </tr>
    <tr>
      <td>MMS-1B</td>
      <td>0.3236</td>
      <td>0.1349</td>
      <td>0.7086</td>
      <td>0.7092</td>
      <td>0.7089</td>
    </tr>
    <tr>
      <td>Distil-Whisper</td>
      <td>0.0918</td>
      <td>0.0416</td>
      <td>0.9225</td>
      <td>0.9266</td>
      <td>0.9246</td>
    </tr>
    <tr>
      <td><strong>Fine-Tuned Wav2Vec2</strong></td>
      <td>0.1584</td>
      <td>0.0547</td>
      <td>0.7900</td>
      <td>0.7751</td>
      <td>0.7824</td>
    </tr>
  </tbody>
</table>

</div>

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
