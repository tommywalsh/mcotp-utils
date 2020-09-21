import audio_metadata
import re
import logging
from iterator import McotpIterator

"""When possible, add years to the names of album directories

According to the Naming Convention of The People, the names of album directories can optionally begin with a 4-digit
year. This utility finds album directories that do not have years, then tries to figure out the year. If it can do that,
then the directory is renamed.

Note that this really does rename files. It's probably safest to do a filesystem snapshot before you run this command
on your collection, just in case things go wrong.
"""

logging.basicConfig()

# For now the only date string we know how to process is one that ends in 4 digits: 19xx or 20xx
date_pattern = r'((?:19|20)\d\d)$'


def process_date_string(date_string):
    # Given a supported date string, returns a 4-digit string representing the year
    match = re.match(date_pattern, date_string)
    if match:
        return match.group(1)
    logging.error("Unrecognized date string {}".format(date_string))


def get_inferred_dates_for_file(file_path):
    # Reads audio file, and returns a set of possible dates, based on internal metadata.
    dates = set()
    try:
        metadata = audio_metadata.load(file_path)
        if "tags" in metadata:
            if "date" in metadata["tags"]:
                # looks like this returns an array of strings?
                for date_string in metadata["tags"]["date"]:
                    dates.add(process_date_string(date_string))
        if len(dates) == 0:
            logging.info("No dates found for song at {}".format(file_path))
            logging.debug("Metadata for {}:\n{}".format(file_path, metadata))
    except audio_metadata.exceptions.UnsupportedFormat:
        logging.info("Unsupported file format at {}".format(file_path))
    except ValueError:
        logging.info("Illegal value in metadata for {}".format(file_path))
    return dates


class YearGuesser:
    pattern = date_pattern = r'^\d\d\d\d[a-z]? - \S+'

    def __init__(self):
        self.album_years = set()

    def begin_album(self, path_to_album):
        # If the album is already tagged with a year, then we can just skip it.
        if re.match(self.pattern, path_to_album.name):
            return False
        else:
            self.album_years = set()

    def visit_album_song(self, path_to_song):
        self.album_years |= get_inferred_dates_for_file(path_to_song)

    def end_album(self, path_to_album):
        if len(self.album_years) == 1:
            year = self.album_years.pop()
            print("Inferred year {} for album at {}".format(year, path_to_album))
            base_name = path_to_album.name
            new_name = "{} - {}".format(year, base_name)
            new_path = path_to_album.with_name(new_name)
            path_to_album.rename(new_path)
        else:
            message = "Cannot infer year for album at {}".format(path_to_album)
            if len(self.album_years) > 1:
                message += " Candidates are {}".format(self.album_years)
            print(message)
        self.album_years = set()


printer = YearGuesser()
iterator = McotpIterator("/net/server.local/storage/music/mcotp")  # TODO: make this a parameter
iterator.iterate(printer)
