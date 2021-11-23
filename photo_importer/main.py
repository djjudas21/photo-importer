"""
photo-importer
"""

import argparse
import os
import shutil
from pathlib import Path
import exifread

def exifdate(f):
    """
    Read an image file's EXIF data and return the original
    timestamp in YYYY-MM-DD format
    """
    # Open image file for reading (must be in binary mode)
    # TODO: use try when opening file
    image = open(f, 'rb')
    tags = exifread.process_file(image, details=False, stop_tag='DateTimeOriginal')
    # TODO: close file or use "with"
    return tags.get('DateTimeOriginal')


def filetype(extension):
    """
    Determine whether a specific file extension is a photo,
    a video, or something else unknown/unsupported
    """
    filetypes = {
        'jpg': 'photo',
        'cr2': 'photo',
        'heic': 'photo',
        'tiff': 'photo',
        'tif': 'photo',
        'mov': 'video',
        'mp4': 'video',
    }
    result = filetypes.get(extension)
    return result


def main():
    """
    Main function
    """

    # Read in args
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dry-run', help="don't actually move anything", action='store_true')
    parser.add_argument('-q', '--quiet', help="", action='store_true')
    parser.add_argument('-m', '--month', help="", action='store_true')
    parser.add_argument('-s', '--source', help="directory to move items from", default=Path.cwd(), type=str)
    parser.add_argument('-p', '--photo-path', help="directory to move photos to", default=Path.home(), type=str)
    parser.add_argument('-v', '--video-path', help="directory to move videos to", default=Path.home(), type=str)
    args = parser.parse_args()

    # Get files in source dir
    flist = []
    for p in Path(args.source).iterdir():
        if p.is_file():
            print(p)
            flist.append(p)

    # Now loop through all files, assume fully qualified path
    for f in flist:
        # skip if not readable
        if not os.path.isfile(f):
            print(f"{f} is not a file, skipping")
            continue
        if not os.access(f, os.R_OK):
            print(f"{f} is not readable, skipping")
            continue

        # get file name and extension
        pathlibobject = Path(f)
        filename = pathlibobject.name
        extension = pathlibobject.suffix

        # find and parse exif data. skip if no date
        date = exifdate(f)
        if date is None:
            print(f"Could not parse date from {f}, skipping")
            continue

        # skip if not a valid file type
        filetype = filetype(extension)
        if filetype is None:
            print(f"{f} is not a supported file type, skipping")
            continue

        # build dest path using date and filetype
        if filetype == 'photo':
            destpath = os.path.join(args.photo_path, date)
        elif filetype == 'video':
            destpath = os.path.join(args.video_path, date)
        else:
            print(f"{f} is not a supported file type, skipping")
        destname = os.path.join(destpath, filename)

        # mkdir dest path
        if not os.path.isdir(destpath):
            Path.mkdir(destpath, parents=True, exist_ok=True)

        # verify that file isn't already in right place
        if destname == f:
            print(f"{f} does not need to be moved, skipping")
            continue

        # verify that dest file doesn't already exist
        if os.path.isfile(destname):
            print(f"{f} already exists in the destination, skipping")
            continue

        # move file into dest path if not dry run
        if args.dry_run:
            print(f"not moving {f} to {destname} because of --dry-run")
            continue

        print(f"moving {f} to {destname}")
        shutil.move(f, destname)

if __name__ == '__main__':
    main()
