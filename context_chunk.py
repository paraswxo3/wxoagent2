import re
from bisect import bisect_left

def split_text_into_passages(text, model_limit=500, overlap_percentage=0.2):
    # Fix: Use a two-step process instead of lookbehind for non-fixed width patterns
    # First, temporarily replace "Mr.", "Ms.", and "Mrs." to avoid splitting inside them
    text = text.replace("Mr.", "Mr|").replace("Ms.", "Ms|").replace("Mrs.", "Mrs|")

    # Split sentences using ".", "!", or "?" as delimiters
    sentences = re.split(r'(?<=[.!?])\s+', text)

    # Restore "Mr.", "Ms.", and "Mrs."
    sentences = [s.replace("Mr|", "Mr.").replace("Ms|", "Ms.").replace("Mrs|", "Mrs.") for s in sentences]

    passages = []
    overlapping_text = []
    i = 0

    while i < len(sentences):
        passage_text = [sentences[i]]
        accum_lengths = [len(sentences[i])]
        accum_length = len(sentences[i])

        j = i + 1
        while j < len(sentences) and (accum_length + len(sentences[j]) < model_limit):
            passage_text.append(sentences[j])
            accum_length += len(sentences[j])
            accum_lengths.append(accum_length)
            j += 1

        # Store the passage
        passages.append({
            'text': ' '.join(overlapping_text) + ' ' + ' '.join(passage_text),
        })

        # Compute overlap
        start_length = int(accum_length * (1 - overlap_percentage)) + 1
        k = bisect_left(accum_lengths, start_length)

        # Prepare the next overlapping text
        overlapping_text = sentences[i + k:j]

        i = j  # Move to the next passage

    return passages

# Example usage
text = """Mr. John approved the guarantee. The total guarantee amount is USD 500,000. 
In case of default, the bank will pay the amount. Please contact us for any queries!"""

passages = split_text_into_passages(text, model_limit=2048, overlap_percentage=0.25)
for idx, passage in enumerate(passages):
    print(f"Passage {idx+1}: {passage['text']}\n")
