# -*- coding: utf-8 -*-
from unittest import TestCase

from mock import MagicMock, patch

from collections import OrderedDict

class TestOperatingSystem(TestCase):
    def setUp(self):
        self.patcher = patch.dict('sys.modules', {'pyautogui': MagicMock()})
        self.patcher.start()
        from ImageHorizonLibrary import ImageHorizonLibrary
        self.lib = ImageHorizonLibrary()

    def tearDown(self):
        self.patcher.stop()

    def test_launch_application(self):
        mock = MagicMock()
        with patch('subprocess.Popen',
                   autospec=True,
                   return_value=mock) as mock_popen:
            self.lib.launch_application('application -argument')
            mock_popen.assert_called_once_with(['application', '-argument'])
            expected_applications = OrderedDict()
            expected_applications[0] = mock
            self.assertDictEqual(self.lib.open_applications, expected_applications)
            mock_popen.reset_mock()

            self.lib.launch_application('application -a -r --gu ment',
                                        'MY ALIAS')
            mock_popen.assert_called_once_with(['application', '-a',
                                                '-r', '--gu', 'ment'])
            expected_applications['MY ALIAS'] = mock
            self.assertDictEqual(self.lib.open_applications,
                                 expected_applications)
            mock_popen.reset_mock()

            self.lib.launch_application('application', 'ÛMLÄYT ÖLIAS')
            mock_popen.assert_called_once_with(['application'])
            expected_applications['ÛMLÄYT ÖLIAS'] = mock
            self.assertDictEqual(self.lib.open_applications,
                                 expected_applications)


    def test_terminate_application_when_application_was_not_launched(self):
        from ImageHorizonLibrary import OSException
        with self.assertRaises(OSException):
            self.lib.terminate_application()

    def test_terminate_application(self):
        from ImageHorizonLibrary import OSException
        mock = MagicMock()
        with patch('subprocess.Popen',
                   autospec=True,
                   return_value=mock) as mock_popen:
            for args in (('app1',), ('app2', 'my alias'),
                         ('app3', 'youalias'), ('app4', 'shelias')):
                self.lib.launch_application(*args)

            expected_applications = OrderedDict()
            expected_applications[0] = mock
            expected_applications['my alias'] = mock
            expected_applications['youalias'] = mock
            expected_applications['shelias'] = mock

            self.assertDictEqual(self.lib.open_applications, expected_applications)

            self.lib.terminate_application()

            del expected_applications['shelias']
            self.assertDictEqual(self.lib.open_applications,
                                 expected_applications)

            self.lib.terminate_application('my alias')
            del expected_applications['my alias']

            self.assertDictEqual(self.lib.open_applications,
                                 expected_applications)

            self.lib.terminate_application(0) # TODO needs checking
            del expected_applications[0]
            self.assertDictEqual(self.lib.open_applications,
                                 expected_applications)

            self.lib.terminate_application()
            self.assertDictEqual(self.lib.open_applications, {})

            with self.assertRaises(OSException):
                self.lib.terminate_application('nonexistent alias')
