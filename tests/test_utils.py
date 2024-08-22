# def test_inherit_logger():
#     # Define a dummy function for testing
#     @inherit_logger
#     def dummy_function():
#         pass

#     # Call the dummy function
#     dummy_function()

#     # Assert that the child logger has inherited the core from the parent logger
#     assert dummy_function.__wrapped__._core is parent_logger._core
