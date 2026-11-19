import csv
import os
import parselmouth
from parselmouth.praat import call

# GLOBAL CONSTANTS
PITCH_FLOOR = 75.0
PITCH_CEILING = 600.0
INTENSITY_PITCH_FLOOR = 100.0
JITTER_PERIOD_FLOOR = 0.0001
JITTER_PERIOD_CEILING = 0.02
JITTER_MAX_PERIOD_FACTOR = 1.3
SHIMMER_PERIOD_FLOOR = 0.0001
SHIMMER_PERIOD_CEILING = 0.02
SHIMMER_MAX_PERIOD_FACTOR = 1.3
SHIMMER_MAX_AMPLITUDE_FACTOR = 1.6
HNR_TIME_STEP = 0.01
HNR_MIN_PITCH = 75.0
HNR_SILENCE_THRESHOLD = 0.1
HNR_PERIODS_PER_WINDOW = 1.0


PERSONAL_TRANSCRIPTS = {
    "Neutral.wav": "My Mama lives in Memphis",
    "Sad.wav": "My Mama lives in Memphis",
    "Happy.wav": "My Mama lives in Memphis",
    "Angry.wav": "My Mama lives in Memphis",
    "Afraid.wav": "My Mama lives in Memphis",
    "Surprised.wav": "My Mama lives in Memphis",
    "Disgusted.wav": "My Mama lives in Memphis",
}

MSP_TRANSCRIPTS = {
    "Neutral.wav": "referencing more than 200 footnotes and 30 classic texts",
    "Sad.wav": "umm our producer Keith had family issues and then things just kind of kept onnn falling apart",
    "Happy.wav": "when we have two eyes and two ears and fingernails and I am like, oh my gosh, that's so adorable",
    "Angry.wav": "this process that I walked this path with her is she came out",
    "Afraid.wav": "and I I think about uh ah about Trump if he gets power I mean if he actually gets elected I fear for this country's future I fear for the future of human liberty",
    "Surprised.wav": "and I am I am watching people go wait a minute you mean uh mean dr. Carson is",
    "Disgusted.wav": "I mean the more politicians speak the more I want to turn it off uh because they're all bunch of liars and thieves and crooks",
}


def extract_features(audio_file_path, transcript):
    sound = parselmouth.Sound(audio_file_path)

    # Audio duration in seconds
    duration = sound.get_total_duration()  

    # Pitch
    pitch = call(sound, "To Pitch", 0.0, PITCH_FLOOR, PITCH_CEILING)
    pitch_min = call(pitch, "Get minimum", 0, 0, "Hertz", "Parabolic")
    pitch_max = call(pitch, "Get maximum", 0, 0, "Hertz", "Parabolic")
    pitch_mean = call(pitch, "Get mean", 0, 0, "Hertz")
    pitch_sd = call(pitch, "Get standard deviation", 0, 0, "Hertz")

    # Intensity
    intensity = call(sound, "To Intensity", INTENSITY_PITCH_FLOOR, 0.0, "yes")
    intensity_min = call(intensity, "Get minimum", 0, 0, "Parabolic")
    intensity_max = call(intensity, "Get maximum", 0, 0, "Parabolic")
    intensity_mean = call(intensity, "Get mean", 0, 0, "energy")
    intensity_sd = call(intensity, "Get standard deviation", 0, 0)

    # Jitter and Shimmer thru PointProcess
    point_process = call(
        sound, "To PointProcess (periodic, cc)", PITCH_FLOOR, PITCH_CEILING
    )
    jitter_local = call(
        point_process,
        "Get jitter (local)",
        0,
        0,
        JITTER_PERIOD_FLOOR,
        JITTER_PERIOD_CEILING,
        JITTER_MAX_PERIOD_FACTOR,
    )
    shimmer_local = call(
        [sound, point_process],
        "Get shimmer (local)",
        0,
        0,
        SHIMMER_PERIOD_FLOOR,
        SHIMMER_PERIOD_CEILING,
        SHIMMER_MAX_PERIOD_FACTOR,
        SHIMMER_MAX_AMPLITUDE_FACTOR,
    )

    # HNR
    harmonicity = call(
        sound,
        "To Harmonicity (cc)",
        HNR_TIME_STEP,
        HNR_MIN_PITCH,
        HNR_SILENCE_THRESHOLD,
        HNR_PERIODS_PER_WINDOW,
    )
    hnr_mean = call(harmonicity, "Get mean", 0, 0)

    # Speaking Rate (num of words / duration)
    word_count = len(transcript.split())
    speaking_rate = word_count / duration if duration > 0 else 0.0

    return {
        "Speech File": os.path.basename(audio_file_path),
        "Min Pitch": pitch_min,
        "Max Pitch": pitch_max,
        "Mean Pitch": pitch_mean,
        "Sd Pitch": pitch_sd,
        "Min Intensity": intensity_min,
        "Max Intensity": intensity_max,
        "Mean Intensity": intensity_mean,
        "Sd Intensity": intensity_sd,
        "Speaking Rate": speaking_rate,
        "Jitter": jitter_local,
        "Shimmer": shimmer_local,
        "HNR": hnr_mean,
    }


def process_dataset(audio_dir, output_csv, transcripts):
    data = []
    for filename, transcript in transcripts.items():
        file_path = os.path.join(audio_dir, filename)
        features = extract_features(file_path, transcript)
        data.append(features)

    if data:
        dir_name = os.path.dirname(output_csv)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(data[0].keys()))
            writer.writeheader()
            writer.writerows(data)
    
    print('Done processing')


def sound_manipulation(neutral_file_path):
    sound = parselmouth.Sound(neutral_file_path)

    # Intensity Downscaling (-7.25% -> factor 0.9275)
    intensity = call(
        sound, "To Intensity", INTENSITY_PITCH_FLOOR, 0.0, "yes"
    )
    neutral_mean_intensity = call(intensity, "Get mean", 0, 0, "energy")
    target_intensity = neutral_mean_intensity * 0.9275

    sound_for_manip = call(sound, "Copy", "neutral_for_happy")
    call(sound_for_manip, "Scale intensity", target_intensity)

    manipulation = call(
        sound_for_manip, "To Manipulation", 0.01, PITCH_FLOOR, PITCH_CEILING
    )

    # Pitch Upscaling (+14.6% -> factor 1.146)
    pitch_tier = call(manipulation, "Extract pitch tier")
    call(
        pitch_tier,
        "Multiply frequencies",
        sound_for_manip.xmin,
        sound_for_manip.xmax,
        1.146,
    )
    call([pitch_tier, manipulation], "Replace pitch tier")

    # Speaking Rate Decreased (-1.3% -> factor 0.987) 
    ## So duration downscaling (1/0.987 -> factor 1.013)
    duration_tier = call(manipulation, "Extract duration tier")
    duration = sound_for_manip.get_total_duration()
    epsilon = min(0.000001, duration / 1000.0)
    call(
        duration_tier, "Add point", sound_for_manip.xmin + epsilon, 1.013
    )
    call(
        duration_tier, "Add point", sound_for_manip.xmax - epsilon, 1.013
    )
    call([duration_tier, manipulation], "Replace duration tier")

    os.makedirs("bonus", exist_ok=True)
    manipulation_output = "bonus/bonus.Manipulation"
    call(manipulation, "Save as text file", manipulation_output)

    sound_happy = call(manipulation, "Get resynthesis (overlap-add)")
    wav_output = "bonus/bonus.wav"
    sound_happy.save(wav_output, "WAV")

    print("Done manipulation")


def main():
    process_dataset("Devang_recordings", "my_features.csv", PERSONAL_TRANSCRIPTS)

    process_dataset("MSP_samples", "msp_features.csv", MSP_TRANSCRIPTS)

    # bonus manipulation
    neutral_path = os.path.join("Devang_recordings", "Neutral.wav")
    sound_manipulation(neutral_path)


if __name__ == "__main__":
    main()


# Ran below code on Google Colab to transcribe the MSP recordings.
# pip install openai-whisper
# import whisper
# model = whisper.load_model("tiny")
# def get_transcript(filename):
#     result = model.transcribe(filename, initial_prompt="Umm ahh I about ah um hmm uh hm ha haa")
#     return result["text"]