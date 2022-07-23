def join_url_with_slashes(main_url, *args):
    url = "https://" + main_url
    for part in args:
        url = "/".join([url, part])
    return url
