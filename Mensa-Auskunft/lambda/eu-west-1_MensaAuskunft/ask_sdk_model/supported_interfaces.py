# coding: utf-8

#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file
# except in compliance with the License. A copy of the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for
# the specific language governing permissions and limitations under the License.
#

import pprint
import re  # noqa: F401
import six
import typing
from enum import Enum


if typing.TYPE_CHECKING:
    from typing import Dict, List, Optional
    from datetime import datetime
    from ask_sdk_model.interfaces.audioplayer.audio_player_interface import AudioPlayerInterface
    from ask_sdk_model.interfaces.alexa.presentation.apl.alexa_presentation_apl_interface import AlexaPresentationAplInterface
    from ask_sdk_model.interfaces.videoapp.video_app_interface import VideoAppInterface
    from ask_sdk_model.interfaces.geolocation.geolocation_interface import GeolocationInterface
    from ask_sdk_model.interfaces.display.display_interface import DisplayInterface


class SupportedInterfaces(object):
    """
    An object listing each interface that the device supports. For example, if supportedInterfaces includes AudioPlayer {}, then you know that the device supports streaming audio using the AudioPlayer interface.


    :param alexa_presentation_apl: 
    :type alexa_presentation_apl: (optional) ask_sdk_model.interfaces.alexa.presentation.apl.alexa_presentation_apl_interface.AlexaPresentationAplInterface
    :param audio_player: 
    :type audio_player: (optional) ask_sdk_model.interfaces.audioplayer.audio_player_interface.AudioPlayerInterface
    :param display: 
    :type display: (optional) ask_sdk_model.interfaces.display.display_interface.DisplayInterface
    :param video_app: 
    :type video_app: (optional) ask_sdk_model.interfaces.videoapp.video_app_interface.VideoAppInterface
    :param geolocation: 
    :type geolocation: (optional) ask_sdk_model.interfaces.geolocation.geolocation_interface.GeolocationInterface

    """
    deserialized_types = {
        'alexa_presentation_apl': 'ask_sdk_model.interfaces.alexa.presentation.apl.alexa_presentation_apl_interface.AlexaPresentationAplInterface',
        'audio_player': 'ask_sdk_model.interfaces.audioplayer.audio_player_interface.AudioPlayerInterface',
        'display': 'ask_sdk_model.interfaces.display.display_interface.DisplayInterface',
        'video_app': 'ask_sdk_model.interfaces.videoapp.video_app_interface.VideoAppInterface',
        'geolocation': 'ask_sdk_model.interfaces.geolocation.geolocation_interface.GeolocationInterface'
    }  # type: Dict

    attribute_map = {
        'alexa_presentation_apl': 'Alexa.Presentation.APL',
        'audio_player': 'AudioPlayer',
        'display': 'Display',
        'video_app': 'VideoApp',
        'geolocation': 'Geolocation'
    }  # type: Dict

    def __init__(self, alexa_presentation_apl=None, audio_player=None, display=None, video_app=None, geolocation=None):
        # type: (Optional[AlexaPresentationAplInterface], Optional[AudioPlayerInterface], Optional[DisplayInterface], Optional[VideoAppInterface], Optional[GeolocationInterface]) -> None
        """An object listing each interface that the device supports. For example, if supportedInterfaces includes AudioPlayer {}, then you know that the device supports streaming audio using the AudioPlayer interface.

        :param alexa_presentation_apl: 
        :type alexa_presentation_apl: (optional) ask_sdk_model.interfaces.alexa.presentation.apl.alexa_presentation_apl_interface.AlexaPresentationAplInterface
        :param audio_player: 
        :type audio_player: (optional) ask_sdk_model.interfaces.audioplayer.audio_player_interface.AudioPlayerInterface
        :param display: 
        :type display: (optional) ask_sdk_model.interfaces.display.display_interface.DisplayInterface
        :param video_app: 
        :type video_app: (optional) ask_sdk_model.interfaces.videoapp.video_app_interface.VideoAppInterface
        :param geolocation: 
        :type geolocation: (optional) ask_sdk_model.interfaces.geolocation.geolocation_interface.GeolocationInterface
        """
        self.__discriminator_value = None  # type: str

        self.alexa_presentation_apl = alexa_presentation_apl
        self.audio_player = audio_player
        self.display = display
        self.video_app = video_app
        self.geolocation = geolocation

    def to_dict(self):
        # type: () -> Dict[str, object]
        """Returns the model properties as a dict"""
        result = {}  # type: Dict

        for attr, _ in six.iteritems(self.deserialized_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else
                    x.value if isinstance(x, Enum) else x,
                    value
                ))
            elif isinstance(value, Enum):
                result[attr] = value.value
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else
                    (item[0], item[1].value)
                    if isinstance(item[1], Enum) else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        # type: () -> str
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        # type: () -> str
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        # type: (object) -> bool
        """Returns true if both objects are equal"""
        if not isinstance(other, SupportedInterfaces):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        # type: (object) -> bool
        """Returns true if both objects are not equal"""
        return not self == other
