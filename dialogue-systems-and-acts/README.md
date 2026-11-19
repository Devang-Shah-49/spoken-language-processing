# Dialogue Act Recognition

A multimodal dialogue-act classification project: engineer linguistic and acoustic features from conversational utterances, analyze their relationship to dialogue acts, and compare text-only, speech-only, and combined classifiers.

## Results

Validation results saved in `classification.ipynb` (19,156 utterances):

| Input features | Selected model | Accuracy | Macro F1 |
|---|---|---:|---:|
| Speech | MLP (128, 64) | 68.15% | 0.2382 |
| Text | Logistic Regression | 84.73% | **0.6777** |
| Speech + Text | Logistic Regression | **84.77%** | 0.6776 |

Text features provide the strongest balance across dialogue-act classes. Combining speech with text yields nearly identical validation performance, while speech alone is substantially weaker. Since accuracy can hide uneven class-level performance, macro F1 is included; the notebook also reports per-class precision, recall, and F1, and plots confusion matrices.

## Implementation

- **Text features:** clean utterance transcripts; combine LIWC and lexical features, dialogue/utterance context, and TF-IDF word uni-/bigrams (up to 200 terms).
- **Speech features:** use Praat-Parselmouth to extract pitch and intensity statistics, voiced fraction, jitter, shimmer, and speaking rate from utterance audio segments.
- **Analysis:** explore class distributions and feature patterns, and run statistical feature/label comparisons with multiple-testing correction.
- **Classification:** compare Logistic Regression, Linear SVM, HistGradientBoosting, and an MLP. Scale features, handle missing acoustic values, and evaluate speech, text, and merged feature sets.

## Notebooks

1. `features.ipynb` — exploratory analysis, feature extraction, and statistical analysis.
2. `classification.ipynb` — preprocessing, model comparison, validation reports, confusion matrices, and test-set predictions.

## Reproduce

Use Python 3 with Jupyter. Install dependencies:

```bash
pip install numpy pandas scipy scikit-learn matplotlib seaborn statsmodels spacy praat-parselmouth tqdm
python -m spacy download en_core_web_sm
```

Provide `train.csv`, `valid.csv`, and `test.csv` with dialogue IDs, speaker IDs, transcripts, dialogue-act labels, and utterance start/end times. Speech extraction also expects a `wav/` directory with recordings named `{dialog_id}_{speaker}.wav`.

Run the notebooks in order from this folder. Feature extraction writes `task1aa/text_features_*.csv` and `speech_features_*.csv`, which the classification notebook loads. Data and recordings are not included in this folder.
