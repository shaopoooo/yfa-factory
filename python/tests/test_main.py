import unittest
import sys
import os
import time
import json
from mock import patch, MagicMock, call

# Add parent directory to path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main

class TestFactoryControl(unittest.TestCase):

    @patch('main.get_db_connection')
    @patch('main.requests')
    @patch('main.time')
    def test_run_led_control_basic_on(self, mock_time, mock_requests, mock_get_db):
        """Test LED control: Turn ON when within simple time range"""
        # Mock time to 10:00:00
        mock_time.strftime.return_value = "10" 
        mock_time.localtime.return_value = time.struct_time((2025, 12, 30, 10, 0, 0, 1, 364, 0))

        # Mock DB connection and cursor
        mock_cursor = MagicMock()
        mock_db_conn = MagicMock()
        mock_get_db.return_value = mock_db_conn
        mock_db_conn.cursor.return_value = mock_cursor

        # Mock DB result: One LED, active (limit 09:00 to 18:00)
        # Columns based on main.py usage:
        # i[1]=ip, i[2]=address, i[6]=start_time, i[7]=end_time, i[11]=start_time2, i[12]=end_time2
        # Mocking a tuple with enough elements (indices go up to 12)
        #                 0,  1,       2,    3, 4, 5, 6,      7,      8, 9, 10, 11,     12
        mock_row = (None, '1.2.3.4', '1', None, 0, 0, '0900', '1800', 0, 0, 0, 'None', 'None')
        mock_cursor.fetchall.return_value = [mock_row]

        # Mock requests.get response (current status is 0/OFF)
        mock_response = MagicMock()
        mock_response.text = json.dumps({'io': {'do': {'1': {'doStatus': 0}}}})
        mock_requests.get.return_value = mock_response

        # Execute
        main.run_led_control()

        # Verify DB select
        mock_cursor.execute.assert_any_call("SELECT * FROM control_led where control = 'auto';")

        # Verify Switch turned ON (requests.put called because current=0, target=1)
        # Expected Logic: 09 <= 10 < 18 -> ON (1)
        # Check Hand_switch call logic -> requests.put
        self.assertTrue(mock_requests.put.called)
        
        # Verify DB Update (cs='1')
        mock_cursor.execute.assert_any_call("UPDATE control_led SET control_status = '1' WHERE ip = '1.2.3.4' AND address= 1;")

    @patch('main.get_db_connection')
    @patch('main.requests')
    @patch('main.time')
    def test_run_led_control_basic_off(self, mock_time, mock_requests, mock_get_db):
        """Test LED control: Turn OFF when outside simple time range"""
        # Mock time to 20:00:00
        mock_time.strftime.return_value = "20" 

        # Mock DB
        mock_cursor = MagicMock()
        mock_get_db.return_value = MagicMock(cursor=MagicMock(return_value=mock_cursor))
        # Same row: 09-18
        mock_row = (None, '1.2.3.4', '1', None, 0, 0, '0900', '1800', 0, 0, 0, 'None', 'None')
        mock_cursor.fetchall.return_value = [mock_row]

        # Mock requests (current status is 1/ON)
        mock_response = MagicMock()
        mock_response.text = json.dumps({'io': {'do': {'1': {'doStatus': 1}}}})
        mock_requests.get.return_value = mock_response

        # Execute
        main.run_led_control()

        # Verify Switch turned OFF (requests.put called because current=1, target=0)
        self.assertTrue(mock_requests.put.called)
        
        # Verify DB Update (cs='0')
        mock_cursor.execute.assert_any_call("UPDATE control_led SET control_status = '0' WHERE ip = '1.2.3.4' AND address= 1;")

    @patch('main.get_db_connection')
    @patch('main.requests')
    @patch('main.time')
    def test_run_motor_control_on_phase(self, mock_time, mock_requests, mock_get_db):
        """Test Motor control: ON phase (within minute_cycle)"""
        # Mock time to 10:05:00 (Total minutes = 605)
        # Cycle: 1 hour (60 mins). Position = 605 % 60 = 5
        # minute_cycle = 10. Position 5 < 10 -> ON
        mock_time.localtime.return_value = time.struct_time((2025, 12, 30, 10, 5, 0, 1, 364, 0))
        mock_time.strftime.return_value = "2025-12-30 10:05:00"

        # Mock DB
        mock_cursor = MagicMock()
        mock_get_db.return_value = MagicMock(cursor=MagicMock(return_value=mock_cursor))
        
        # Mock row
        # Indexes: i[1]=ip, i[2]=address, i[6]=hour_cycle, i[7]=minute_cycle
        # i[6]=1 (1 hour cycle), i[7]=10 (10 mins on)
        mock_row = (None, '1.2.3.4', '2', None, 0, 0, 1, 10, 0, 0, 0)
        mock_cursor.fetchall.return_value = [mock_row]

        # Mock requests (current status OFF '0')
        mock_response = MagicMock()
        mock_response.text = json.dumps({'io': {'do': {'2': {'doStatus': 0}}}})
        mock_requests.get.return_value = mock_response

        # Execute
        main.run_motor_control()

        # Verify Hand_switch turned ON
        self.assertTrue(mock_requests.put.called)

        # Verify DB Update
        # position=5. minute_timer = 10-5 = 5. hour_timer = 0.
        mock_cursor.execute.assert_any_call("UPDATE control_motor SET hour_timer = '0', minute_timer = '5' WHERE ip = '1.2.3.4' AND address = 2;")

    @patch('main.get_db_connection')
    @patch('main.requests')
    @patch('main.time')
    def test_run_motor_control_off_phase(self, mock_time, mock_requests, mock_get_db):
        """Test Motor control: OFF phase (outside minute_cycle)"""
        # Mock time to 10:15:00 (Total minutes = 615)
        # Cycle: 1 hour. Position = 15
        # minute_cycle = 10. Position 15 >= 10 -> OFF
        mock_time.localtime.return_value = time.struct_time((2025, 12, 30, 10, 15, 0, 1, 364, 0))
        mock_time.strftime.return_value = "2025-12-30 10:15:00"

        # Mock DB
        mock_cursor = MagicMock()
        mock_get_db.return_value = MagicMock(cursor=MagicMock(return_value=mock_cursor))
        
        # Mock row: 1 hour cycle, 10 mins on
        mock_row = (None, '1.2.3.4', '2', None, 0, 0, 1, 10, 0, 0, 0)
        mock_cursor.fetchall.return_value = [mock_row]

        # Mock requests (current status ON '1')
        mock_response = MagicMock()
        mock_response.text = json.dumps({'io': {'do': {'2': {'doStatus': 1}}}})
        mock_requests.get.return_value = mock_response

        # Execute
        main.run_motor_control()

        # Verify Hand_switch turned OFF
        self.assertTrue(mock_requests.put.called)

        # Verify DB Update
        # position=15. minute_timer = 0. hour_timer = 60 - 15 = 45.
        mock_cursor.execute.assert_any_call("UPDATE control_motor SET hour_timer = '45', minute_timer = '0' WHERE ip = '1.2.3.4' AND address = 2;")

if __name__ == '__main__':
    unittest.main()
