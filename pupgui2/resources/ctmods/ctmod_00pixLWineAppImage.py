# pupgui2 compatibility tools module
# Proton-GE
# Copyright (C) 2021 DavidoTek, partially based on AUNaseef's protonup

import os
import requests
import hashlib

from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QObject, QCoreApplication, Signal, Property

from pupgui2.datastructures import Launcher
from pupgui2.util import fetch_project_release_data, fetch_project_releases
from pupgui2.util import get_launcher_from_installdir, extract_tar
from pupgui2.util import build_headers_with_authorization
from pupgui2.networkutil import download_file


CT_NAME = 'pixL-Wine-AppImage'
CT_LAUNCHERS = ['pixlwine']
CT_DESCRIPTION = {'en': QCoreApplication.instance().translate('ctmod_00pixLWineAppImage', '''This is the "Legacy" AppImage that we used with pixL.<br/><br/><b>This is meant to be used for testing principally.</b>''')}


class CtInstaller(QObject):

    BUFFER_SIZE = 65536
    CT_URL = 'https://api.github.com/repos/pixl-os/WINE_AppImage/releases'
    CT_INFO_URL = 'https://github.com/pixl-os/WINE_AppImage/releases/tag/'

    p_download_progress_percent = 0
    download_progress_percent = Signal(int)
    message_box_message = Signal(str, str, QMessageBox.Icon)

    def __init__(self, main_window = None):
        super(CtInstaller, self).__init__()
        self.p_download_canceled = False

        self.release_format = '.AppImage'

        self.rs = requests.Session()
        rs_headers = build_headers_with_authorization({}, main_window.web_access_tokens, 'github')
        self.rs.headers.update(rs_headers)

    def get_download_canceled(self):
        return self.p_download_canceled

    def set_download_canceled(self, val):
        self.p_download_canceled = val

    download_canceled = Property(bool, get_download_canceled, set_download_canceled)

    def __set_download_progress_percent(self, value : int):
        if self.p_download_progress_percent == value:
            return
        self.p_download_progress_percent = value
        self.download_progress_percent.emit(value)

    def __download(self, url: str, destination: str, known_size: int = 0) -> bool:
        """
        Download files from url to destination
        Return Type: bool
        """
        try:
            return download_file(
                url=url,
                destination=destination,
                progress_callback=self.__set_download_progress_percent,
                download_cancelled=self.download_canceled,
                buffer_size=self.BUFFER_SIZE,
                stream=True,
                known_size=known_size
            )
        except Exception as e:
            print(f"Failed to download tool {CT_NAME} - Reason: {e}")

            self.message_box_message.emit(
                self.tr("Download Error!"),
                self.tr(
                    "Failed to download tool '{CT_NAME}'!\n\nReason: {EXCEPTION}".format(CT_NAME=CT_NAME, EXCEPTION=e)),
                QMessageBox.Icon.Warning
            )

    def __sha256sum(self, filename):
        """
        Get SHA256 checksum of a file
        Return Type: str
        """
        sha256sum = hashlib.sha256()
        with open(filename, 'rb') as file:
            while True:
                data = file.read(self.BUFFER_SIZE)
                if not data:
                    break
                sha256sum.update(data)
        return sha256sum.hexdigest()

    def __fetch_github_data(self, tag):
        """
        Fetch GitHub release information
        Return Type: dict
        Content(s):
            'version', 'date', 'download', 'size', 'checksum'
        """

        return fetch_project_release_data(self.CT_URL, self.release_format, self.rs, tag=tag)

    def __get_data(self, version: str) -> dict | None:

        """
        Get needed download data
        Return Type: dict | None
        """
        print(f"version: {version}")
        data = self.__fetch_github_data(version)
        print(f"data: {data}")
        if not data or 'download' not in data:
            return None

        return data

    def is_system_compatible(self) -> bool:
        """
        Are the system requirements met?
        Return Type: bool
        """
        return True

    def fetch_releases(self, count: int = 100, page: int = 1) -> list[str]:
        """
        List available releases
        Return Type: str[]
        """

        return fetch_project_releases(self.CT_URL, self.rs, count=count, page=page)

    def get_tool(self, version, install_dir, temp_dir):
        """
        Download and install the compatibility tool
        Return Type: bool
        """

        print(f"install_dir: {install_dir}")
        
        data = self.__get_data(version)
        if not data:
            return False

        download_appimage = os.path.join(temp_dir, data['download'].split('/')[-1])
        
        installed_appimage = os.path.join(install_dir, data['download'].split('/')[-1])

        #check if appimage already exists
        if os.path.exists(installed_appimage):
                return False

        if not self.__download(url=data['download'], destination=download_appimage):
            return False

        download_checksum = self.__sha256sum(download_appimage)
        if data['checksum'] and (download_checksum not in data['checksum']):
            return False

        #install AppImage by moving and add execution right
        os.system('mv ' + download_appimage + ' ' + installed_appimage)
        os.system('chmod +x ' + installed_appimage)

        self.__set_download_progress_percent(100)

        return True

    def get_info_url(self, version: str) -> str:
        """
        Get link with info about version (eg. GitHub release page)
        Return Type: str
        """
        return self.CT_INFO_URL + version
