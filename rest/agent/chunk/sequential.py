# Approximate the chunk size for number of tokens
CHUNK_SIZE = 200_000
WINDOW_SIZE = 195_000


def sequential_chunk(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    window_size: int = WINDOW_SIZE,
) -> list[str]:
    r"""Chunk the text sequentially.

    Args:
        text (str): The text to chunk.
        chunk_size (int): The size of each chunk.
        window_size (int): The size of the window to
            slide, which means there is CHUNK_SIZE - WINDOW_SIZE overlap
            size between chunks.

    Returns:
        A list of chunks.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += window_size
    return chunks
