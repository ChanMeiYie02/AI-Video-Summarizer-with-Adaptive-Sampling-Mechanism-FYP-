# Gemma-4-E2B Speech Transcription Noise Robustness Report

**Date Executed:** 2026-07-27 16:13:13
**Total Samples Evaluated:** 1000 / 1000

## Executive Summary
This report evaluates the noise-tolerance capabilities of **Gemma-4-E2B** using short voice segments mixed with 10 noise types at 4 SNR levels (0dB, 5dB, 10dB, 15dB).

- **Overall Word Error Rate (WER):** 25.19%
- **Overall Exact Match (EM) Accuracy:** 48.00%

### Model Capability Statement
> Gemma-4-E2B is capable of accepting noise levels at **15 dB and above** (maintaining an average WER below 15%).

## Performance by Signal-to-Noise Ratio (SNR)
Lower SNR indicates higher levels of background noise.

| SNR Level | Sample Count | Word Error Rate (WER) | Exact Match (EM) Accuracy |
| :---: | :---: | :---: | :---: |
| 0 dB | 250 | 50.34% | 26.40% |
| 5 dB | 250 | 22.42% | 46.80% |
| 10 dB | 250 | 15.75% | 57.60% |
| 15 dB | 250 | 12.26% | 61.20% |

## Performance by Noise Category

| Noise Category | Sample Count | Word Error Rate (WER) | Exact Match (EM) Accuracy |
| :--- | :---: | :---: | :---: |
| Babble | 100 | 62.84% | 23.00% |
| Cafeteria | 100 | 27.99% | 43.00% |
| Car | 100 | 8.55% | 70.00% |
| Kitchen | 100 | 12.36% | 62.00% |
| Meeting | 100 | 33.93% | 34.00% |
| Metro | 100 | 11.87% | 61.00% |
| Restaurant | 100 | 34.76% | 37.00% |
| Ssn | 100 | 29.86% | 40.00% |
| Station | 100 | 17.29% | 48.00% |
| Traffic | 100 | 12.49% | 62.00% |

## Performance Matrix (WER / EM Accuracy)

| Noise Category | 15 dB | 10 dB | 5 dB | 0 dB |
| :--- | :---: | :---: | :---: | :---: |
| Babble | 26.6% / 40.0% | 30.2% / 32.0% | 40.2% / 20.0% | 154.3% / 0.0% |
| Cafeteria | 6.9% / 64.0% | 17.8% / 56.0% | 23.5% / 48.0% | 63.8% / 4.0% |
| Car | 15.8% / 64.0% | 6.7% / 68.0% | 5.4% / 76.0% | 6.3% / 72.0% |
| Kitchen | 6.4% / 80.0% | 11.6% / 68.0% | 9.8% / 64.0% | 21.6% / 36.0% |
| Meeting | 22.2% / 56.0% | 22.9% / 52.0% | 33.6% / 24.0% | 57.0% / 4.0% |
| Metro | 6.4% / 68.0% | 8.1% / 60.0% | 12.1% / 64.0% | 20.9% / 52.0% |
| Restaurant | 14.2% / 48.0% | 11.7% / 60.0% | 38.8% / 32.0% | 74.3% / 8.0% |
| Ssn | 8.4% / 64.0% | 22.3% / 52.0% | 30.4% / 32.0% | 58.3% / 12.0% |
| Station | 10.2% / 48.0% | 15.9% / 60.0% | 18.8% / 48.0% | 24.3% / 36.0% |
| Traffic | 5.5% / 80.0% | 10.4% / 68.0% | 11.5% / 60.0% | 22.6% / 40.0% |

## Sample Discrepancies / Errors
Here are some examples where Gemma-4's prediction diverged from the ground truth:

| File | Category | SNR | Ground Truth | Gemma-4 Prediction | WER |
| :--- | :--- | :---: | :--- | :--- | :---: |
| p254_228 | meeting | 5 dB | "Her condition was yesterday described as critical, but stable." | "Found that her condition was yesterday described as critical." | 44.4% |
| p267_145 | metro | 10 dB | "We will turn the corner." | "We will turn the cone." | 20.0% |
| p227_311 | metro | 10 dB | "I'm looking for work in Bath and back home in Scotland." | "Hi, I'm looking for work in Bath and Backham in Scotland." | 25.0% |
| p231_375 | station | 10 dB | "Here is a weather forecast for the weekend." | "Here is the weather forecast for the weekend." | 12.5% |
| p243_001 | babble | 15 dB | "Please call Stella." | "Hola Stella." | 66.7% |
| p269_224 | meeting | 5 dB | "Who was on the panel?" | "Hey, it was on the panel." | 40.0% |
| p270_435 | metro | 0 dB | "It is not an inquiry to clear the athletes." | "This is not an inquiry to clear the athletes." | 11.1% |
| p236_112 | meeting | 0 dB | "I've heard this stuff about the markets." | "I'm in not. I've had this stuff about market." | 87.5% |
| p239_036 | station | 0 dB | "That can cost him a fortune." | "That can cost a fortune." | 16.7% |
| p270_210 | cafeteria | 10 dB | "This decision will prove to be the opposite of a standstill." | "If you desire to prove to be the opposite of a standstillo" | 45.5% |
