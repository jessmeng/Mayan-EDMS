from __future__ import absolute_import

import errno
import os

from django.utils.translation import ugettext_lazy as _

from .os_specifics import (assemble_suffixed_filename,
    assemble_path_from_list)
from .conf.settings import (FILESERVING_ENABLE, FILESERVING_PATH)
from .conf.settings import SUFFIX_SEPARATOR


def assemble_suffixed_filename(filename, suffix=0):
    """
    Split document filename, to attach suffix to the name part then
    re attacht the extension
    """

    if suffix:
        name, extension = os.path.splitext(filename)
        return SUFFIX_SEPARATOR.join([name, unicode(suffix), os.extsep, extension])
    else:
        return filename


def assemble_path_from_list(directory_list):
    return os.sep.join(directory_list)


def get_instance_path(index_instance):
    """
    Return a platform formated filesytem path corresponding to an
    index instance
    """
    names = []
    for ancestor in index_instance.get_ancestors():
        names.append(ancestor.value)

    names.append(index_instance.value)

    return assemble_path_from_list(names)


def fs_create_index_directory(index_instance):
    if FILESERVING_ENABLE:
        target_directory = assemble_path_from_list([FILESERVING_PATH, get_instance_path(index_instance)])
        try:
            os.mkdir(target_directory)
        except OSError, exc:
            if exc.errno == errno.EEXIST:
                pass
            else:
                raise Exception(_(u'Unable to create indexing directory; %s') % exc)


def fs_create_document_link(index_instance, document, suffix=0):
    if FILESERVING_ENABLE:
        filename = assemble_suffixed_filename(document.file.name, suffix)
        filepath = assemble_path_from_list([FILESERVING_PATH, get_instance_path(index_instance), filename])

        try:
            os.symlink(document.file.path, filepath)
        except OSError, exc:
            if exc.errno == errno.EEXIST:
                # This link should not exist, try to delete it
                try:
                    os.unlink(filepath)
                    # Try again
                    os.symlink(document.file.path, filepath)
                except Exception, exc:
                    raise Exception(_(u'Unable to create symbolic link, file exists and could not be deleted: %(filepath)s; %(exc)s') % {'filepath': filepath, 'exc': exc})
            else:
                raise Exception(_(u'Unable to create symbolic link: %(filepath)s; %(exc)s') % {'filepath': filepath, 'exc': exc})


def fs_delete_document_link(index_instance, document, suffix=0):
    if FILESERVING_ENABLE:
        filename = assemble_suffixed_filename(document.file.name, suffix)
        filepath = assemble_path_from_list([FILESERVING_PATH, get_instance_path(index_instance), filename])

        try:
            os.unlink(filepath)
        except OSError, exc:
            if exc.errno != errno.ENOENT:
                # Raise when any error other than doesn't exits
                raise Exception(_(u'Unable to delete document symbolic link; %s') % exc)


def fs_delete_index_directory(index_instance):
    if FILESERVING_ENABLE:
        target_directory = assemble_path_from_list([FILESERVING_PATH, get_instance_path(index_instance)])
        try:
            os.removedirs(target_directory)
        except OSError, exc:
            if exc.errno == errno.EEXIST:
                pass
            else:
                raise Exception(_(u'Unable to delete indexing directory; %s') % exc)


def fs_delete_directory_recusive(path=FILESERVING_PATH):
    if FILESERVING_ENABLE:
        for dirpath, dirnames, filenames in os.walk(path, topdown=False):
            for filename in filenames:
                os.unlink(os.path.join(dirpath, filename))
            for dirname in dirnames:
                os.rmdir(os.path.join(dirpath, dirname))
