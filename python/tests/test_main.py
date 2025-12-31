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
        # position=5. minute_timer = 10-5 = 5. hour_timer = 0. control_status = 1
        mock_cursor.execute.assert_any_call("UPDATE control_motor SET hour_timer = '0', minute_timer = '5', control_status = '1' WHERE ip = '1.2.3.4' AND address = 2;")

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
        # position=15. minute_timer = 0. hour_timer = 60 - 15 = 45. control_status = 0
        mock_cursor.execute.assert_any_call("UPDATE control_motor SET hour_timer = '45', minute_timer = '0', control_status = '0' WHERE ip = '1.2.3.4' AND address = 2;")

    @patch('main.get_db_connection')
    @patch('main.requests')
    @patch('main.time')
    def test_run_motor_control_staggered(self, mock_time, mock_requests, mock_get_db):
        """Test Motor control: Staggered start times based on line priority"""
        # Mock DB
        mock_cursor = MagicMock()
        mock_get_db.return_value = MagicMock(cursor=MagicMock(return_value=mock_cursor))

        # Mock 5 rows: ip, address, line, ..., hour_cycle, minute_cycle, ...
        # Columns: 1=ip, 2=address, 3=line, 6=hour_cycle (1), 7=minute_cycle (10)
        # Ranks after sorting by line:
        # 0: Line 10 (IP 1.1.1.2) -> Offset 0. Active [0, 10)
        # 1: Line 20 (IP 1.1.1.3) -> Offset 0. Active [0, 10)
        # 2: Line 30 (IP 1.1.1.4) -> Offset 0. Active [0, 10)
        # 3: Line 40 (IP 1.1.1.5) -> Offset 0. Active [0, 10)
        # 4: Line 50 (IP 1.1.1.1) -> Offset 10. Active [10, 20)
        
        row1 = (None, '1.1.1.1', '1', 50, 0, 0, 1, 10, 0, 0, 0)
        row2 = (None, '1.1.1.2', '1', 10, 0, 0, 1, 10, 0, 0, 0)
        row3 = (None, '1.1.1.3', '1', 20, 0, 0, 1, 10, 0, 0, 0)
        row4 = (None, '1.1.1.4', '1', 30, 0, 0, 1, 10, 0, 0, 0)
        row5 = (None, '1.1.1.5', '1', 40, 0, 0, 1, 10, 0, 0, 0)
        
        mock_cursor.fetchall.return_value = [row1, row2, row3, row4, row5]

        # --- Sub-test 1: T=5 (00:05). Active window for Rank 0-3 ---
        mock_time.localtime.return_value = time.struct_time((2025, 12, 30, 0, 5, 0, 1, 364, 0))
        mock_time.strftime.return_value = "2025-12-30 00:05:00"

        # Execute
        main.run_motor_control()

        # Helper to check assert calls
        def check_status(ip, status, message_suffix=""):
             found = False
             for call_args in mock_cursor.execute.call_args_list:
                 sql = call_args[0][0]
                 if ip in sql and f"control_status = '{status}'" in sql:
                     found = True
                     break
             self.assertTrue(found, f"Expected IP {ip} to have status {status} {message_suffix}")

        check_status('1.1.1.2', 1, "at T=5") # Rank 0
        check_status('1.1.1.3', 1, "at T=5") # Rank 1
        check_status('1.1.1.4', 1, "at T=5") # Rank 2
        check_status('1.1.1.5', 1, "at T=5") # Rank 3
        check_status('1.1.1.1', 0, "at T=5 (should wait)") # Rank 4 (Wait)
        
        # Reset mocks for next sub-test
        mock_cursor.reset_mock()
        mock_requests.reset_mock()

        # --- Sub-test 2: T=15 (00:15). Active window for Rank 4 ---
        mock_time.localtime.return_value = time.struct_time((2025, 12, 30, 0, 15, 0, 1, 364, 0))
        mock_time.strftime.return_value = "2025-12-30 00:15:00"
        
        # We need to set fetchall again because reset_mock might have cleared it or it's a new call
        mock_cursor.fetchall.return_value = [row1, row2, row3, row4, row5]

        # Execute
        main.run_motor_control()

        check_status('1.1.1.2', 0, "at T=15 (finished)") # Rank 0
        check_status('1.1.1.3', 0, "at T=15 (finished)") # Rank 1
        check_status('1.1.1.4', 0, "at T=15 (finished)") # Rank 2
        check_status('1.1.1.5', 0, "at T=15 (finished)") # Rank 3
        check_status('1.1.1.1', 1, "at T=15 (should run)") # Rank 4 (Active now)

if __name__ == '__main__':
    unittest.main()
