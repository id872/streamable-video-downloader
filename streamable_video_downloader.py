import logging
from argparse import ArgumentParser
from urllib import request


class ExecutionError(Exception):
    pass


def download_video_file_decorator(func_decorated):
    def func_wrapper(*args, **kwargs):
        direct_video_url = func_decorated(*args, **kwargs)

        if not direct_video_url or "https://" not in direct_video_url:
            raise ExecutionError("Video URL not found")

        patterns = ("/video/mp4/", "?")
        file_name = (
            direct_video_url.split(patterns[0])[1].split(patterns[1])[0]
            if patterns[0] in direct_video_url
            else "video.mp4"
        )

        logging.info("Direct link:\n%s\nDownloading...", direct_video_url)
        with open(file_name, "wb") as video_file:
            with request.urlopen(direct_video_url) as req_url:
                video_file.write(req_url.read())
        logging.info("Video downloaded")

    return func_wrapper


def video_url_getter_decorator(fun_decorated):
    def func_wrapper(*args, **kwargs):
        html_content = fun_decorated(*args, **kwargs)
        patterns = ('/><meta property="og:video:url" content="', '"/><meta')
        return (
            html_content.split(patterns[0])[1].split(patterns[1])[0].replace("&amp;", "&")
            if patterns[0] in html_content
            else None
        )

    return func_wrapper


@download_video_file_decorator
@video_url_getter_decorator
def streamable_video_download(streamable_link):
    try:
        logging.info("Downloading video from: %s", streamable_link)
        return str(request.urlopen(streamable_link).read())
    except Exception as exc:
        raise ExecutionError(f"Error: could not download data from {streamable_link}") from exc


def main():
    logging.basicConfig(format="%(asctime)s-%(levelname)s -- %(message)s", level=logging.INFO)

    arg_parser = ArgumentParser()
    arg_parser.add_argument(dest="streamable_url", help="URL to streamable video")
    args = arg_parser.parse_args()

    try:
        streamable_video_download(args.streamable_url)
    except ExecutionError as ex_err:
        logging.error(ex_err)


if __name__ == "__main__":
    main()
