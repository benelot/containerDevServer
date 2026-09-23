---
title: "The CRISP-DM cycle"
weight: 1
---

## What is CRISP-DM?

CRISP-DM (Cross-Industry Standard Process for Data Mining) describes the full lifecycle of a data science project as six phases. It was developed in the 1990s by a consortium of industry practitioners and remains the most widely used process framework for ML projects.

The most important thing to understand about CRISP-DM is that **the cycle is iterative, not linear**. You will find yourself moving backwards — from Evaluation back to Data Preparation, or from Deployment back to Business Understanding — many times during a real project.

## The six phases

```
   Business          Data             Data
  Understanding  Understanding    Preparation
       │               │               │
       ▼               ▼               ▼
  ┌───────────┐  ┌───────────┐  ┌───────────┐
  │ Define    │  │ Explore & │  │ Clean,    │
  │ goal &    │  │ describe  │  │ transform,│
  │ success   │  │ the data  │  │ engineer  │
  │ criteria  │  │           │  │ features  │
  └───────────┘  └───────────┘  └───────────┘
       ▲                               │
       │                               ▼
  ┌───────────┐  ┌───────────┐  ┌───────────┐
  │ Deploy &  │  │ Evaluate  │  │ Model     │
  │ monitor   │  │ against   │  │ select,   │
  │ in prod   │  │ criteria  │  │ train &   │
  │           │  │           │  │ tune      │
  └───────────┘  └───────────┘  └───────────┘
   Deployment     Evaluation      Modelling
       ▲               │
       └───────────────┘
        monitor → re-label → retrain
```

### Business Understanding
Define what you are trying to achieve and how you will know if you succeeded. This is the most neglected phase and the most expensive to skip — a model that answers the wrong question is useless no matter how accurate it is.

### Data Understanding
Explore the data: its structure, distributions, anomalies, and quality. This is where you decide whether you have enough data, whether the labels are reliable, and whether the features you have are actually predictive.

### Data Preparation
Transform raw data into a form the model can learn from. Clean missing values, normalise features, engineer new ones, split into train/test sets, and validate the result. Every transformation should be reproducible and version-controlled.

### Modelling
Select a model family, train it, and tune hyperparameters. In modern ML this phase is highly iterative — you run dozens or hundreds of experiments and use experiment tracking to keep them organised.

### Evaluation
Assess the model against the business criteria you defined in Phase 1. A 94% accuracy rate is meaningless without a baseline and a business case. This phase often sends you back to Data Preparation or Modelling.

### Deployment
Put the model into production and keep it there. This means serving predictions via an API, scheduling retraining, monitoring for data drift and performance degradation, and routing new uncertain samples back to annotation. The loop from Deployment back to Data Understanding is what keeps a deployed model accurate over time.

## Why this matters for the labs

Each lab in this series maps to one or more phases of the CRISP-DM cycle. By the end of all eight labs, you will have touched every phase at least once and built a working end-to-end project on real data.
