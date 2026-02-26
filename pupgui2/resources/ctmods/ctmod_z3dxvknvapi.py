# pupgui2 compatibility tools module
# DXVK with async patch for Lutris: https://github.com/Sporif/dxvk-async/
# Copyright (C) 2022 DavidoTek, partially based on AUNaseef's protonup

import os
from PySide6.QtCore import QCoreApplication

from pupgui2.resources.ctmods.ctmod_z0dxvk import CtInstaller as DXVKInstaller
from pupgui2.util import build_headers_with_authorization


CT_NAME = 'DXVK NVAPI'
CT_LAUNCHERS = ['pixlwine']
CT_DESCRIPTION = {'en': QCoreApplication.instance().translate('ctmod_z3dxvknvapi', '''Provides an alternative implementation of NVIDIA's NVAPI/NVOFAPI library for usage with DXVK and VKD3D-Proton.<br/>Its way of working is similar to DXVK-AGS, but adjusted and enhanced for NVAPI.<br/><br/>https://github.com/jp7677/dxvk-nvapi/''')}


class CtInstaller(DXVKInstaller):

    CT_URL: str = 'https://api.github.com/repos/jp7677/dxvk-nvapi/releases'
    CT_INFO_URL: str = 'https://github.com/jp7677/dxvk-nvapi/releases/tag/'

    def __get_data(self, version: str, install_dir: str) -> tuple[dict | None, str | None]:

        """
        Get needed download data and path to extract directory.
        Return Type: diple[dict | None, str | None]
        """

        data = self.__fetch_data(version)
        if not data or 'download' not in data:
            return (None, None)

        dxvk_dir = os.path.join(install_dir, "dxvk-nvapi-" + data['version'])

        return (data, dxvk_dir)
