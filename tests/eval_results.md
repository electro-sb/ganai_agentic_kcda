Using evaluation criteria: criteria={'tool_trajectory_avg_score': 1.0} user_simulator_config=None
*********************************************************************
Eval Run Summary
routing_test_set:
  Tests passed: 4
  Tests failed: 0
********************************************************************
Eval Set Id: routing_test_set
Eval Id: case_search_01
Overall Eval Status: PASSED
---------------------------------------------------------------------
Metric: tool_trajectory_avg_score, Status: PASSED, Score: 1.0, Threshold: 1.0
---------------------------------------------------------------------
Invocation Details:
+----+---------------------------+---------------------+---------------------------+------------------------+---------------------------+-----------------------------+
|    | prompt                    | expected_response   | actual_response           | expected_tool_calls    | actual_tool_calls         | tool_trajectory_avg_score   |
+====+===========================+=====================+===========================+========================+===========================+=============================+
|  0 | Who won the cricket match | MATCH_SEARCH        | I found a match. Is there | id=None args={'query': | id='adk-1a0e92aa-600a-432 | Status: PASSED, Score:      |
|    | yesterday?                |                     | a specific match you are  | 'Who won the cricket   | a-8257- e0fd4814a57f'     | 1.0                         |
|    |                           |                     | looking for?              | match yesterday?'}     | args={'query': 'Who won   |                             |
|    |                           |                     |                           | name='call_web_search' | the cricket match         |                             |
|    |                           |                     |                           |                        | yesterday?'}              |                             |
|    |                           |                     |                           |                        | name='call_web_search'    |                             |
+----+---------------------------+---------------------+---------------------------+------------------------+---------------------------+-----------------------------+



********************************************************************
Eval Set Id: routing_test_set
Eval Id: case_mardi_01
Overall Eval Status: PASSED
---------------------------------------------------------------------
Metric: tool_trajectory_avg_score, Status: PASSED, Score: 1.0, Threshold: 1.0
---------------------------------------------------------------------
Invocation Details:
+----+---------------------------+---------------------+---------------------------+------------------------+---------------------------+-----------------------------+
|    | prompt                    | expected_response   | actual_response           | expected_tool_calls    | actual_tool_calls         | tool_trajectory_avg_score   |
+====+===========================+=====================+===========================+========================+===========================+=============================+
|  0 | Find the MaRDI dataset ID | MATCH_MARDI         | A MaRDI dataset was found | id=None args={'query': | id='adk-1105ddd6-b245-42f | Status: PASSED, Score:      |
|    | for thermodynamics        |                     | for thermodynamics.       | 'MaRDI dataset ID for  | b- bac2-26b0b15e8044'     | 1.0                         |
|    |                           |                     | However, the specific     | thermodynamics'}       | args={'query': 'MaRDI     |                             |
|    |                           |                     | dataset ID is not         | name='call_mardi'      | dataset ID for            |                             |
|    |                           |                     | available.                |                        | thermodynamics'}          |                             |
|    |                           |                     |                           |                        | name='call_mardi'         |                             |
+----+---------------------------+---------------------+---------------------------+------------------------+---------------------------+-----------------------------+



********************************************************************
Eval Set Id: routing_test_set
Eval Id: case_wolfram_01
Overall Eval Status: PASSED
---------------------------------------------------------------------
Metric: tool_trajectory_avg_score, Status: PASSED, Score: 1.0, Threshold: 1.0
---------------------------------------------------------------------
Invocation Details:
+----+--------------------------+---------------------+-------------------------+---------------------------+---------------------------+-----------------------------+
|    | prompt                   | expected_response   | actual_response         | expected_tool_calls       | actual_tool_calls         | tool_trajectory_avg_score   |
+====+==========================+=====================+=========================+===========================+===========================+=============================+
|  0 | Calculate the derivative | MATCH_WOLFRAM       | The derivative of x^3 + | id=None args={'query':    | id='adk-1a3287d0-419d-406 | Status: PASSED, Score:      |
|    | of x^3 + 5x              |                     | 5x is 3x^2 + 5.         | 'derivative of x^3 + 5x'} | 7-ac49- ac0336352a09'     | 1.0                         |
|    |                          |                     |                         | name='call_wolfram'       | args={'query':            |                             |
|    |                          |                     |                         |                           | 'derivative of x^3 + 5x'} |                             |
|    |                          |                     |                         |                           | name='call_wolfram'       |                             |
+----+--------------------------+---------------------+-------------------------+---------------------------+---------------------------+-----------------------------+



********************************************************************
Eval Set Id: routing_test_set
Eval Id: case_calc_01
Overall Eval Status: PASSED
---------------------------------------------------------------------
Metric: tool_trajectory_avg_score, Status: PASSED, Score: 1.0, Threshold: 1.0
---------------------------------------------------------------------
Invocation Details:
+----+------------------+---------------------+-------------------+------------------------+---------------------------+-----------------------------+
|    | prompt           | expected_response   | actual_response   | expected_tool_calls    | actual_tool_calls         | tool_trajectory_avg_score   |
+====+==================+=====================+===================+========================+===========================+=============================+
|  0 | What is 25 + 25? | MATCH_CALC          | 25 + 25 = 50.     | id=None args={'query': | id='adk-d7805400-a102-413 | Status: PASSED, Score:      |
|    |                  |                     |                   | '25 + 25'}             | 0-94b8- a81111df0f9d'     | 1.0                         |
|    |                  |                     |                   | name='call_calculator' | args={'query': '25 + 25'} |                             |
|    |                  |                     |                   |                        | name='call_calculator'    |                             |
+----+------------------+---------------------+-------------------+------------------------+---------------------------+-----------------------------+



