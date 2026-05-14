from transformers import pipeline

from editor.utils.chunking_utils import (
    split_text_into_chunks
)

from editor.utils.cleaning_utils import (
    clean_generated_text
)

# =========================================================
# LOAD QUESTION GENERATION MODEL
# =========================================================

question_generator = pipeline(
    task="text-generation",
    model="gpt2",
    device=-1
)


# =========================================================
# GENERATE QUESTIONS
# =========================================================

def generate_questions(extracted_text):
    """
    Generate descriptive questions from PDF text.
    """

    try:

        if not extracted_text.strip():

            return {
                "success": False,
                "error": "No text available for question generation"
            }

        # Split into chunks
        chunks = split_text_into_chunks(
            extracted_text,
            max_words=350
        )

        all_questions = []

        for chunk in chunks:

            chunk = chunk.strip()

            if len(chunk.split()) < 30:
                continue

            # Take limited chunk text
            short_text = chunk[:600]

            # Create prompt
            prompt = (
                f"Create an educational question from this text:\n\n"
                f"{short_text}\n\n"
                f"Question:"
            )

            # Generate
            result = question_generator(
                prompt,
                max_new_tokens=40,
                do_sample=True,
                temperature=0.7
            )

            generated_text = result[0]["generated_text"]

            # Remove prompt
            generated_question = generated_text.replace(
                prompt,
                ""
            ).strip()

            generated_question = clean_generated_text(
                generated_question
            )

            # Validation
            if (
                generated_question
                and len(generated_question.split()) > 4
            ):

                if not generated_question.endswith("?"):
                    generated_question += "?"

                all_questions.append(
                    generated_question
                )

        # Remove duplicates
        unique_questions = []

        seen = set()

        for q in all_questions:

            q_lower = q.lower()

            if q_lower not in seen:

                seen.add(q_lower)

                unique_questions.append(q)

        if not unique_questions:

            return {
                "success": False,
                "error": "No questions generated"
            }

        return {
            "success": True,
            "questions": unique_questions,
            "total_questions": len(unique_questions),
            "chunks_processed": len(chunks)
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }