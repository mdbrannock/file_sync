#!/home/daniel/miniconda3/envs/file_sync/bin/python

from fileinput import filename
from os import walk
from os import path
from os import makedirs
from os import remove
from os import rmdir
import shutil
import logging
from datetime import datetime
from pathlib import Path

if __name__ == '__main__':

    # Base directory on computer and drive
    comp_base_dir = '/home/daniel'
    nas_dir = '/mnt/backup/daniel'
    nas_base_dir = path.join(nas_dir, 'Current')

    # Logging stuff
    logger = logging
    logFormatter = logging.Formatter("%(asctime)s %(message)s")
    rootLogger = logging.getLogger()

    now = datetime.now()
    nowString = now.strftime("%Y-%m-%d %H-%M-%S")
    logPath = path.join(nas_dir, 'Logs', nowString)
    Path(logPath).touch()

    fileHandler = logging.FileHandler(logPath)
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    consoleHandler.setLevel(logging.INFO)
    rootLogger.addHandler(consoleHandler)
    rootLogger.setLevel(logging.DEBUG)

    # Initialize dictionaries of files and modified times
    comp_files = {}
    nas_files = {}
    comp_dirs = {}
    nas_dirs = {}

    # List directories to be synced
    sub_dir = ['Documents', 'Projects', 'Pictures', 'Videos', 'Music']

    # Iterate through one top level directory at a time
    for d in sub_dir:
        logging.debug(f'Scanning {d}')

        # Get list of files and modified dates on computer
        comp_path = path.join(comp_base_dir, d)
        for (dirpath, dirnames, filenames) in walk(comp_path):

            # Add directories
            relative_path = dirpath[1+len(comp_base_dir):]
            comp_dirs.update({relative_path: [dirpath, relative_path]})

            # Add files
            files = [path.join(dirpath, filename) for filename in filenames]
            for f in files:
                # Get modified date
                modified_date = int(path.getmtime(f))

                # Get relative path
                relative_path = f[1+len(comp_base_dir):]

                # Create hash (of sorts)
                file_hash = f'{relative_path}{modified_date}'

                # Store modified and relative paths
                comp_files.update({file_hash: [f, relative_path, modified_date]})

        # Get list of directories and files/modified dates on hard drive
        nas_path = path.join(nas_base_dir, d)
        for (dirpath, dirnames, filenames) in walk(nas_path):

            # Add directories
            relative_path = dirpath[1+len(nas_base_dir):]
            nas_dirs.update({relative_path: [dirpath, relative_path, 0]})

            # Add files
            files = [path.join(dirpath, filename) for filename in filenames]
            for f in files:
                # Get modified date
                modified_date = int(path.getmtime(f))

                # Get relative path
                relative_path = f[1+len(nas_base_dir):]

                # Create hash (of sorts)
                file_hash = f'{relative_path}{modified_date}'

                # Store modified and relative paths
                nas_files.update({file_hash: [f, relative_path, modified_date]})

    # What is on the computer that is not on the NAS drive?
    # These need to be added to the NAS
    comp_files_set = set(comp_files.keys())
    comp_dirs_set = set(comp_dirs.keys())
    nas_files_set = set(nas_files.keys())
    nas_dirs_set = set(nas_dirs.keys())
    nas_files_add = comp_files_set.difference(nas_files_set)
    nas_dirs_add = comp_dirs_set.difference(nas_dirs_set)
    logging.info(f'NAS missing or outdated on {len(nas_files_add)} files')
    logging.info(f'NAS missing {len(nas_dirs_add)} directories')

    # What is on the nas drive that is not on the computer?
    # These should be deleted
    nas_files_del = nas_files_set.difference(comp_files_set)
    nas_dirs_del = nas_dirs_set.difference(comp_dirs_set)
    logging.info(f'{len(nas_files_del)} files to replace or remove on NAS')
    logging.info(f'{len(nas_dirs_del)} directories to remove from NAS')

    # Copy missing directories over to the NAS drive first
    for k in nas_dirs_add:
        logging.debug(f'Copying directory {k}')
        dest_path = path.join(nas_base_dir, k)
        # May have already created nested dir, need exist_ok
        makedirs(dest_path, exist_ok=True)

    # Copy missing files to the NAS drive
    for k in nas_files_add:
        logging.debug(f'Copying file {k}')
        paths = comp_files[k]
        source_path = paths[0]
        dest_path = path.join(nas_base_dir, paths[1])
        
        shutil.copy2(source_path, dest_path)
        
    # If files were edited on the computer, then that will have replaced them
    # on the NAS. We don't want to go behind and delete them now, so we have to
    # check the files we were planning to delete from the NAS and make sure none
    # were updated from the computer.
    # Make a copy of nas_files_del so we can remove stuff
    nas_files_del_iter = nas_files_del.copy()
    for cm in nas_files_del_iter:
        paths = nas_files[cm]
        modified_date = int(path.getmtime(paths[0]))

        if modified_date != paths[2]:
            nas_files_del.remove(cm)

    # Updated number of files to remove
    msg = f'{len(nas_files_del)} files to delete on NAS (excludes replacements)'
    logging.info(msg)

    # Print files and directories to be deleted and prompt for confirmation
    if len(nas_files_del) + len(nas_dirs_del) > 0:
        joined_files = '\n'.join(nas_files_del)
        msg = 'Files to be deleted from NAS: \n{}'.format(joined_files)
        logging.info(msg)

        joined_dirs = '\n'.join(nas_dirs_del)
        msg = 'Directories to be deleted from NAS: \n{}'.format(joined_dirs)
        logging.info(msg)

        remove_the_files = input('Proceed with deletion? (n/y)')

        if remove_the_files == 'y': 
            # Delete files first
            for k in nas_files_del:
                logging.debug(f'Deleting file {k}')
                paths = nas_files[k]
                remove(paths[0])
            
            # Next delete directories
            # Sort directories to delete by length.. not very elegant but I
            # really don't want to delete directories recursively.
            nas_dirs_del = list(nas_dirs_del)
            nas_dirs_del.sort(reverse=True, key=len)
            for k in nas_dirs_del:
                logging.debug(f'Removing directory {k}')
                paths = nas_dirs[k]
                rmdir(paths[0])
        else:
            logging.debug(f'User input was {remove_the_files}')
            logging.info('Deleting aborted')

    logging.info("Finishing syncing")