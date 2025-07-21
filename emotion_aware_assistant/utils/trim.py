from emotion_aware_assistant.gloabal_import import *
def trim_to_last_full_sentence(text: str, word_limit: int = 100) -> str:
    words = text.split()
    if len(words) <= word_limit:
        return text  # no trimming needed

    # Trim to just over the word limit
    trimmed = " ".join(words[:word_limit + 20])  # small buffer to avoid chopping mid-sentence

    # Find all complete sentences
    sentences = re.findall(r'[^.?!]*[.?!]', trimmed)
    if not sentences:
        return trimmed.strip()

    # Accumulate sentences until we hit or exceed the limit
    final_sentences = []
    word_count = 0
    for sentence in sentences:
        sentence_words = sentence.strip().split()
        if word_count + len(sentence_words) > word_limit:
            break
        final_sentences.append(sentence.strip())
        word_count += len(sentence_words)

    return " ".join(final_sentences).strip()

def cleanly_truncate(text):
    # Look for the last full stop, question mark, or exclamation mark
    match = re.search(r'(?s)(.*?[\.\?\!])[^\.!\?]*$', text.strip())
    return match.group(1) if match else text.strip()
