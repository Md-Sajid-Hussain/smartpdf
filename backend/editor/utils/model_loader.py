import torch

from transformers import (
    pipeline,
    AutoTokenizer,
    AutoModelForSeq2SeqLM
)


# =========================================================
# FORCE CPU MODE
# =========================================================

DEVICE = -1


# =========================================================
# GLOBAL MODEL VARIABLES
# =========================================================

summarizer_pipeline = None

question_generator_pipeline = None


# =========================================================
# SUMMARIZATION MODEL
# =========================================================

def load_summarizer_model():
    """
    Load BART summarization model once.
    """

    global summarizer_pipeline

    if summarizer_pipeline is None:

        model_name = "facebook/bart-large-cnn"

        tokenizer = AutoTokenizer.from_pretrained(model_name)

        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

        summarizer_pipeline = pipeline(
            "summarization",
            model=model,
            tokenizer=tokenizer,
            device=DEVICE
        )

    return summarizer_pipeline


# =========================================================
# QUESTION GENERATION MODEL
# =========================================================

def load_question_generator_model():
    """
    Load T5 question generation model once.
    """

    global question_generator_pipeline

    if question_generator_pipeline is None:

        model_name = "valhalla/t5-base-qg-hl"

        tokenizer = AutoTokenizer.from_pretrained(model_name)

        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

        question_generator_pipeline = pipeline(
            "text2text-generation",
            model=model,
            tokenizer=tokenizer,
            device=DEVICE
        )

    return question_generator_pipeline


# =========================================================
# MEMORY / DEVICE INFO
# =========================================================

def get_model_device():
    """
    Returns current AI device.
    """

    return "cpu"


# =========================================================
# OPTIONAL MODEL WARMUP
# =========================================================

def warmup_models():
    """
    Optional preload to avoid first-request delay.
    """

    try:

        load_summarizer_model()

        load_question_generator_model()

        return True

    except Exception as e:

        print("Model warmup failed:", str(e))

        return False