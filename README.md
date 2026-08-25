# Raksha — Regional-Language Phishing Detection

Raksha is an AI-based phishing detection system designed to identify and warn users about phishing content written in Indian regional languages and mixed-language formats.

## Problem

Phishing attacks increasingly use regional languages, transliterated text, and code-mixed communication to target users who may be underserved by conventional English-focused phishing detection systems.

A phishing message may combine regional-language wording, English terms, informal spellings, social-engineering tactics, and suspicious URLs. These variations can make detection more challenging for systems designed primarily around standard English-language content.

Raksha aims to address this gap by combining regional-language NLP, phishing classification, URL analysis, and explainable risk scoring.

## Proposed Solution

Raksha will analyze suspicious messages and optional URLs to identify signals associated with phishing and social engineering.

The proposed detection pipeline will include:

- Regional-language and code-mixed text processing
- Language detection and text normalization
- Transliteration handling
- Multilingual NLP-based phishing analysis
- URL and domain analysis
- Machine-learning based classification
- Rule-based phishing indicators
- Risk scoring
- Explainable warnings and recommended actions

The initial prototype will focus on **Kannada and English/code-mixed Kannada-English**, with the architecture designed to support expansion to other Indian regional languages.


## How It Works

Raksha follows a multi-stage detection process:

1. **User Input** — The user provides a suspicious message and, optionally, a URL.

2. **Language Detection & Preprocessing** — The system identifies the language and prepares regional-language, transliterated, and code-mixed text for analysis.

3. **NLP Analysis** — The system analyzes the message for phishing and social-engineering indicators.

4. **URL Analysis** — If a URL is provided, the system analyzes its domain and URL-level characteristics for suspicious patterns.

5. **Risk Scoring** — NLP results, URL signals, and rule-based indicators are combined to determine the overall phishing risk.

6. **Result & Explanation** — Raksha classifies the content as **Safe, Suspicious, or Phishing** and provides the main reasons and recommended action.
   

## Key Features

### Multilingual Phishing Detection

Analyze phishing content written in Indian regional languages and mixed-language formats.

### Regional & Code-Mixed Text Processing

Handle regional-language text, transliterated text, and messages that combine regional languages with English.

### URL Analysis

Identify potentially suspicious URLs using domain and URL-level characteristics.

### Social-Engineering Detection

Identify patterns commonly associated with phishing, including:

- Urgency
- Fear or threats
- Fake rewards
- Account suspension
- KYC-related requests
- Credential requests
- Impersonation

### Risk Classification

Classify analyzed content into:

- **Safe**
- **Suspicious**
- **Phishing**

### Explainable Warnings

Instead of providing only a classification, Raksha is intended to explain why a message was flagged and recommend an appropriate action.

## Technology Stack

| Area | Technology |
|---|---|
| Programming | Python |
| Machine Learning | scikit-learn (Mandatory baseline: TF-IDF + Logistic Regression) |
| Multilingual Models | Hugging Face Transformers (Candidate evaluation: MuRIL / XLM-RoBERTa vs. baseline) |
| Language Processing | Indic language processing + transliteration/code-mix handling |
| URL Analysis | Python URL parsing + local lexical feature extraction (no external network calls) |
| Backend | FastAPI (Stateless monolith) |
| Frontend | React + Vite |
| Database | Stateless MVP (MongoDB Atlas strictly as optional telemetry if time permits) |
| Development | VS Code, Jupyter Notebook |
| Version Control | Git + GitHub |

## Model Development Approach

The implementation mandates a baseline model using:

**TF-IDF + Logistic Regression**

Candidate multilingual transformer models (such as MuRIL and XLM-RoBERTa) will then be evaluated against this mandatory baseline.

The models will be evaluated using:

- Precision
- Recall
- F1-score
- False-positive rate
- Inference latency

Final model selection will depend strictly on empirical evaluation metrics.

## Project Scope

The initial implementation will focus on:

**Language:** Kannada + English / code-mixed Kannada-English

**Platform:** Web-based prototype

The architecture will be designed so that additional Indian regional languages can be supported in future iterations.

## Expected Challenges

- Limited regional-language phishing datasets
- Transliterated and code-mixed text variations
- Informal spelling and language variations
- False positives and false negatives
- Detection of newly created or previously unseen malicious URLs
- Balancing detection accuracy with understandable warnings

## Proposed Implementation Plan

### Phase 1 — Dataset Preparation

Collect and prepare legitimate and phishing examples, including regional-language and code-mixed samples.

### Phase 2 — Preprocessing

Implement language identification, normalization, transliteration handling, tokenization, and URL extraction.

### Phase 3 — Model Development

Develop the baseline classifier and compare it with a multilingual transformer-based model.

### Phase 4 — Phishing Feature Engine

Combine NLP predictions, URL indicators, and rule-based signals into a unified risk assessment.

### Phase 5 — Application Development

Develop the web interface and expose the detection pipeline through FastAPI.

### Phase 6 — Testing

Evaluate the system using unseen regional-language, transliterated, and code-mixed examples.

### Phase 7 — Demonstration

Demonstrate realistic phishing scenarios and show the resulting risk level, reasons, and recommended user action.

## Project Status

> 🚧 **Idea / Proposal Stage**

Raksha is currently being developed as a proposed solution for the **Omnikon International Hackathon — Round 1 Idea Submission**.

No working prototype is being claimed at this stage. The implementation will be developed during the subsequent project phase if the team advances.

## Repository Structure

```text
raksha/
├── backend/          # FastAPI monolithic backend
├── frontend/         # React + Vite single-page frontend
├── models/           # Training scripts, notebooks & baseline models
├── docs/             # Project documentation
├── .agent-spec/docs/ # Local implementation specifications
├── README.md
└── .gitignore
```
The repository structure will evolve as implementation progresses.


## Team

| Member | Role | GitHub |
|---|---|---|
| **Venkatesh B Kulkarni** | Team Lead / Full-Stack & Integration | [@venkateshbk0409](https://github.com/venkateshbk0409) |
| **Prajwal Angadi** | ML / NLP & Backend | [@prajwal-an](https://github.com/prajwal-an) |

### Team Contributions

**Venkatesh B Kulkarni**
- System architecture and project coordination
- Frontend development
- Backend integration
- GitHub and deployment workflow

**Prajwal Angadi**
- NLP and machine-learning pipeline
- Dataset preparation
- Model experimentation and evaluation
- Backend detection logic

Responsibilities may evolve during implementation based on project requirements.

## Third-Party Resources

The project may use third-party libraries, models, APIs, and datasets during implementation.

All third-party resources will be properly attributed in accordance with their respective licenses and terms of use.

## AI Disclosure

Generative AI tools were used during the project for brainstorming, documentation assistance, technical discussion, and reviewing implementation approaches.

The project concept, technical decisions, implementation, testing, and final submission are reviewed and carried out by the team.

## Hackathon

**Omnikon International Hackathon**

**Round 1 — Idea Submission**

## License

This project is being developed as an open-source hackathon project.
