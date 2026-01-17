from youtube_transcript_api import YouTubeTranscriptApi

def get_video_transcript(video_id: str) -> str:
    """
    Fetches the transcript for a given video ID.
    Returns the concatenated text or None if disabled/unavailable.
    """
    try:
        # Try to list transcripts first
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Try fetching manual english, or generated english, or just the first available
        try:
            transcript = transcript_list.find_generated_transcript(['en'])
        except:
            try:
                transcript = transcript_list.find_manually_created_transcript(['en'])
            except:
                # Fallback to whatever is first
                transcript = next(iter(transcript_list))
        
        fetched = transcript.fetch()
        full_text = " ".join([entry['text'] for entry in fetched])
        return full_text

    except Exception as e:
        # Transcript might be disabled or unavailable
        print(f"Error fetching transcript for {video_id}: {e}")
        return None
