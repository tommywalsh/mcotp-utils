from pathlib import Path
import logging


class _TaskWrapper(object):

    """For internal use by McotpIterator.
    Each client of McotpIterator must provide an object that has "callbacks" that are called throughout the iteration
    process (see details below). This class wraps the client-provided object so that the client only needs to bother
    providing the callbacks that they need. Anything left unimplemented will be handled by this class as no-ops.
    """
    def __init__(self, wrapped):
        self.wrapped = wrapped

    @staticmethod
    def _safe_call(call):
        try:
            result = call()
            if result is False:
                return False
        except AttributeError:
            pass
        return True

    def begin_collection(self, path_to_collection):
        return self._safe_call(lambda: self.wrapped.begin_collection(path_to_collection))

    def end_collection(self, path_to_collection):
        return self._safe_call(lambda: self.wrapped.end_collection(path_to_collection))

    def begin_band(self, path_to_band):
        return self._safe_call(lambda: self.wrapped.begin_band(path_to_band))

    def end_band(self, path_to_band):
        return self._safe_call(lambda: self.wrapped.end_band(path_to_band))

    def begin_album(self, path_to_album):
        return self._safe_call(lambda: self.wrapped.begin_album(path_to_album))

    def end_album(self, path_to_album):
        return self._safe_call(lambda: self.wrapped.end_album(path_to_album))

    def visit_album_song(self, path_to_song):
        return self._safe_call(lambda: self.wrapped.visit_album_song(path_to_song))

    def visit_loose_song(self, path_to_song):
        return self._safe_call(lambda: self.wrapped.visit_loose_song(path_to_song))


class McotpIterator(object):
    """Object that knows how to iterate over the music collection of the people.
    """

    def __init__(self, full_path_to_mcotp):
        self.root = Path(full_path_to_mcotp)

    def iterate(self, iterator_tasks):
        """Kicks off an iteration.
        This method expects to be passed an object with some/all of the following methods, which are called as described

        begin_collection, end_collection -- called at the very beginning and end of the iteration

        begin_band, end_band -- called when we start and finish processing on a particular band. If you return "false"
             from begin_band, then the iterator will skip over the band.

        begin_album, end_album -- called when we start/finish processing an album. Note that these calls will happen
             after a begin_band call, and before the corresponding end_band call.  If you return "false" from
             begin_album, then the iterator will skip over the album.

        visit_album_song -- called once for each song file inside an album. This call will happen after a begin_album
             call, and before the corresponding end_album call

        visit_loose_song -- called once for each non-album song. This call will happen after a begin_band call, and
            before the corresponding end_band call. This will never be called in between a begin_album/end_album pair.
        """

        tasks = _TaskWrapper(iterator_tasks)
        tasks.begin_collection(self.root)
        for mcotp_item in [x for x in self.root.iterdir() if not x.name.startswith('[')]:
            if mcotp_item.is_dir():
                self._iterate_band_dir(mcotp_item, tasks)
            else:
                logging.error("Illegal top-level file found: {}".format(mcotp_item))
        tasks.end_collection(self.root)

    def _iterate_band_dir(self, band_path, tasks):
        if not tasks.begin_band(band_path):
            return
        for band_item in [x for x in band_path.iterdir() if not x.name.startswith('[')]:
            if band_item.is_dir():
                self._iterate_album_dir(band_item, tasks)
            else:
                tasks.visit_loose_song(band_item)
        tasks.end_band(band_path)

    @staticmethod
    def _iterate_album_dir(album_path, tasks):
        if not tasks.begin_album(album_path):
            return
        for album_item in [x for x in album_path.iterdir() if not x.name.startswith('[')]:
            if album_item.is_file():
                tasks.visit_album_song(album_item)
            else:
                logging.error("Illegal non-regular file found at {}".format(album_item))
        tasks.end_album(album_path)
