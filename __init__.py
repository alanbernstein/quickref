from .quickref import show_search_results, expand_aliases


def qr(topic):
    """shortcut for using in python shell
    qr('search string') """
    file = expand_aliases(['python'])[0]
    topic = topic if type(topic) == list else [topic]
    return show_search_results(file, topic)
