# Speech Analysis and Feature Extraction

Systematic extraction + analysis of prosodic and voice quality parameters from emotional speech recordings to characterize the acoustic correlates of human emotion.

### Emotions evaluated

- Neutral
- Happy
- Sad
- Angry
- Afraid
- Surprised
- Disgusted

### Considered Features

1. **Pitch**: Min, Max, Mean, Standard Deviation
2. **Intensity**: Min, Max, Mean, Standard Deviation
3. **Voice Quality**: Jitter, Shimmer, Harmonics-to-Noise Ratio (HNR)
4. **Temporal**: Speaking Rate (words per second)

## Dependencies

Ensure you have Python 3.x installed

```bash
pip install praat-parselmouth openai-whisper
```

To transcribe (speech-to-text) MSP recordings, `get_transcript()` uses open-ai whisper model. This function can be executed on Google colab easily. But to locally reproduce on MacOS, install `ffmpeg`:

```bash
brew install ffmpeg
```

For simplicity, I have hardcoded the transcriptions and commented the `get_transcript()` function.

## Reproduce code

- My emotion recordings (reading "My mama lives in Memphis") are present in `./Devang_recordings`
- MSP Podcast speech recordings are present in `./MSP_samples`

### Running the Script

```bash
python features_extract.py
```

The script will:

- Generate `my_features.csv` with features from your recordings
- Generate `msp_features.csv` with features from msp_samples

### Format of CSV file

- **Speech File**: filename of emotion (Happy, Angry, Sad, Afraid, Surprised, Disgusted, Neutral)
- **Min/Max/Mean/Sd Pitch**: pitch statistics in Hz (frequency)
- **Min/Max/Mean/Sd Intensity**: intensity statistics in dB (loudness)
- **Speaking Rate**: words spoken per second (`total_number_of_words_spoken_in_audio / total_audio_duration`)
- **Jitter**: Variations in pitch period (voice quality)
- **Shimmer**: Variations in amplitude (voice quality)
- **HNR**: harmonics-to-noise ratio in dB (voice quality)
