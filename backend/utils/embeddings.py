


def creator_to_document(creator):

    document = f"""
    Creator Name: {creator.name}
    Niche: {creator.niche}
    Platform: {creator.platform}
    Bio: {creator.bio}
    """

    return document.strip()